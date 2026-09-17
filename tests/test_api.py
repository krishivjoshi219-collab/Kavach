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


def test_demo_attack_creates_scam_loop():
    r = client.post("/api/demo/attack", json={"senior_id": "demo-senior", "scenario": "bank_otp"})
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] and j["test_mode"] and j["verdict"] in ("SCAM", "SUSPICIOUS")
    assert j["incident_id"] and len(j["confirm_code"]) == 6
    f = client.get("/api/family-feed", params={"senior_id": "demo-senior"}).json()
    assert any(i["id"] == j["incident_id"] for i in f["incidents"])


def test_pause_directory_challenge_billing():
    for lang, needle in (("en", "Pause"), ("hi", "रुकें"), ("hinglish", "Ruko")):
        r = client.get("/api/pause-card", params={"lang": lang}).json()
        assert needle in r["card"] and r["offline"] is True
    d = client.get("/api/directory/lookup", params={"q": "hdfc"}).json()
    assert d["count"] >= 1 and d["entries"][0]["caller_authenticated"] is False
    c = client.post("/api/family/challenge/create",
                    json={"senior_id": "demo-senior", "claim_who": "Priya",
                          "question": "Did you ask for money?"}).json()
    assert c["ok"] and c["state"] == "pending"
    g = client.get(f"/api/family/challenge/{c['id']}").json()
    assert g["ok"] and g["challenge"]["state"] == "pending"
    r2 = client.post(f"/api/family/challenge/{c['id']}/respond",
                     json={"decision": "DENY"}).json()
    assert r2["ok"] and r2["decision"] == "DENY" and "saved number" in r2["wording"]
    w = client.post("/api/v1/billing/webhook",
                    json={"event_id": "evt-test-1", "household_id": "hh_x",
                          "event_type": "TEST", "entitlement": "pro_caregiver"}).json()
    # hh_x may not exist in isolated DB: create a household and retry for tier path
    if not w.get("ok"):
        hid = client.post("/api/v1/households").json()["household_id"]
        w = client.post("/api/v1/billing/webhook",
                        json={"event_id": "evt-test-1b", "household_id": hid,
                              "event_type": "TEST", "entitlement": "pro_caregiver"}).json()
    assert w["ok"] and w["test_mode"] is True
    w2 = client.post("/api/v1/billing/webhook",
                     json={"event_id": "evt-test-1", "household_id": "hh_x",
                           "event_type": "TEST", "entitlement": "pro_caregiver"}).json()
    assert w2["ok"] and w2.get("duplicate") is True


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
