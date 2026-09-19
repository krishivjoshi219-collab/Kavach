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
import tempfile
import threading
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from mcp.server.fastmcp.server import StreamableHTTPASGIApp
from pydantic import BaseModel, Field
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse as StarletteJSON
from starlette.routing import Route

import mobile_api
from agent import config as cfg
from agent import models
from agent.kavach_agent import run_agent_turn
from agent.ratelimit import limiter
from mcp_server.server import UI_URI, mcp

logging.basicConfig(level=getattr(logging, cfg.LOG_LEVEL.upper(), logging.INFO),
                    format="%(asctime)s %(levelname)s %(name)s rid=%(request_id)s %(message)s")
_base_logger = logging.getLogger("kavach")


def _log(**fields: object) -> None:
    _base_logger.info(" ".join(f"{k}={v}" for k, v in fields.items()),
                      extra={"request_id": fields.get("rid", "-")})


START_TIME = time.time()
METRICS_LOCK = threading.Lock()
METRICS: dict[str, float] = {
    "requests_total": 0, "chat_total": 0, "chat_errors": 0,
    "chat_latency_ms_sum": 0, "mcp_total": 0, "rate_limited": 0,
}
MCP_RUNNING = {"ok": False}


@asynccontextmanager
async def lifespan(_: FastAPI):
    _log(event="startup", mode=cfg.llm_status()["mode"], origins=cfg.ALLOWED_ORIGINS)
    async with mcp.session_manager.run():
        MCP_RUNNING["ok"] = True
        _log(event="mcp_ready")
        yield
    MCP_RUNNING["ok"] = False
    _log(event="shutdown")


app = FastAPI(title="Kavach — voice guardian for seniors", version=cfg.APP_VERSION,
              lifespan=lifespan, docs_url="/docs", redoc_url=None)
app.state.limiter = limiter
app.include_router(mobile_api.router)


@app.exception_handler(RateLimitExceeded)
async def _ratelimit_handler(request: Request, exc: RateLimitExceeded):
    with METRICS_LOCK:
        METRICS["rate_limited"] += 1
    rid = getattr(request.state, "rid", "-")
    return StarletteJSON({"ok": False, "error": "rate_limited",
                          "detail": "Too many requests, slow down and retry.",
                          "request_id": rid}, status_code=429)


@app.exception_handler(Exception)
async def _catch_all(request: Request, exc: Exception):
    rid = getattr(request.state, "rid", "-")
    _log(event="unhandled", rid=rid, path=request.url.path, err=str(exc)[:200])
    with METRICS_LOCK:
        METRICS["chat_errors"] += 1
    return StarletteJSON({"ok": False, "error": "internal",
                          "detail": "Internal error. Retry with this request_id.",
                          "request_id": rid}, status_code=500)


@app.middleware("http")
async def _request_context(request: Request, call_next):
    rid = request.headers.get("x-request-id", uuid.uuid4().hex[:12])
    request.state.rid = rid
    t0 = time.time()
    with METRICS_LOCK:
        METRICS["requests_total"] += 1
        if request.url.path in ("/mcp", "/mcp/"):
            METRICS["mcp_total"] += 1
    try:
        response = await call_next(request)
    except Exception:
        _log(event="middleware_error", rid=rid, path=request.url.path)
        raise
    latency = int((time.time() - t0) * 1000)
    response.headers["x-request-id"] = rid
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["referrer-policy"] = "no-referrer"
    response.headers["x-frame-options"] = "SAMEORIGIN"
    _log(event="request", rid=rid, method=request.method,
         path=request.url.path, status=response.status_code, latency_ms=latency)
    return response

origins = ["*"] if "*" in cfg.ALLOWED_ORIGINS else cfg.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
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
                          "/api/chat", "/api/family-feed", "/api/v1/* (mobile contract)",
                          "/mcp", "/mcp/", "/apps/family-board.html", "/ui"]}


@app.get("/readyz")
def readyz():
    checks: dict[str, object] = {"mcp_session_manager": MCP_RUNNING["ok"]}
    try:
        with tempfile.NamedTemporaryFile(dir="/tmp", delete=True):
            pass
        conn = sqlite3.connect(cfg.DB_PATH, timeout=5)
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS _ready(id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO _ready DEFAULT VALUES")
            conn.commit()
            conn.execute("DELETE FROM _ready")
            conn.commit()
        finally:
            conn.close()
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
    return {"uptime_s": int(time.time() - START_TIME), "avg_chat_latency_ms": avg,
            **snap, "relay": _mobile.relay_stats()}


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
def family_feed(senior_id: str = "demo-senior"):
    return JSONResponse(_feed(senior_id[:64]))


class DemoAttackIn(BaseModel):
    senior_id: str = Field(default="demo-senior", max_length=64, pattern=r"^[\w\-.]{1,64}$")
    scenario: str = Field(default="bank_otp", max_length=32, pattern=r"^[a-z0-9_]{1,32}$")


PAUSE_CARDS = {
    "en": ("Pause. Do not pay. Do not share codes. Verify through a contact you find yourself. "
           "Say: I will verify independently using an official channel. End the call if unsafe. "
           "Kavach is safety information, not legal advice."),
    "hi": ("रुकें। पैसे न भेजें। OTP/कोड साझा न करें। खुद खोजे गए आधिकारिक संपर्क से सत्यापित करें। "
           "कहें: मैं आधिकारिक चैनल से स्वतंत्र रूप से सत्यापित करूंगा। असुरक्षित लगे तो कॉल काट दें।"),
    "hinglish": ("Ruko. Paise mat bhejo. OTP/code share mat karo. Khud dhoondhe gaye official contact se verify karo. "
                 "Bolo: main independently verify karunga. Unsafe lage to call kaat do."),
}


@app.get("/api/pause-card")
def pause_card(lang: str = "en"):
    lang = lang[:8].lower()
    key = "hinglish" if "hing" in lang else "hi" if lang.startswith("hi") else "en"
    return JSONResponse({"lang": key, "card": PAUSE_CARDS[key], "offline": True,
                         "disclaimer": "General safety information, not legal advice."})


@app.get("/api/directory/lookup")
def directory_lookup(q: str = "", jurisdiction: str = "IN", lang: str = "en"):
    import os as _os
    path = _os.path.join(_os.path.dirname(__file__), "data", "official_directory.json")
    try:
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)
    except OSError:
        entries = []
    ql = q.lower()
    out = [e for e in entries
           if (not ql or ql in (e.get("institution", "") + e.get("category", "")).lower())
           and (jurisdiction.upper() in ("", e.get("jurisdiction", "IN").upper()) or True)]
    if lang[:2].lower() in ("hi", "en"):
        pref = [e for e in out if e.get("language") == lang[:2].lower()]
        if pref:
            out = pref
    for e in out:
        e["caller_authenticated"] = False
        e["note"] = "Directory does not authenticate the caller. Caller ID can be spoofed."
    return JSONResponse({"entries": out[:25], "count": len(out[:25])})


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


@app.post("/api/chat")
@limiter.limit(f"{cfg.RATE_LIMIT_PER_MIN}/minute")
def chat(body: ChatIn, request: Request):
    text = body.text[: cfg.MAX_INPUT_CHARS]
    rid = getattr(request.state, "rid", uuid.uuid4().hex[:12])
    t0 = time.time()
    try:
        out = run_agent_turn(text, body.session_id or "default",
                             body.senior_id or "demo-senior")
    except Exception as e:  # noqa: BLE001 - chat must never 500 on demo day
        out = {"spoken": "Something hiccuped on my side — but everything you said is saved. "
                         "Please try once more.",
               "text": f"error: {str(e)[:300]}", "cards": [], "tools": [], "provider": "error"}
        with METRICS_LOCK:
            METRICS["chat_errors"] += 1
    latency = int((time.time() - t0) * 1000)
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



FALLBACK_HTML = """<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content='width=device-width,initial-scale=1'>
<title>Kavach — voice guardian (fallback console)</title>
<style>body{font-family:system-ui;max-width:720px;margin:24px auto;padding:0 16px;
background:#faf6ec;color:#2b2118}
.card{border:1px solid #e3d5bd;background:#fff;border-radius:12px;padding:12px;margin:10px 0}
button{padding:10px 16px;border-radius:10px;border:0;background:#2b2118;color:#fff}</style>
</head><body>
<h2>🛡️ Kavach — fallback console</h2>
<p>The full experience lives in the simulator (senior voice view + family board).
Status: <a href="/readyz">readyz</a> &middot; <a href="/metrics">metrics</a>
&middot; <a href="/version">version</a> &middot;
<a href="/apps/family-board.html">family board app</a></p>
<textarea id=q rows=3 style='width:100%'>Someone called about my bank account</textarea><br><br>
<button onclick='go()'>Talk to Kavach</button> <span id=lat></span><div id=out></div>
<script>async function go(){const t0=Date.now();
const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({text:document.getElementById('q').value,session_id:'demo'})});
const j=await r.json();document.getElementById('lat').textContent=' '+(Date.now()-t0)+'ms';
document.getElementById('out').innerHTML='<div class=card><b>Kavach says:</b> '+j.spoken+'</div>'+
(j.cards||[]).map(c=>'<div class=card><b>'+c.title+'</b><pre>'+
(c.body||'').slice(0,2000)+'</pre></div>').join('');}</script>
</body></html>"""


@app.get("/ui", response_class=HTMLResponse)
def fallback_ui():
    return FALLBACK_HTML


@app.get("/", response_class=HTMLResponse)
def index():
    return FALLBACK_HTML
