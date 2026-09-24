"""HTTP surface tests: health, version, chat validation, family feed, pause cards.

Guards the demo-day contract: every endpoint judges touch must answer
with the right shape and never 500 on bad input.
"""
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


def test_block_case_is_real_relay_mutation():
    atk = client.post("/api/demo/attack",
                      json={"senior_id": "block-senior", "scenario": "bank_otp"}).json()
    b = client.post("/api/family/block-case",
                    json={"senior_id": "block-senior",
                          "incident_id": atk["incident_id"]}).json()
    assert b["ok"] and len(b["number_hash"]) == 64
    assert b["household_id"] == "web|block-senior"
    lst = client.get("/api/v1/screen/list",
                     params={"household_id": "web|block-senior"}).json()
    assert any(e["number_hash"] == b["number_hash"] for e in lst["entries"])
    bad = client.post("/api/family/block-case",
                      json={"senior_id": "block-senior", "incident_id": 999999})
    assert bad.status_code == 404


def test_directory_jurisdiction_filter():
    all_in = client.get("/api/directory/lookup", params={"q": ""}).json()
    assert all_in["count"] >= 1
    # count is the total matches (not the page length): entries are capped.
    assert all_in["count"] >= len(all_in["entries"]) and len(all_in["entries"]) <= 25
    none = client.get("/api/directory/lookup",
                      params={"q": "", "jurisdiction": "US"}).json()
    assert none["count"] == 0
    # bad senior ids are 422, not silent slices.
    for bad in ("", "no way!!", "x" * 65):
        assert client.get("/api/family-feed", params={"senior_id": bad}).status_code == 422
    # unknown routes use the uniform envelope.
    nf = client.get("/api/nope-not-real")
    assert nf.status_code == 404 and nf.json()["error"] == "not_found"
    assert "request_id" in nf.json()
    # schema errors use the uniform envelope too.
    bad_chat = client.post("/api/chat", json={"text": "", "session_id": "t"})
    assert bad_chat.status_code == 422 and bad_chat.json()["error"] == "validation_error"


def test_nextgen_proof_contract():
    p = client.get("/api/nextgen/proof").json()
    assert p["track"] == "Next Gen" and p["test_mode"] is True
    assert "SHIPATON-JUDGE" in p["revenuecat"]["judge_promo"]
    assert "shield_protection" in p["revenuecat"]["entitlements"]
    assert p["repo"]["license_mit"] and p["repo"]["submission_pack"]
    assert p["repo"]["icon_1024"] and p["repo"]["screenshot_1179x2556"]


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
    # replay reports the STORED tier even if the replay names another one.
    w3 = client.post("/api/v1/billing/webhook",
                     json={"event_id": "evt-test-1", "household_id": "hh_x",
                           "event_type": "CANCELLATION", "entitlement": ""}).json()
    assert w3["ok"] and w3.get("duplicate") is True and w3["tier"] == w2["tier"]
    # purchase events with an empty entitlement never mint paid quota.
    hid2 = client.post("/api/v1/households").json()["household_id"]
    empty = client.post("/api/v1/billing/webhook",
                        json={"event_id": "evt-empty-ent", "household_id": hid2,
                              "event_type": "INITIAL_PURCHASE", "entitlement": ""})
    assert empty.status_code == 400
    # challenge error branches: missing id 404, bad decision 422, double 410.
    assert client.get("/api/family/challenge/ch_nope").status_code == 404
    assert client.post(f"/api/family/challenge/{c['id']}/respond",
                       json={"decision": "MAYBE"}).status_code == 422
    again = client.post(f"/api/family/challenge/{c['id']}/respond",
                        json={"decision": "APPROVE"})
    assert again.status_code == 410


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
