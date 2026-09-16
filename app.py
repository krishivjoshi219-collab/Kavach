"""K-VoiceOps production entrypoint.

Serves, on one port (HF Spaces :7860):
  GET  /healthz   liveness (always 200 when process is up)
  GET  /readyz    readiness (DB writable + MCP session manager running)
  GET  /version   build + capability descriptor
  GET  /metrics   operational counters (JSON, no extra deps)
  POST /api/chat  REST bridge for the Pages simulator (rate-limited)
  POST /mcp       real MCP over Streamable HTTP, spec 2025-11-25 (bare path)
  POST /mcp/      same (trailing-slash alias, no redirects)
  GET  /ui, /     lightweight fallback console (Pages is the full UI)
"""
from __future__ import annotations

import logging
import sqlite3
import tempfile
import threading
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse as StarletteJSON

from agent import config as cfg
from agent.ops_agent import run_agent_turn
from mcp_server.server import mcp

logging.basicConfig(level=getattr(logging, cfg.LOG_LEVEL.upper(), logging.INFO),
                    format="%(asctime)s %(levelname)s %(name)s rid=%(request_id)s %(message)s")
_base_logger = logging.getLogger("k-voiceops")


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
    # Start MCP session manager (task group) so Streamable HTTP works.
    _log(event="startup", mode=cfg.llm_status()["mode"], origins=cfg.ALLOWED_ORIGINS)
    async with mcp.session_manager.run():
        MCP_RUNNING["ok"] = True
        _log(event="mcp_ready")
        yield
    MCP_RUNNING["ok"] = False
    _log(event="shutdown")


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="K-VoiceOps Alexa+", version=cfg.APP_VERSION, lifespan=lifespan,
              docs_url="/docs", redoc_url=None)
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
    response.headers["x-frame-options"] = "DENY"
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
# Direct Starlette Routes to the session-manager ASGI app (no Mount -> no 307
# redirect, so strict MCP clients work on the bare /mcp path too).
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


@app.get("/healthz")
def healthz():
    return {"ok": True, "service": cfg.APP_NAME, "version": cfg.APP_VERSION,
            "mcp": "/mcp", "spec": cfg.MCP_SPEC_VERSION, "time": time.time()}


@app.get("/version")
def version():
    return {"service": cfg.APP_NAME, "version": cfg.APP_VERSION,
            "mcp_spec": cfg.MCP_SPEC_VERSION, "llm": cfg.llm_status(),
            "endpoints": ["/healthz", "/readyz", "/version", "/metrics",
                          "/api/chat", "/mcp", "/mcp/", "/ui"]}


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
    except Exception as e:  # noqa: BLE001
        checks["db_writable"] = False
        checks["db_error"] = str(e)[:200]
    ready = bool(checks["mcp_session_manager"] and checks["db_writable"])
    return JSONResponse({"ready": ready, "checks": checks},
                        status_code=200 if ready else 503)


@app.get("/metrics")
def metrics():
    with METRICS_LOCK:
        snap = dict(METRICS)
    chats = snap["chat_total"]
    avg = int(snap["chat_latency_ms_sum"] / chats) if chats else 0
    return {"uptime_s": int(time.time() - START_TIME), "avg_chat_latency_ms": avg, **snap}


@app.post("/api/chat")
@limiter.limit(f"{cfg.RATE_LIMIT_PER_MIN}/minute")
def chat(body: ChatIn, request: Request):
    text = body.text[: cfg.MAX_INPUT_CHARS]
    rid = getattr(request.state, "rid", uuid.uuid4().hex[:12])
    t0 = time.time()
    try:
        out = run_agent_turn(text, body.session_id or "default")
    except Exception as e:  # noqa: BLE001 - never 500 on demo day
        out = {"spoken": "Sorry, I hit an internal error.",
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


FALLBACK_HTML = """<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content='width=device-width,initial-scale=1'>
<title>K-VoiceOps Alexa+ (fallback UI)</title>
<style>body{font-family:system-ui;max-width:720px;margin:24px auto;padding:0 16px}
.card{border:1px solid #ddd;border-radius:12px;padding:12px;margin:10px 0}
button{padding:10px 16px;border-radius:10px;border:0;background:#232f3e;color:#fff}</style>
</head><body>
<h2>K-VoiceOps Alexa+ — fallback console</h2>
<p>Full simulator: deploy <code>simulator/web</code> to Cloudflare Pages and point it at
<code>/api/chat</code>. This page works even if Pages is down. Status: <a href="/readyz">readyz</a>
&middot; <a href="/metrics">metrics</a> &middot; <a href="/version">version</a></p>
<textarea id=q rows=3 style='width:100%'>why did my deploy fail?</textarea><br><br>
<button onclick='go()'>Ask</button> <span id=lat></span><div id=out></div>
<script>async function go(){const t0=Date.now();
const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({text:document.getElementById('q').value,session_id:'demo'})});
const j=await r.json();document.getElementById('lat').textContent=' '+(Date.now()-t0)+'ms';
document.getElementById('out').innerHTML='<div class=card><b>Alexa says:</b> '+j.spoken+'</div>'+
(j.cards||[]).map(c=>'<div class=card><b>'+c.title+'</b><pre>'+(c.body||'').slice(0,2000)+'</pre></div>').join('')
+(j.tools||[]).map(t=>'<div class=card><small>'+t+'</small></div>').join('');}</script>
</body></html>"""


@app.get("/ui", response_class=HTMLResponse)
def fallback_ui():
    return FALLBACK_HTML


@app.get("/", response_class=HTMLResponse)
def index():
    return FALLBACK_HTML
