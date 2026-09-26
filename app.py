"""Kavach production entrypoint: guardian API + real MCP + family board.

  GET  /healthz   liveness        GET  /readyz    readiness (DB + MCP manager)
  GET  /version   build + mode    GET  /metrics   operational counters
  POST /api/chat  senior/family conversation (rate-limited)
  GET  /api/family-feed          incidents + routines + check-ins + alerts
  POST /mcp , /mcp/              real MCP, Streamable HTTP, spec 2025-11-25
  GET  /apps/family-board.html   MCP App UI (also served as ui:// resource)
  GET  /ui , /                   lightweight fallback console
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from time import monotonic

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from mcp.server.fastmcp.server import StreamableHTTPASGIApp
from pydantic import BaseModel, Field
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse as StarletteJSON
from starlette.routing import Route

import mobile_api
from agent import config as cfg
from agent import models
from agent.kavach_agent import run_agent_turn
from agent.ratelimit import limiter
from mcp_server.server import UI_URI, mcp

APP_ENV = cfg.APP_ENV
IS_PROD = cfg.IS_PROD


class _RequestIdFilter(logging.Filter):
    """Guarantee %(request_id)s exists on every record.

    Without this, ANY third-party log (uvicorn, httpx, mcp) emitted
    without extra={"request_id": ...} raises KeyError during formatting
    and can take down request handling. Production crash bug.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"  # type: ignore[attr-defined]
        return True


logging.basicConfig(level=getattr(logging, cfg.LOG_LEVEL.upper(), logging.INFO),
                    format="%(asctime)s %(levelname)s %(name)s rid=%(request_id)s %(message)s")
for _h in logging.root.handlers:
    _h.addFilter(_RequestIdFilter())
_base_logger = logging.getLogger("kavach")


def _log(**fields: object) -> None:
    _base_logger.info(" ".join(f"{k}={v}" for k, v in fields.items()),
                      extra={"request_id": fields.get("rid", "-")})


START_TIME = time.time()
METRICS_LOCK = threading.Lock()
METRICS: dict[str, int] = {
    "requests_total": 0, "chat_total": 0, "chat_errors": 0,
    "chat_latency_ms_sum": 0, "mcp_total": 0, "rate_limited": 0,
}
MCP_RUNNING = {"ok": False}


@asynccontextmanager
async def lifespan(_: FastAPI):
    _log(event="startup", mode=cfg.llm_status()["mode"], origins=cfg.ALLOWED_ORIGINS)
    if "*" in cfg.ALLOWED_ORIGINS:
        _base_logger.warning("CORS allows all origins — set ALLOWED_ORIGINS in production",
                             extra={"request_id": "-"})
    if not os.getenv("RC_WEBHOOK_AUTH", ""):
        _base_logger.warning("RC_WEBHOOK_AUTH unset — webhook runs in TEST MODE",
                             extra={"request_id": "-"})
    if IS_PROD and cfg.DB_PATH.endswith("kavach.db") and "/data/" not in cfg.DB_PATH:
        _base_logger.warning("SQLite DB is on ephemeral disk — mount a volume in production",
                             extra={"request_id": "-"})
    async with mcp.session_manager.run():
        MCP_RUNNING["ok"] = True
        _log(event="mcp_ready")
        yield
    MCP_RUNNING["ok"] = False
    _log(event="shutdown")


#: Reject bodies larger than any legitimate call: biggest blob is a 200KB
#: base64 ciphertext + JSON envelope. 1MB cap stops memory-exhaustion DoS
#: before JSON parsing. Tune via MAX_BODY_BYTES.
MAX_BODY_BYTES = int(os.getenv("MAX_BODY_BYTES", str(1024 * 1024)))

_docs_url = None if IS_PROD else "/docs"
app = FastAPI(title="Kavach — voice guardian for seniors", version=cfg.APP_VERSION,
              lifespan=lifespan, docs_url=_docs_url, redoc_url=None,
              openapi_url=None if IS_PROD else "/openapi.json")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.include_router(mobile_api.router)


@app.exception_handler(RateLimitExceeded)
async def _ratelimit_handler(request: Request, exc: RateLimitExceeded):
    with METRICS_LOCK:
        METRICS["rate_limited"] += 1
    rid = getattr(request.state, "rid", "-")
    retry_after = getattr(exc, "retry_after", None)
    headers = {"Retry-After": str(retry_after)} if retry_after else {}
    return StarletteJSON({"ok": False, "error": "rate_limited",
                          "detail": "Too many requests, slow down and retry.",
                          "request_id": rid}, status_code=429, headers=headers)


@app.exception_handler(404)
async def _not_found_handler(request: Request, exc: Exception):
    rid = getattr(request.state, "rid", "-")
    return StarletteJSON({"ok": False, "error": "not_found",
                          "detail": "No such endpoint.",
                          "request_id": rid}, status_code=404)


@app.exception_handler(RequestValidationError)
async def _validation_handler(request: Request, exc: RequestValidationError):
    """Uniform envelope for schema errors; keeps FastAPI's 422 status."""
    rid = getattr(request.state, "rid", "-")
    return StarletteJSON({"ok": False, "error": "validation_error",
                          "detail": exc.errors(),
                          "request_id": rid}, status_code=422)


@app.exception_handler(Exception)
async def _catch_all(request: Request, exc: Exception):
    import traceback as _tb
    rid = getattr(request.state, "rid", "-")
    _base_logger.error("unhandled path=%s rid=%s\n%s", request.url.path, rid,
                       _tb.format_exc(limit=5), extra={"request_id": rid})
    if request.url.path.startswith(("/api/chat", "/api/demo", "/api/family")):
        with METRICS_LOCK:
            METRICS["chat_errors"] += 1
    if request.url.path.startswith(("/mcp", "/mcp/")):
        # Streamable-HTTP framing: a bare {"ok":false} envelope breaks MCP
        # clients. Return a JSON-RPC error object instead.
        return StarletteJSON({"jsonrpc": "2.0", "id": None,
                              "error": {"code": -32603,
                                        "message": "Internal error",
                                        "data": {"request_id": rid}}},
                             status_code=500,
                             headers=_security_headers(request, https_only=False))
    return StarletteJSON({"ok": False, "error": "internal",
                          "detail": "Internal error. Retry with this request_id.",
                          "request_id": rid}, status_code=500,
                         headers=_security_headers(request, https_only=False))


def _security_headers(request: Request, https_only: bool = True) -> dict[str, str]:
    """Security headers for responses built outside _request_context
    (413/429/500 paths skip the middleware's post-call injection)."""
    if https_only:
        return {}
    headers = {
        "x-request-id": getattr(request.state, "rid", "-"),
        "x-content-type-options": "nosniff",
        "referrer-policy": "no-referrer",
        "x-frame-options": "DENY",
        "permissions-policy": "geolocation=(), camera=(), microphone=()",
    }
    if request.url.path.startswith("/api/"):
        headers["cache-control"] = "no-store"
        headers["content-security-policy"] = "default-src 'none'; frame-ancestors 'none'"
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    if proto == "https":
        headers["strict-transport-security"] = "max-age=31536000; includeSubDomains"
    return headers


@app.middleware("http")
async def _request_context(request: Request, call_next):
    rid = request.headers.get("x-request-id", uuid.uuid4().hex[:12])
    request.state.rid = rid
    t0 = monotonic()  # durations use the monotonic clock (NTP-safe)
    # Early body-size gate: Content-Length is client-declared, so this is a
    # cheap pre-check only; the ASGI server should also enforce a limit.
    try:
        clen = int(request.headers.get("content-length", "0") or 0)
    except ValueError:
        clen = 0
    if clen > MAX_BODY_BYTES:
        return StarletteJSON({"ok": False, "error": "payload_too_large",
                              "detail": f"Body exceeds {MAX_BODY_BYTES} bytes.",
                              "request_id": rid}, status_code=413)
    with METRICS_LOCK:
        METRICS["requests_total"] += 1
        if request.url.path in ("/mcp", "/mcp/"):
            METRICS["mcp_total"] += 1
    try:
        response = await call_next(request)
    except Exception:
        _log(event="middleware_error", rid=rid, path=request.url.path)
        raise
    latency = int((monotonic() - t0) * 1000)
    response.headers["x-request-id"] = rid
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["referrer-policy"] = "no-referrer"
    response.headers["x-frame-options"] = "DENY"
    response.headers["permissions-policy"] = "geolocation=(), camera=(), microphone=()"
    if request.url.path.startswith("/api/"):
        response.headers["cache-control"] = "no-store"
        response.headers["content-security-policy"] = "default-src 'none'; frame-ancestors 'none'"
    # HSTS only over HTTPS (direct or via trusted proxy header). Never send
    # on plain HTTP — a wrong HSTS can brick local dev in browsers.
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    if proto == "https":
        response.headers["strict-transport-security"] = (
            "max-age=31536000; includeSubDomains")
    _log(event="request", rid=rid, method=request.method,
         path=request.url.path, status=response.status_code, latency_ms=latency)
    return response


_TRUSTED_HOSTS = [h.strip() for h in os.getenv("TRUSTED_HOSTS", "*").split(",") if h.strip()]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=_TRUSTED_HOSTS or ["*"])

origins = ["*"] if "*" in cfg.ALLOWED_ORIGINS else cfg.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)

# Real MCP over Streamable HTTP at /mcp AND /mcp/ (spec 2025-11-25).
_mcp_init_app = mcp.streamable_http_app()  # creates mcp.session_manager
del _mcp_init_app

_mcp_asgi = StreamableHTTPASGIApp(mcp.session_manager)
app.router.routes.append(Route("/mcp", endpoint=_mcp_asgi, methods=["GET", "POST", "DELETE"]))
app.router.routes.append(Route("/mcp/", endpoint=_mcp_asgi, methods=["GET", "POST", "DELETE"]))


class ChatIn(BaseModel):
    text: str = Field(min_length=1, max_length=8000)
    session_id: str = Field(default="default", max_length=64, pattern=r"^[\w\-.]{1,64}$")
    senior_id: str = Field(default="demo-senior", max_length=64, pattern=r"^[\w\-.]{1,64}$")


@app.get("/healthz")
def healthz():
    return {"ok": True, "service": cfg.APP_NAME, "version": cfg.APP_VERSION,
            "mcp": "/mcp", "spec": cfg.MCP_SPEC_VERSION, "time": time.time()}


@app.get("/version")
def version():
    return {"service": cfg.APP_NAME, "version": cfg.APP_VERSION,
            "mcp_spec": cfg.MCP_SPEC_VERSION, "mcp_app": UI_URI,
            "llm": cfg.llm_status(),
            "endpoints": ["/healthz", "/readyz", "/version", "/metrics",
                          "/api/chat", "/api/family-feed", "/api/demo/attack",
                          "/api/family/block-case", "/api/nextgen/proof",
                          "/api/v1/* (mobile contract)",
                          "/mcp", "/mcp/", "/apps/family-board.html", "/ui"]}


@app.get("/readyz")
def readyz():
    checks: dict[str, object] = {"mcp_session_manager": MCP_RUNNING["ok"]}
    try:
        # Non-destructive probe: plain SELECT, never creates tables or rows.
        # (Plain connect may create a 0-byte file on first boot — no schema writes.)
        conn = sqlite3.connect(cfg.DB_PATH, timeout=5)
        try:
            conn.execute("SELECT 1")
        finally:
            conn.close()
        # Writable check without schema side-effects: temp file in DB dir.
        probe = Path(cfg.DB_PATH).parent / f".ready-{os.getpid()}"
        try:
            probe.touch()
            probe.unlink(missing_ok=True)
        except OSError as e:
            raise OSError(f"db_dir_not_writable: {e}") from e
        checks["db_writable"] = True
    except Exception as e:  # noqa: BLE001 - readiness probe must report, not raise
        checks["db_writable"] = False
        checks["db_error"] = str(e)[:200]
    board = os.path.join(os.path.dirname(__file__), "mcp_server", "ui", "family_board.html")
    checks["mcp_app_board"] = os.path.exists(board)
    ready = bool(checks["mcp_session_manager"] and checks["db_writable"]
                 and checks["mcp_app_board"])
    return JSONResponse({"ready": ready, "checks": checks},
                        status_code=200 if ready else 503)


@app.get("/metrics")
def metrics():
    from agent import mobile as _mobile
    with METRICS_LOCK:
        snap = dict(METRICS)
    chats = snap["chat_total"]
    avg = int(snap["chat_latency_ms_sum"] / chats) if chats else 0
    try:
        db_bytes = Path(cfg.DB_PATH).stat().st_size
    except OSError:
        db_bytes = -1
    return {"uptime_s": int(time.time() - START_TIME), "avg_chat_latency_ms": avg,
            **snap, "relay": _mobile.relay_stats(),
            "db_bytes": db_bytes, "env": APP_ENV}


def _feed(senior_id: str) -> dict:
    models.ensure_seed(senior_id)
    senior = models.get_senior(senior_id) or {}
    incidents = models.list_incidents(senior_id, 20)
    for i in incidents:
        try:
            i["red_flags"] = json.loads(i["red_flags"])
        except (json.JSONDecodeError, TypeError):
            i["red_flags"] = []
    return {"senior": {"id": senior.get("id"), "name": senior.get("name"),
                       "language": senior.get("language")},
            "incidents": incidents,
            "routines": models.list_routines(senior_id),
            "checkins": models.list_checkins(senior_id, 10),
            "alerts": [{k: a[k] for k in ("id", "kind", "title", "status", "created", "sent_at")
                        if k in a} for a in models.list_alerts(senior_id, 20)],
            "contacts": [{"label": c["label"], "kind": c["kind"]}
                         for c in models.list_contacts(senior_id)]}


@app.get("/api/family-feed")
def family_feed(senior_id: str = "demo-senior", request: Request = None):  # type: ignore[assignment]
    import re as _re
    if not senior_id or len(senior_id) > 64 or not _re.match(r"^[\w\-.]{1,64}$", senior_id):
        rid = getattr(request.state, "rid", "-") if request is not None else "-"
        return JSONResponse({"ok": False, "error": "invalid_id",
                             "detail": "senior_id must match ^[\\w\\-.]{1,64}$.",
                             "request_id": rid}, status_code=422)
    return JSONResponse(_feed(senior_id))


class DemoAttackIn(BaseModel):
    senior_id: str = Field(default="demo-senior", max_length=64, pattern=r"^[\w\-.]{1,64}$")
    scenario: str = Field(default="bank_otp", max_length=32, pattern=r"^[a-z0-9_]{1,32}$")


PAUSE_CARDS = {
    "en": ("Pause. Do not pay. Do not share codes. Verify through a contact you find yourself. "
           "Say: I will verify independently using an official channel. End the call if unsafe. "
           "Kavach is safety information, not legal advice."),
    "hi": ("रुकें। पैसे न भेजें। OTP/कोड साझा न करें। खुद खोजे गए आधिकारिक संपर्क से सत्यापित करें। "
           "कहें: मैं आधिकारिक चैनल से स्वतंत्र रूप से सत्यापित करूंगा। असुरक्षित लगे तो कॉल काट दें। "
           "कवच सामान्य सुरक्षा जानकारी है, कानूनी सलाह नहीं।"),
    "hinglish": ("Ruko. Paise mat bhejo. OTP/code share mat karo. Khud dhoondhe gaye official contact se verify karo. "
                 "Bolo: main independently verify karunga. Unsafe lage to call kaat do. "
                 "Kavach safety information hai, legal advice nahi."),
}


@app.get("/api/pause-card")
def pause_card(lang: str = "en"):
    lang = lang[:8].lower()
    key = "hinglish" if "hing" in lang else "hi" if lang.startswith("hi") else "en"
    return JSONResponse({"lang": key, "card": PAUSE_CARDS[key], "offline": True,
                         "disclaimer": "General safety information, not legal advice."})


@app.get("/api/directory/lookup")
def directory_lookup(q: str = "", jurisdiction: str = "IN", lang: str = "en"):
    entries = _load_directory()
    ql = q[:120].lower()
    out = [e for e in entries
           if (not ql or ql in (e.get("institution", "") + e.get("category", "")).lower())]
    if jurisdiction and jurisdiction.upper() != "ALL":
        out = [e for e in out
               if e.get("jurisdiction", "IN").upper() == jurisdiction[:8].upper()]
    if lang[:2].lower() in ("hi", "en"):
        pref = [e for e in out if e.get("language") == lang[:2].lower()]
        if pref:
            out = pref
    # Copy before annotating: _load_directory() is cached, never mutate it.
    # count = total matches (not page length) so clients can paginate honestly.
    annotated = [dict(e, caller_authenticated=False,
                      note="Directory does not authenticate the caller. "
                           "Caller ID can be spoofed.") for e in out]
    return JSONResponse({"entries": annotated[:25], "count": len(annotated)})


@lru_cache(maxsize=1)
def _load_directory() -> list[dict]:
    """Curated directory, parsed once per process (mmap-free, ~KBs)."""
    path = Path(__file__).parent / "data" / "official_directory.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return []


DEMO_SCENARIOS = {
    "bank_otp": ("call", "HDFC bank officer",
                 ("Senior: phone call. Caller: HDFC bank officer. Asked: share OTP to unfreeze account. "
                  "Pressure: yes, police complaint today itself.")),
    "digital_arrest": ("call", "CBI cyber cell",
                       ("Senior: phone call. Caller: CBI cyber cell. "
                        "Asked: stay on video call, transfer to safe account. "
                        "Pressure: yes, arrest immediately, do not hang up.")),
    "power_apk": ("message", "electricity department",
                  ("Senior: SMS with APK link. Caller: electricity department. Asked: download APK to update KYC. "
                   "Pressure: power cut tonight.")),
}


@app.post("/api/demo/attack")
@limiter.limit(f"{cfg.RATE_LIMIT_PER_MIN}/minute")
def demo_attack(body: DemoAttackIn, request: Request):
    from agent import redflags as _rf
    _ = request
    models.ensure_seed(body.senior_id)
    channel, claim, transcript = DEMO_SCENARIOS.get(body.scenario, DEMO_SCENARIOS["bank_otp"])
    signals = _rf.extract_signals(transcript)
    contact = models.find_contact(body.senior_id, claim)
    verdict, conf, reasons = _rf.score_verdict(signals, transcript, known_contact=bool(contact))
    iid = models.create_incident(body.senior_id, channel, claim, transcript,
                                 signals, verdict, conf)
    draft = models.draft_alert(body.senior_id, "family_note",
                               "Kavach live-attack: possible scam",
                               f"Case #{iid}: {verdict} — {claim}. {'; '.join(reasons[:3])}",
                               iid)
    return JSONResponse({"ok": True, "test_mode": True, "incident_id": iid,
                         "verdict": verdict, "confidence": conf, "reasons": reasons,
                         "alert_id": draft["id"], "confirm_code": draft["confirm_code"]})


class ChallengeIn(BaseModel):
    senior_id: str = Field(default="demo-senior", max_length=64, pattern=r"^[\w\-.]{1,64}$")
    claim_who: str = Field(default="", max_length=200)
    question: str = Field(default="Did you call and ask for money?", max_length=500)


class BlockCaseIn(BaseModel):
    senior_id: str = Field(default="demo-senior", max_length=64, pattern=r"^[\w\-.]{1,64}$")
    incident_id: int = Field(gt=0)
    label: str = Field(default="war-room block", max_length=120)


class ChallengeRespondIn(BaseModel):
    decision: str = Field(pattern=r"^(APPROVE|DENY|NEED_HELP|approve|deny|need_help)$")


@app.post("/api/family/challenge/create")
@limiter.limit(f"{cfg.RATE_LIMIT_PER_MIN}/minute")
def challenge_create(body: ChallengeIn, request: Request):
    _ = request
    models.ensure_seed(body.senior_id)
    ch = models.create_challenge(body.senior_id, body.claim_who, body.question)
    return JSONResponse({"ok": True, **ch,
                         "copy": "This confirms a response from an enrolled family device. "
                                 "It does not prove the caller is genuine. If unsure, end the call "
                                 "and contact family using a saved number."})


@app.get("/api/family/challenge/{challenge_id}")
def challenge_get(challenge_id: str):
    ch = models.get_challenge(challenge_id[:64])
    if not ch:
        return JSONResponse({"ok": False, "error": "not_found"}, status_code=404)
    return JSONResponse({"ok": True, "challenge": {k: ch[k] for k in
                         ("id", "senior_id", "claim_who", "question", "state",
                          "decision", "created", "expires")}})


@app.post("/api/family/challenge/{challenge_id}/respond")
@limiter.limit(f"{cfg.RATE_LIMIT_PER_MIN}/minute")
def challenge_respond(challenge_id: str, body: ChallengeRespondIn, request: Request):
    _ = request
    out = models.respond_challenge(challenge_id[:64], body.decision)
    if not out:
        return JSONResponse({"ok": False, "error": "bad_state_or_expired"}, status_code=410)
    wording = {"APPROVE": "Enrolled device confirmed. This does not authenticate the caller. "
                          "Call back using your saved number before acting.",
               "DENY": "Enrolled device says they did not make this request. End the call and "
                       "contact them using your saved number.",
               "NEED_HELP": "Your family member requested help. Contact another trusted person."}
    return JSONResponse({"ok": True, "state": out["state"], "decision": out["decision"],
                         "wording": wording.get(out["decision"], "")})


@app.post("/api/family/block-case")
@limiter.limit(f"{cfg.RATE_LIMIT_PER_MIN}/minute")
def block_case(body: BlockCaseIn, request: Request):
    """War-room Block: real household block + community report, from a case file.

    The web war-room has no raw phone number (vault shows masked claims), so the
    sender-hash is derived deterministically from the case's caller claim. The
    same lure blocked by 3 independent households enters the community feed.
    Raw numbers never exist here — hashes only.
    """
    from agent import mobile as _mobile
    _ = request
    models.ensure_seed(body.senior_id)
    inc = models.get_incident(body.incident_id)
    if not inc or inc["senior_id"] != body.senior_id:
        return JSONResponse({"ok": False, "error": "not_found"}, status_code=404)
    household_id = f"web|{body.senior_id}"
    claim = (inc.get("caller_claim") or "") + "|" + (inc.get("channel") or "")
    number_hash = _mobile.hash_number(household_id, claim.strip() or f"case-{inc['id']}")
    ok = _mobile.block_number(household_id, number_hash, body.label[:120], "block")
    feed_hit = any(f["number_hash"] == number_hash for f in _mobile.threat_feed())
    return JSONResponse({"ok": ok, "number_hash": number_hash,
                         "household_id": household_id,
                         "community": feed_hit,
                         "summary": ("Blocked sender-hash for household. Sibling devices sync it "
                                     "via GET /api/v1/screen/list; all households gain it at "
                                     "3 independent reports.")})


@app.post("/api/chat")
@limiter.limit(f"{cfg.RATE_LIMIT_PER_MIN}/minute")
def chat(body: ChatIn, request: Request):
    text = body.text[: cfg.MAX_INPUT_CHARS]
    rid = getattr(request.state, "rid", uuid.uuid4().hex[:12])
    t0 = monotonic()  # monotonic: NTP steps must not skew latency metrics
    try:
        out = run_agent_turn(text, body.session_id or "default",
                             body.senior_id or "demo-senior")
    except Exception:  # noqa: BLE001 - chat must never 500 on demo day
        import traceback as _tb
        _base_logger.error("chat_error rid=%s\n%s", rid, _tb.format_exc(limit=5),
                           extra={"request_id": rid})
        # Generic client text: never echo internals (DB paths, SQL) outward.
        out = {"spoken": "Something hiccuped on my side — but everything you said is saved. "
                         "Please try once more.",
               "text": f"error id {rid}", "cards": [], "tools": [], "provider": "error"}
        with METRICS_LOCK:
            METRICS["chat_errors"] += 1
    latency = int((monotonic() - t0) * 1000)
    with METRICS_LOCK:
        METRICS["chat_total"] += 1
        METRICS["chat_latency_ms_sum"] += latency
    out["request_id"] = rid
    out["latency_ms"] = latency
    return JSONResponse(out)


@app.get("/apps/family-board.html")
def board_html(senior_id: str = "demo-senior"):
    path = os.path.join(os.path.dirname(__file__), "mcp_server", "ui", "family_board.html")
    return FileResponse(path, media_type="text/html")


@app.get("/funnel.html")
def funnel_html():
    path = os.path.join(os.path.dirname(__file__), "simulator", "web", "public", "funnel.html")
    if os.path.exists(path):
        return FileResponse(path, media_type="text/html")
    return HTMLResponse("<h1>Funnel not found</h1>", status_code=404)


@app.get("/api/nextgen/proof")
def nextgen_proof():
    """One-JSON Next Gen proof: RevenueCat integration, demo contract, assets.

    Judges verify thoughtful RevenueCat use + repo/video readiness without a
    store release. All file checks are best-effort (missing file = false)."""
    import agent.rulepack as _rp
    base = os.path.dirname(__file__)
    assets = os.path.join(base, "assets")
    sub = os.path.join(base, "docs", "SUBMISSION_NEXTGEN.md")
    return JSONResponse({
        "track": "Next Gen",
        "test_mode": True,
        "revenuecat": {
            "sdk": "purchases:10.23.2 (PaywallActivity.kt)",
            "entitlements": ["sheild_protection", "shield_protection", "family_fortress",
                             "pro_caregiver", "pro", "family_pro_shield"],
            "judge_promo": "SHIPATON-JUDGE",
            "server_authority": "POST /api/v1/billing/webhook "
                                "(Bearer + idempotent receipts + downgrade)",
            "sandbox_reconcile": "POST /api/v1/household/tier",
            "tiers": {"free": 20, "pro": 200, "ultra": 2000},
            "never_paywalled": ["urgent actions", "consent screens",
                                "revoke/kill-switch", "export"],
        },
        "demo_contract": {
            "attack": "POST /api/demo/attack {bank_otp|digital_arrest|power_apk}",
            "block_case": "POST /api/family/block-case {senior_id, incident_id}",
            "household_sync": "GET /api/v1/screen/list?household_id=",
            "community": "GET /api/v1/threat-feed (hashes only, 3-household gate)",
            "rules": "GET /api/v1/rules/pack (Ed25519, test_mode="
                     + str(_rp.is_test_mode()) + ")",
            "apks": ["kavach-senior-apk (.senior)", "kavach-manager-apk (.manager)"],
        },
        "repo": {
            "license_mit": os.path.exists(os.path.join(base, "LICENSE")),
            "submission_pack": os.path.exists(sub),
            "icon_1024": os.path.exists(os.path.join(assets, "icon-1024.png")),
            "screenshot_1179x2556": os.path.exists(
                os.path.join(assets, "screenshot-1179x2556.png")),
            "video_source": os.path.exists(
                os.path.join(assets, "kavach-demo-2min.mp4")),
        },
        "endpoints": ["/healthz", "/readyz", "/version", "/metrics",
                      "/api/chat", "/api/family-feed", "/api/demo/attack",
                      "/api/family/block-case", "/api/v1/*", "/mcp",
                      "/apps/family-board.html", "/funnel.html", "/ui"],
    })



FALLBACK_HTML = """<!doctype html><html lang='en'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<meta name='color-scheme' content='dark light'>
<title>Kavach 🛡️ — voice guardian for seniors</title>
<style>
:root{--bg:#14100b;--bg2:#1e1710;--panel:#fffdf7;--ink:#2b2118;--card:#fff;--line:#e8dcc3;
--muted:#8a7660;--accent:#e26a1b;--accent2:#9a3d0c;--green:#1f7a4d;--red:#c1121f;--gold:#ffd98a;
--r:20px;--sh:0 12px 40px rgba(20,12,4,.28);--font:ui-sans-serif,system-ui,'Segoe UI',Roboto,'Noto Sans','Noto Sans Devanagari',sans-serif}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:var(--font);color:#f5ead2;min-height:100vh;background:radial-gradient(900px 480px at 15% -5%,#4a2c12 0%,transparent 60%),radial-gradient(900px 520px at 90% 0%,#5c1a1a 0%,transparent 55%),linear-gradient(180deg,var(--bg),var(--bg2)) fixed}
a{color:var(--gold)}.wrap{max-width:1060px;margin:0 auto;padding:20px 16px 64px}
.hero{position:relative;overflow:hidden;border-radius:28px;padding:30px 28px 22px;color:#fff8e8;background:linear-gradient(135deg,#241708,#4a2a0e 45%,#7a3a10);border:1px solid rgba(255,217,138,.25);box-shadow:var(--sh)}
.hero::after{content:'🛡️';position:absolute;right:16px;top:0;font-size:150px;opacity:.12;pointer-events:none}
.topline{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.brand{font-size:30px;font-weight:900;display:flex;align-items:center;gap:10px;letter-spacing:.5px}
.mark{width:46px;height:46px;border-radius:14px;display:grid;place-items:center;font-size:26px;background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 6px 18px rgba(226,106,27,.5)}
.tag{font-size:12px;font-weight:800;padding:6px 12px;border-radius:999px;border:1px solid rgba(255,217,138,.35);background:rgba(255,255,255,.08);color:#ffe9bd}
.tag.hot{background:var(--gold);color:#3a2200;border-color:var(--gold)}
.tag.dash{border-style:dashed}
.sub{color:#e9d3a8;margin:10px 0 0;font-size:16px;max-width:68ch;line-height:1.6}
.pills{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px;align-items:center}
.pill-live{display:inline-flex;align-items:center;gap:8px;font-size:12.5px;font-weight:700;background:rgba(0,0,0,.35);border:1px solid rgba(255,217,138,.3);padding:7px 12px;border-radius:999px;color:#ffe9bd}
.dot{width:9px;height:9px;border-radius:50%;background:#ffb020;box-shadow:0 0 10px #ffb020}.dot.on{background:#4ade80;box-shadow:0 0 10px #4ade80}.dot.off{background:#f87171;box-shadow:0 0 10px #f87171}
.grid{display:grid;grid-template-columns:1.15fr .85fr;gap:14px;margin-top:16px}
@media(max-width:860px){.grid{grid-template-columns:1fr}}
.panel{background:var(--panel);color:var(--ink);border-radius:24px;padding:22px;box-shadow:var(--sh)}
.panel h2{margin:0 0 4px;font-size:21px}.hint{color:var(--muted);font-size:14px;margin:0 0 12px;line-height:1.5}
.tabs{display:flex;gap:8px;margin:14px 0;flex-wrap:wrap}
.tab{flex:1;min-width:140px;padding:12px;border-radius:14px;border:2px solid rgba(255,217,138,.2);background:rgba(255,253,247,.06);color:#cbb894;font-weight:800;font-size:15px;cursor:pointer}
.tab.active{border-color:var(--gold);color:#fff3d6;background:rgba(255,217,138,.1)}
.thread{display:grid;gap:10px;max-height:380px;overflow:auto;padding:4px 2px}
.bubble{border-radius:16px;padding:13px 15px;font-size:16px;line-height:1.6;white-space:pre-wrap;word-break:break-word}
.bubble.you{background:#f3ead7;border-left:6px solid var(--accent)}
.bubble.kav{background:#e6f4ec;border:1px solid #a8dfbc}
.bubble.sys{background:#fff4d6;border:1px dashed #d9b45b;font-size:14px}
.verdict{display:inline-block;font-size:12px;font-weight:900;padding:3px 12px;border-radius:999px;margin-bottom:6px}
.v-SCAM{background:#fecaca;color:#7f1d1d}.v-SUSPICIOUS{background:#fde68a;color:#713f12}.v-LIKELY_SAFE{background:#bbf7d0;color:#14532d}.v-UNCERTAIN{background:#bfdbfe;color:#1e3a8a}
.composer{display:flex;gap:10px;margin-top:12px}
.composer textarea{flex:1;font-size:17px;min-height:64px;border:2px solid var(--line);border-radius:14px;padding:12px 14px;font-family:var(--font);resize:vertical}
.composer textarea:focus{outline:4px solid #ffcf7a;border-color:var(--accent)}
.btnrow{display:flex;gap:10px;margin-top:10px;flex-wrap:wrap}
.big{flex:1;min-width:170px;padding:16px;font-size:17px;font-weight:900;border-radius:16px;border:0;cursor:pointer;color:#fff;background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 8px 22px rgba(226,106,27,.4)}
.big.talk{background:linear-gradient(135deg,#2a9d6b,#14532d)}.big:disabled{opacity:.55;cursor:wait}.big.listening{background:var(--red);animation:pl 1.1s infinite}
@keyframes pl{50%{opacity:.6}}
.ghost{background:transparent;border:1.5px solid var(--line);border-radius:999px;padding:9px 15px;font-size:14px;font-weight:700;color:var(--ink);cursor:pointer}
.ghost:hover{border-color:var(--accent)}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.meta{font-size:12.5px;color:var(--muted);display:flex;gap:10px;flex-wrap:wrap;margin-top:10px;align-items:center}
.side{display:grid;gap:14px;align-content:start}
.card{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:18px;padding:16px 18px;box-shadow:0 4px 16px rgba(20,12,4,.12)}
.card h3{margin:0 0 8px;font-size:12px;text-transform:uppercase;letter-spacing:1px;color:var(--muted)}
.card p{margin:6px 0;font-size:15px;line-height:1.6}
.kv{display:flex;justify-content:space-between;gap:8px;font-size:14px;padding:7px 0;border-top:1px dashed var(--line)}
.kv:first-of-type{border-top:0}
.ring{width:74px;height:74px}
.case{border:1px solid var(--line);border-left:8px solid var(--line);border-radius:12px;padding:10px 12px;margin-top:8px;font-size:14px}
.case.SCAM{border-left-color:#f87171}.case.SUSPICIOUS{border-left-color:#fbbf24}.case.LIKELY_SAFE{border-left-color:#34d399}.case.UNCERTAIN{border-left-color:#93c5fd}
input,select{font-size:15px;border:1.5px solid var(--line);border-radius:10px;padding:10px 12px;font-family:var(--font);width:100%}
.toolrow{display:flex;gap:8px;margin-top:8px}.toolrow button{flex:1}
.nav{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
.nav a{font-size:13px;font-weight:700;text-decoration:none;background:rgba(255,255,255,.08);border:1px solid rgba(255,217,138,.35);padding:9px 14px;border-radius:999px}
footer{margin-top:22px;font-size:13px;color:#a68e6c;text-align:center;line-height:1.7}
.typing{display:inline-flex;gap:5px;padding:12px 16px}.typing i{width:8px;height:8px;border-radius:50%;background:#1f7a4d;animation:tp 1s infinite}.typing i:nth-child(2){animation-delay:.15s}.typing i:nth-child(3){animation-delay:.3s}
@keyframes tp{50%{opacity:.3;transform:translateY(-3px)}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
:focus-visible{outline:4px solid var(--gold);outline-offset:2px}
</style></head><body><div class='wrap'>
<header class='hero'><div class='topline'><div class='brand'><span class='mark'>🛡️</span>Kavach</div>
<span class='tag hot'>Next Gen</span><span class='tag dash'>TEST MODE · no charges</span></div>
<p class='sub'><b>Pause pressure. Verify independently. Bring family.</b> — without uploading calls.
A voice guardian for seniors in Hindi, Hinglish &amp; English. Deterministic safety rules on-device, LLM only narrates warmly.</p>
<div class='pills'><span class='pill-live'><span class='dot' id='d1'></span><span id='t1'>checking backend…</span></span>
<span class='pill-live'><span class='dot' id='d2'></span><span id='t2'>…</span></span>
<span class='pill-live' id='t3'>…</span></div>
<nav class='nav'><a href='/apps/family-board.html'>🏠 Family board app</a><a href='/funnel.html'>💛 60-sec risk quiz</a>
<a href='/docs'>📖 API docs</a><a href='/version'>version</a><a href='/metrics'>metrics</a><a href='/readyz'>readyz</a></nav>
</header>
<div class='tabs' role='tablist'><button class='tab active' id='tab-chat' role='tab' aria-selected='true'>💬 Talk to Kavach<small style='display:block;font-weight:500;font-size:12px;opacity:.8'>senior-safe · big type · voice</small></button>
<button class='tab' id='tab-feed' role='tab' aria-selected='false'>🏠 Family feed<small style='display:block;font-weight:500;font-size:12px;opacity:.8'>cases · rhythms · alerts</small></button>
<button class='tab' id='tab-tools' role='tab' aria-selected='false'>🧰 Safety tools<small style='display:block;font-weight:500;font-size:12px;opacity:.8'>pause card · directory · demo</small></button></div>
<div class='grid'><section class='panel' id='pane-chat' role='tabpanel'>
<h2>Namaste 🙏 I am Kavach, your shield</h2><p class='hint'>Worried about a call or message? Type below — or tap <b>🎤 Speak</b>. Slowly, I am listening. Nothing leaves this demo unencrypted.</p>
<div class='thread' id='thread' aria-live='polite'><div class='bubble kav'>🛡️ <b>Ruko. Verify karo.</b><br>Try: “Bank called asking for OTP” — I will check the red flags and tell your family only with your words.</div></div>
<label class='sr' for='q'>Talk to Kavach</label>
<div class='composer'><textarea id='q' rows='2' maxlength='8000' placeholder='Type here… e.g. Someone called about my bank account'>Someone called about my bank account</textarea></div>
<div class='btnrow'><button class='big talk' id='b-voice'>🎤 Speak</button><button class='big' id='b-send'>Send ➤</button></div>
<div class='chips'><button class='ghost' data-q='Bank officer called, share OTP to unfreeze account, police complaint today'>🏦 Bank OTP pressure</button>
<button class='ghost' data-q='CBI cyber cell on video call, transfer to safe account, do not hang up'>🚨 Digital arrest</button>
<button class='ghost' data-q='SMS with APK link from electricity department, power cut tonight'>⚡ Power APK</button>
<button class='ghost' data-q='My grandson called asking for money urgently'>👪 Grandchild voice</button></div>
<div class='meta'><span id='lat'></span><span id='rid'></span><button class='ghost' id='b-hear'>🔊 hear again</button><button class='ghost' id='b-clear'>clear</button></div>
<div id='cards' style='display:grid;gap:10px;margin-top:12px'></div>
</section><div class='side'>
<section class='panel' id='pane-feed' role='tabpanel' hidden><h2>🏠 Household at a glance</h2><p class='hint'>Live from <code>/api/family-feed</code> · OTPs masked · verdicts cite evidence.</p>
<div style='display:flex;gap:12px;align-items:center;margin-bottom:8px'><svg class='ring' viewBox='0 0 72 72' role='img' aria-label='safety score'><circle cx='36' cy='36' r='26' fill='none' stroke='#e3d5bd' stroke-width='9'/><circle id='ring' cx='36' cy='36' r='26' fill='none' stroke='#1f7a4d' stroke-width='9' stroke-linecap='round' stroke-dasharray='163.3' stroke-dashoffset='40' transform='rotate(-90 36 36)'/><text id='ringt' x='36' y='42' text-anchor='middle' font-size='19' font-weight='800' fill='#2b2118'>–</text></svg>
<div><div style='font-weight:900;font-size:17px' id='fh'>…</div><div class='meta' id='fm'></div></div>
<span style='margin-left:auto'></span><button class='ghost' id='b-feed'>↻ refresh</button></div>
<div id='feed'></div></section>
<section class='panel' id='pane-tools' role='tabpanel' hidden><h2>🧰 Safety tools</h2><p class='hint'>Offline-first. General safety information, not legal advice.</p>
<div class='card'><h3>⏸️ Pause card</h3><div class='toolrow'><select id='plang'><option value='en'>English</option><option value='hi'>हिंदी</option><option value='hinglish'>Hinglish</option></select><button class='ghost' id='b-pause'>Show</button></div><p id='pause-out' style='margin-top:10px'></p></div>
<div class='card'><h3>📇 Official directory</h3><input id='dq' placeholder='Search e.g. HDFC, CBI, electricity…' value='bank'><div class='toolrow'><button class='ghost' id='b-dir'>Verify independently</button></div><div id='dir-out'></div></div>
<div class='card'><h3>🔴 Live-attack demo</h3><p>Fire a real lure through the production path. Zero-buzz quarantine on the senior phone.</p><div class='toolrow'><button class='ghost' data-s='bank_otp'>Bank OTP</button><button class='ghost' data-s='digital_arrest'>Digital arrest</button><button class='ghost' data-s='power_apk'>Power APK</button></div><p id='demo-out'></p></div>
<div class='card'><h3>🔐 Family-proof challenge</h3><p>Confirms an <b>enrolled family device</b> — never proves the caller. Caller-ID can be spoofed.</p><input id='cq' placeholder='Who claimed to call? e.g. Beta from Delhi' value='Beta — asked for money'><div class='toolrow'><button class='ghost' id='b-ch'>Create challenge</button></div><p id='ch-out'></p></div>
</section>
<section class='card'><h3>⚡ Backend</h3><div class='kv'><span>Health</span><b id='k-h'>…</b></div><div class='kv'><span>Readiness</span><b id='k-r'>…</b></div><div class='kv'><span>LLM mode</span><b id='k-m'>…</b></div><div class='kv'><span>Avg chat latency</span><b id='k-l'>…</b></div></section>
</div></div>
<footer>Kavach · every verdict cites evidence · family alerts need spoken approval · server holds hashes + noise, never raw numbers.<br>Built for RevenueCat Shipaton 2026 · Next Gen · TEST MODE — no card, no charge · judges: promo <b>SHIPATON-JUDGE</b> · <a href='/docs'>docs</a> · <a href='/apps/family-board.html'>board</a> · <a href='/funnel.html'>quiz</a> · <a href='https://github.com/krishivjoshi219-collab/Kavach'>repo</a> · <a href='https://github.com/krishivjoshi219-collab/Kavach/blob/main/docs/SUBMISSION_NEXTGEN.md'>submission pack</a></footer>
</div><script>
var thread=document.getElementById('thread'),cardsEl=document.getElementById('cards'),lastSpoken='';
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function say(t,cls){var d=document.createElement('div');d.className='bubble '+cls;d.innerHTML=t;thread.appendChild(d);thread.scrollTop=thread.scrollHeight;return d}
function speak(t){try{speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(String(t).slice(0,600));u.lang='en-IN';speechSynthesis.speak(u)}catch(e){}}
function verdictPill(v){if(!v)return '';return \"<span class='verdict v-\"+esc(v)+\"'>\"+esc(String(v).replace(/_/g,' '))+\"</span><br>\"}
async function send(text){var t=(text||document.getElementById('q').value||'').trim();if(!t)return;
say('🧑 '+esc(t),'you');document.getElementById('q').value='';
var tp=document.createElement('div');tp.className='bubble kav';tp.innerHTML=\"<span class='typing'><i></i><i></i><i></i></span> Listening carefully…\";thread.appendChild(tp);
var t0=Date.now();try{var r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t,session_id:'web-'+String(Date.now()%100000),senior_id:'demo-senior'})});
var j=await r.json();tp.remove();lastSpoken=j.spoken||'';
say('🛡️ '+verdictPill(j.verdict)+esc(j.spoken||'(no reply)'),'kav');speak(j.spoken||'');
document.getElementById('lat').textContent=' '+(Date.now()-t0)+'ms · '+(j.provider||'');
document.getElementById('rid').textContent=j.request_id?('id '+j.request_id):'';
cardsEl.innerHTML=(j.cards||[]).map(function(c){return \"<div class='card'><h3>\"+esc(c.title||'card')+\"</h3><p>\"+esc((c.body||'').slice(0,2000))+\"</p></div>\"}).join('')+(j.confirm_code?\"<div class='card' style='text-align:center;font-size:28px;font-weight:900;letter-spacing:8px;background:#241708;color:#ffd98a'>\"+esc(j.confirm_code)+\"</div>\":'');
}catch(e){tp.remove();say('⚠️ Something hiccuped — but everything is saved. Please try once more.','sys')}}
function voiceIn(){var SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR){say('🎤 Voice not supported here — typing works just as well.','sys');return}
try{var rec=new SR();rec.lang='en-IN';var b=document.getElementById('b-voice');b.classList.add('listening');b.textContent='● Listening…';
rec.onresult=function(e){send(e.results[0][0].transcript)};rec.onend=function(){b.classList.remove('listening');b.textContent='🎤 Speak'};rec.onerror=rec.onend;rec.start()}catch(e){}}
async function status(){try{var h=await(await fetch('/healthz')).json();document.getElementById('d1').className='dot on';document.getElementById('t1').textContent='online · '+h.service+' '+h.version;document.getElementById('k-h').textContent='ok · '+h.version}catch(e){document.getElementById('d1').className='dot off';document.getElementById('t1').textContent='offline';document.getElementById('k-h').textContent='offline'}
try{var v=await(await fetch('/version')).json();document.getElementById('t3').textContent='🧠 '+(v.llm?v.llm.mode:'rules')+' · MCP '+v.mcp_spec;document.getElementById('k-m').textContent=(v.llm?v.llm.mode:'?')}catch(e){}
try{var rz=await fetch('/readyz');var rj=await rz.json();document.getElementById('d2').className='dot '+(rj.ready?'on':'off');document.getElementById('t2').textContent=rj.ready?'ready · db + mcp + board':'not ready';document.getElementById('k-r').textContent=rj.ready?'ready':'degraded'}catch(e){}
try{var m=await(await fetch('/metrics')).json();document.getElementById('k-l').textContent=(m.avg_chat_latency_ms||0)+'ms · '+m.chat_total+' chats'}catch(e){}}
function ago(ts){var s=Math.max(1,Math.floor(Date.now()/1000-ts));if(s<60)return s+'s ago';if(s<3600)return Math.floor(s/60)+'m ago';if(s<86400)return Math.floor(s/3600)+'h ago';return Math.floor(s/86400)+'d ago'}
async function feed(){try{var f=await(await fetch('/api/family-feed?senior_id=demo-senior')).json();
var sc=(f.incidents||[]).filter(function(c){return c.verdict==='SCAM'}).length,sf=(f.incidents||[]).filter(function(c){return c.verdict==='LIKELY_SAFE'}).length;
var score=Math.max(40,Math.min(100,72+Math.min(18,sf*3+(f.checkins||[]).length*2)-Math.min(30,sc*2)));
var C=163.3;document.getElementById('ring').style.strokeDashoffset=C-(score/100)*C;document.getElementById('ring').setAttribute('stroke',score>=80?'#1f7a4d':score>=60?'#e26a1b':'#c1121f');document.getElementById('ringt').textContent=score;
document.getElementById('fh').textContent=(f.senior&&f.senior.name?f.senior.name:'Household')+'’s household';
document.getElementById('fm').textContent=(f.incidents||[]).length+' cases · '+(f.checkins||[]).length+' check-ins · '+(f.alerts||[]).length+' alerts';
var h=(f.incidents||[]).slice(0,6).map(function(c){var fl='';try{var rf=typeof c.red_flags==='string'?JSON.parse(c.red_flags):(c.red_flags||[]);fl=rf.slice(0,3).map(function(x){return \"<li>\"+esc(x.label||x)+\"</li>\"}).join('')}catch(e){}
return \"<div class='case \"+esc(c.verdict)+\"'><b>#\"+c.id+\"</b> <span class='verdict v-\"+esc(c.verdict)+\"'>\"+esc(c.verdict)+\"</span> · \"+esc(c.channel||'')+\" · \"+ago(c.created)+\"<br>\"+esc((c.caller_claim||'unknown').slice(0,120))+\"<ul style='margin:6px 0 0;padding-left:18px'>\"+fl+\"</ul></div>\"}).join('')||'<p>No incidents — a clean slate. 🕊️</p>';
h+='<div style=\"margin-top:8px;font-size:14px;color:#7a6a55\">Routines: '+esc((f.routines||[]).slice(0,2).map(function(r){return r.label}).join(' · ')||'—')+'</div>';
document.getElementById('feed').innerHTML=h}catch(e){document.getElementById('feed').innerHTML='<p>Feed offline.</p>'}}
function tabs(){var map=[['tab-chat','pane-chat'],['tab-feed','pane-feed'],['tab-tools','pane-tools']];
map.forEach(function(x){document.getElementById(x[0]).onclick=function(){map.forEach(function(y){document.getElementById(y[0]).classList.toggle('active',y[0]===x[0]);document.getElementById(y[1]).hidden=y[1]!==x[1]});if(x[1]==='pane-feed')feed()}})}
document.getElementById('b-send').onclick=function(){send()};document.getElementById('b-voice').onclick=voiceIn;
document.getElementById('b-hear').onclick=function(){speak(lastSpoken||'Kavach is listening')};
document.getElementById('b-clear').onclick=function(){thread.innerHTML='';cardsEl.innerHTML=''};
document.getElementById('q').addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});
document.querySelectorAll('[data-q]').forEach(function(b){b.onclick=function(){send(b.getAttribute('data-q'))}});
document.getElementById('b-feed').onclick=feed;
document.getElementById('b-pause').onclick=async function(){var l=document.getElementById('plang').value;var j=await(await fetch('/api/pause-card?lang='+encodeURIComponent(l))).json();document.getElementById('pause-out').textContent=j.card};
document.getElementById('b-dir').onclick=async function(){var q=document.getElementById('dq').value;var j=await(await fetch('/api/directory/lookup?q='+encodeURIComponent(q))).json();document.getElementById('dir-out').innerHTML=(j.entries||[]).slice(0,4).map(function(e){return \"<div class='case UNCERTAIN'><b>\"+esc(e.institution||'')+\"</b> · \"+esc(e.category||'')+\"<br><span style='font-size:13px'>\"+esc(e.hint||e.note||'Call back using a number you find yourself — never trust caller-ID.')+\"</span></div>\"}).join('')||'<p>No match — verify via official website.</p>'};
document.querySelectorAll('[data-s]').forEach(function(b){b.onclick=async function(){var r=await fetch('/api/demo/attack',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({senior_id:'demo-senior',scenario:b.getAttribute('data-s')})});var j=await r.json();document.getElementById('demo-out').textContent='🔴 Case #'+j.incident_id+' '+j.verdict+' — code '+j.confirm_code+'. Senior phone stayed silent; war-room alerted.';feed()}});
document.getElementById('b-ch').onclick=async function(){var r=await fetch('/api/family/challenge/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({senior_id:'demo-senior',claim_who:document.getElementById('cq').value})});var j=await r.json();document.getElementById('ch-out').textContent='Challenge '+j.id+' created — expires soon. Enrolled-device proof only.'};
tabs();status();setInterval(status,30000);
</script></body></html>"""


@app.get("/ui", response_class=HTMLResponse)
def fallback_ui():
    return FALLBACK_HTML


@app.get("/", response_class=HTMLResponse)
def index():
    return FALLBACK_HTML
