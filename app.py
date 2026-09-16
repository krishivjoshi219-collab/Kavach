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
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse as StarletteJSON

from agent import config as cfg
from agent import models
from agent.kavach_agent import run_agent_turn
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


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Kavach — voice guardian for seniors", version=cfg.APP_VERSION,
              lifespan=lifespan, docs_url="/docs", redoc_url=None)
app.state.limiter = limiter


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
from mcp.server.fastmcp.server import StreamableHTTPASGIApp
from starlette.routing import Route

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
                          "/api/chat", "/api/family-feed", "/mcp", "/mcp/",
                          "/apps/family-board.html", "/ui"]}


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
    with METRICS_LOCK:
        snap = dict(METRICS)
    chats = snap["chat_total"]
    avg = int(snap["chat_latency_ms_sum"] / chats) if chats else 0
    return {"uptime_s": int(time.time() - START_TIME), "avg_chat_latency_ms": avg, **snap}


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
(j.cards||[]).map(c=>'<div class=card><b>'+c.title+'</b><pre>'+(c.body||'').slice(0,2000)+'</pre></div>').join('');}</script>
</body></html>"""


@app.get("/ui", response_class=HTMLResponse)
def fallback_ui():
    return FALLBACK_HTML


@app.get("/", response_class=HTMLResponse)
def index():
    return FALLBACK_HTML
