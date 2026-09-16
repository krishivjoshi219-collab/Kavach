import os

os.environ.setdefault("DB_PATH", "/tmp/assistant/test_api.db")

from fastapi.testclient import TestClient

import app as appmod

client = TestClient(appmod.app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200 and r.json()["ok"]


def test_chat_deploy_fail():
    r = client.post("/api/chat", json={"text": "why did my deploy fail?", "session_id": "t1"})
    assert r.status_code == 200
    j = r.json()
    assert j["cards"] and "request_id" in j


def test_version_ready_metrics_headers():
    r = client.get("/version")
    assert r.status_code == 200 and r.json()["mcp_spec"] == "2025-11-25"
    m = client.get("/metrics")
    assert m.status_code == 200 and "uptime_s" in m.json()
    h = client.get("/healthz")
    assert h.headers.get("x-request-id")
    assert h.headers.get("x-content-type-options") == "nosniff"


def test_chat_validation():
    assert client.post("/api/chat", json={"text": "", "session_id": "t"}).status_code == 422
    assert client.post("/api/chat", json={"text": "hi", "session_id": "bad id!"}).status_code == 422
    r = client.post("/api/chat", json={"text": "hello, what can you do?", "session_id": "t9"})
    assert r.status_code == 200 and r.headers.get("x-request-id")


def test_mcp_and_ready_live():
    # NOTE: session_manager.run() may only be entered once per process,
    # so all lifespan-dependent asserts share this single TestClient session.
    body = {"jsonrpc": "2.0", "id": 0, "method": "initialize",
            "params": {"protocolVersion": "2025-11-25", "capabilities": {},
                       "clientInfo": {"name": "t", "version": "0"}}}
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
         "MCP-Protocol-Version": "2025-11-25"}
    with TestClient(appmod.app, base_url="http://localhost:8000") as live:
        rz = live.get("/readyz")
        assert rz.status_code == 200 and rz.json()["ready"] is True
        for path in ("/mcp", "/mcp/"):
            r = live.post(path, headers=h, json=body)
            assert r.status_code == 200, (path, r.status_code, r.text[:200])
            assert "k-voiceops" in r.text
