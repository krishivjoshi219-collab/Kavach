from fastapi.testclient import TestClient

import app as appmod

client = TestClient(appmod.app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200 and r.json()["ok"] and r.json()["service"] == "kavach"


def test_version_metrics_headers():
    r = client.get("/version")
    assert r.status_code == 200 and r.json()["mcp_spec"] == "2025-11-25"
    assert "mcp_app" in r.json() and r.json()["mcp_app"].startswith("ui://")
    m = client.get("/metrics")
    assert m.status_code == 200 and "uptime_s" in m.json()
    h = client.get("/healthz")
    assert h.headers.get("x-request-id")
    assert h.headers.get("x-content-type-options") == "nosniff"


def test_chat_validation():
    assert client.post("/api/chat", json={"text": "", "session_id": "t"}).status_code == 422
    assert client.post("/api/chat", json={"text": "hi", "session_id": "bad id!"}).status_code == 422
    r = client.post("/api/chat",
                    json={"text": "Someone called about my bank", "session_id": "scam1"})
    assert r.status_code == 200
    j = r.json()
    assert j.get("stage") == "channel" and "request_id" in j


def test_family_feed_and_board():
    f = client.get("/api/family-feed")
    assert f.status_code == 200
    j = f.json()
    assert {"senior", "incidents", "routines", "checkins", "alerts"} <= set(j)
    b = client.get("/apps/family-board.html")
    assert b.status_code == 200 and "kavach-family-board" in b.text


def test_ready_mcp_resources_live():
    # Single lifespan session: session_manager.run() allows one entry per process.
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
            assert "kavach" in r.text
        rl = live.post("/mcp", headers=h,
                       json={"jsonrpc": "2.0", "id": 1, "method": "resources/list",
                             "params": {}})
        assert rl.status_code == 200 and "ui://kavach-family-board" in rl.text
        tl = live.post("/mcp", headers=h,
                       json={"jsonrpc": "2.0", "id": 2, "method": "tools/list",
                             "params": {}})
        assert tl.status_code == 200
        for tool in ("debrief_caller", "report_incident", "incident_history", "checkin",
                     "confirm_routine", "verify_contact", "draft_family_alert",
                     "confirm_family_alert", "daily_briefing", "ask_kavach", "family_board"):
            assert tool in tl.text, tool
