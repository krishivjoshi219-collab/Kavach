"""Mobile contract tests: pairing, blind relay, hash screening, consent, commands, quota."""
from fastapi.testclient import TestClient

import app as appmod
from agent import mobile

client = TestClient(appmod.app)
PUB_A = "A" * 64
PUB_B = "B" * 64


def _household():
    return client.post("/api/v1/households").json()["household_id"]


def test_pairing_flow_and_expiry():
    hid = _household()
    bad = client.post("/api/v1/pair/init",
                      json={"household_id": hid, "manager_pubkey": ""})
    assert bad.json()["ok"] is False
    init = client.post("/api/v1/pair/init",
                       json={"household_id": hid, "manager_pubkey": PUB_A}).json()
    assert init["ok"] and len(init["pairing_code"]) == 6
    nope = client.post("/api/v1/pair/complete",
                       json={"pairing_code": "ZZZZZZ", "senior_pubkey": PUB_B,
                             "senior_id": "s1"})
    assert nope.json()["ok"] is False
    done = client.post("/api/v1/pair/complete",
                       json={"pairing_code": init["pairing_code"], "senior_pubkey": PUB_B,
                             "senior_id": "s1"}).json()
    assert done["ok"] and done["manager_pubkey"] == PUB_A
    again = client.post("/api/v1/pair/complete",
                        json={"pairing_code": init["pairing_code"], "senior_pubkey": PUB_B,
                              "senior_id": "s1"}).json()
    assert again["ok"] is False  # single-use codes


def _noise(n: int = 96, seed: int = 0) -> str:
    import base64
    # Deterministic non-UTF8 bytes: always valid E2E-shaped noise, never flaky.
    # (os.urandom can randomly spell "otp"/"kyc" in base64 and get rejected.)
    raw = bytes(((seed * 37 + i * 11) % 251 + 2) % 256 for i in range(n))
    return base64.b64encode(raw).decode()


def test_blind_relay_never_sees_plaintext():
    hid = _household()
    cipher = _noise()
    bid = client.post("/api/v1/sync/push",
                      json={"household_id": hid, "sender": "senior",
                            "nonce": "nonce-001-abc", "ciphertext": cipher}).json()
    assert bid["ok"]
    blobs = client.get("/api/v1/sync/pull",
                       params={"household_id": hid}).json()["blobs"]
    assert len(blobs) == 1 and blobs[0]["ciphertext"] == cipher
    assert blobs[0]["epoch"] == 0
    # plaintext is rejected: raw OTP words, fake ENCRYPTED prefix, short nonce
    bad1 = client.post("/api/v1/sync/push",
                       json={"household_id": hid, "sender": "senior",
                             "nonce": "nonce-002-abc",
                             "ciphertext": "ENCRYPTED:otp-is-123456-mom"}).json()
    assert bad1["ok"] is False
    bad2 = client.post("/api/v1/sync/push",
                       json={"household_id": hid, "sender": "senior",
                             "nonce": "n1", "ciphertext": cipher}).json()
    assert bad2["ok"] is False
    # nonce reuse = replay rejected
    dup = client.post("/api/v1/sync/push",
                      json={"household_id": hid, "sender": "senior",
                            "nonce": "nonce-001-abc", "ciphertext": _noise()}).json()
    assert dup["ok"] is False
    assert client.post("/api/v1/sync/push",
                       json={"household_id": hid, "sender": "alien",
                             "nonce": "nonce-003-abc", "ciphertext": _noise()}).status_code == 422


def test_pairing_grants_all_manager_powers_and_revoke_bumps_epoch():
    hid = _household()
    init = client.post("/api/v1/pair/init",
                       json={"household_id": hid, "manager_pubkey": PUB_A}).json()
    assert init["ok"]
    done = client.post("/api/v1/pair/complete",
                       json={"pairing_code": init["pairing_code"], "senior_pubkey": PUB_B,
                             "senior_id": "e2e-senior"}).json()
    assert done["ok"]
    consent = client.get("/api/v1/consent",
                         params={"household_id": hid, "senior_id": "e2e-senior"}).json()
    assert consent["granted"] is True
    assert all(consent["capabilities"].values()), consent["capabilities"]
    assert consent["epoch"] == 0
    # remote cut works with auto-grant
    q = client.post("/api/v1/device/command",
                    json={"household_id": hid, "senior_id": "e2e-senior", "target": "senior",
                          "type": "cut_call"}).json()
    assert q["ok"]
    # kill switch: revoke bumps epoch, wipes queued commands, blocks new ones
    assert client.post("/api/v1/consent/revoke",
                       params={"household_id": hid, "senior_id": "e2e-senior"}).json()["ok"] is True
    consent2 = client.get("/api/v1/consent",
                          params={"household_id": hid, "senior_id": "e2e-senior"}).json()
    assert consent2["granted"] is False and consent2["epoch"] == 1
    pend = client.get("/api/v1/device/commands",
                      params={"household_id": hid, "target": "senior"}).json()
    assert pend["commands"] == []
    r2 = client.post("/api/v1/device/command",
                     json={"household_id": hid, "senior_id": "e2e-senior", "target": "senior",
                           "type": "cut_call"}).json()
    assert r2["ok"] is False


def test_error_status_codes_are_http_correct():
    # Business rejections carry real HTTP codes (same ok:false envelope).
    hid = _household()
    h = "a" * 64
    assert client.post("/api/v1/pair/init",
                       json={"household_id": "hh_nope", "manager_pubkey": PUB_A}).status_code == 404
    assert client.post("/api/v1/pair/complete",
                       json={"pairing_code": "ZZZZZZ", "senior_pubkey": PUB_B,
                             "senior_id": "s1"}).status_code == 404
    assert client.get("/api/v1/pair/peer",
                      params={"household_id": hid}).status_code == 404
    assert client.post("/api/v1/screen/unblock",
                       json={"household_id": hid, "number_hash": h}).status_code == 404
    assert client.post("/api/v1/device/commands/999999/ack").status_code == 404
    assert client.post("/api/v1/device/commands/0/ack").status_code == 422
    assert client.get("/api/v1/device/commands",
                      params={"household_id": hid, "target": "alien"}).status_code == 422
    assert client.get("/api/v1/sync/pull",
                      params={"household_id": hid, "since_id": -1}).status_code == 422
    for bad in ("", "not a household!!", "x" * 65):
        assert client.get("/api/v1/screen/list",
                          params={"household_id": bad}).status_code == 422
        assert client.get("/api/v1/threat-radar",
                          params={"household_id": bad}).status_code == 422
    # consent_required is a 403, not a 200.
    r = client.post("/api/v1/device/command",
                    json={"household_id": hid, "senior_id": "ghost", "target": "senior",
                          "type": "cut_call"})
    assert r.status_code == 403 and r.json()["error"] == "consent_required"
    # revoke of a nonexistent record is a 404.
    assert client.post("/api/v1/consent/revoke",
                       params={"household_id": hid, "senior_id": "ghost"}).status_code == 404
    # short nonce / short ciphertext fail at schema (422), not as 400s.
    assert client.post("/api/v1/sync/push",
                       json={"household_id": hid, "sender": "senior",
                             "nonce": "short", "ciphertext": "x" * 100}).status_code == 422
    # every manual error carries request_id like the 422 handler.
    assert "request_id" in r.json()


def test_quota_burst_stays_capped():
    # Concurrent asks at the quota edge must not overshoot: atomic increment.
    import threading

    from agent import mobile as _mobile
    hid, sid = _household(), "burst"
    client.post("/api/v1/consent/set",
                json={"household_id": hid, "senior_id": sid,
                      "capabilities": {"cloud_brain": True}, "granted_by": sid})
    # Drain to 19/20 via direct calls (fast, no HTTP).
    for _ in range(19):
        assert _mobile.brain_ask(hid, "hello")["ok"] is True
    results = []
    lock = threading.Lock()

    def ask():
        out = _mobile.brain_ask(hid, "hello")
        with lock:
            results.append(out)

    threads = [threading.Thread(target=ask) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    oks = [r for r in results if r["ok"]]
    denied = [r for r in results if r.get("error") == "quota_exceeded"]
    # 19 used + 8 racers, quota 20 → exactly 1 winner, 7 denied.
    assert len(oks) == 1 and len(denied) == 7


def test_corrupt_rows_degrade_safely():
    # Poisoned JSON rows must deny/restart, never 500.
    import sqlite3

    import agent.config as cfg
    hid, sid = _household(), "corrupt-senior"
    client.post("/api/v1/consent/set",
                json={"household_id": hid, "senior_id": sid,
                      "capabilities": {"remote_cut": True}, "granted_by": sid})
    conn = sqlite3.connect(cfg.DB_PATH, timeout=10)
    try:
        conn.execute("UPDATE consent SET capabilities='{{not-json' WHERE household_id=?",
                     (hid,))
        conn.commit()
    finally:
        conn.close()
    # Consent check denies instead of 500ing the command path.
    r = client.post("/api/v1/device/command",
                    json={"household_id": hid, "senior_id": sid, "target": "senior",
                          "type": "cut_call"})
    assert r.json()["ok"] is False
    # Corrupt flow data restarts the session instead of 500ing chat.
    from agent import models as _models
    _models.set_flow("poisoned", "debrief", "who", None, {"senior_id": "demo-senior"})
    conn = sqlite3.connect(cfg.DB_PATH, timeout=10)
    try:
        conn.execute("UPDATE flows SET data='{{bad' WHERE session_id='poisoned'")
        conn.commit()
    finally:
        conn.close()
    r = client.post("/api/chat",
                    json={"text": "hello?", "session_id": "poisoned"})
    assert r.status_code == 200 and "spoken" in r.json()
    # Corrupt session history restarts cleanly too.
    _models.save_turn("poisoned2", "user", "seed")
    conn = sqlite3.connect(cfg.DB_PATH, timeout=10)
    try:
        conn.execute("UPDATE sessions SET history='\"just-a-string\"' WHERE id='poisoned2'")
        conn.commit()
    finally:
        conn.close()
    r = client.post("/api/chat",
                    json={"text": "hi there", "session_id": "poisoned2"})
    assert r.status_code == 200 and "spoken" in r.json()


def test_hash_screening_allow_block_unblock():
    hid = _household()
    h = mobile.hash_number(hid, "+91-98XXX-XXX99")
    assert len(h) == 64
    assert client.post("/api/v1/screen/lookup",
                       json={"household_id": hid, "number_hash": h}).json()["action"] == "allow"
    assert client.post("/api/v1/screen/block",
                       json={"household_id": hid, "number_hash": h,
                             "label": "scam call", "action": "block"}).json()["ok"] is True
    hit = client.post("/api/v1/screen/lookup",
                      json={"household_id": hid, "number_hash": h}).json()
    assert hit["action"] == "block" and hit["source"] == "household"
    lst = client.get("/api/v1/screen/list", params={"household_id": hid}).json()
    assert lst["ok"] and any(e["number_hash"] == h for e in lst["entries"])
    assert client.post("/api/v1/screen/unblock",
                       json={"household_id": hid, "number_hash": h}).json()["ok"] is True
    lst2 = client.get("/api/v1/screen/list", params={"household_id": hid}).json()
    assert all(e["number_hash"] != h for e in lst2["entries"])
    # raw numbers are never accepted: hashes only
    assert client.post("/api/v1/screen/lookup",
                       json={"household_id": hid,
                             "number_hash": "+91-98XXX-XXX99"}).status_code == 422


def test_consent_gates_remote_cut():
    hid, sid = _household(), "dad1"
    # no consent: remote cut refused
    r = client.post("/api/v1/device/command",
                    json={"household_id": hid, "senior_id": sid, "target": "senior",
                          "type": "cut_call"}).json()
    assert r["ok"] is False and r["error"] == "consent_required"
    # grant everything, then cut works
    assert client.post("/api/v1/consent/set",
                       json={"household_id": hid, "senior_id": sid,
                             "capabilities": {"remote_cut": True, "screen_calls": True},
                             "granted_by": "dad1"}).json()["ok"] is True
    q = client.post("/api/v1/device/command",
                    json={"household_id": hid, "senior_id": sid, "target": "senior",
                          "type": "cut_call"}).json()
    assert q["ok"] and "command_id" in q
    pend = client.get("/api/v1/device/commands",
                      params={"household_id": hid, "target": "senior"}).json()
    assert len(pend["commands"]) == 1
    assert client.post(f"/api/v1/device/commands/{q['command_id']}/ack").json()["ok"] is True
    # revoke = kill switch: everything refused again
    assert client.post("/api/v1/consent/revoke",
                       params={"household_id": hid, "senior_id": sid}).json()["ok"] is True
    r2 = client.post("/api/v1/device/command",
                     json={"household_id": hid, "senior_id": sid, "target": "senior",
                           "type": "cut_call"}).json()
    assert r2["ok"] is False


def test_brain_quota_and_consent():
    hid, sid = _household(), "dad2"
    # cloud brain off by default
    assert client.post("/api/v1/brain/ask",
                       json={"household_id": hid, "senior_id": sid,
                             "snippet": "share otp now"}).json()["error"] == "consent_required"
    client.post("/api/v1/consent/set",
                json={"household_id": hid, "senior_id": sid,
                      "capabilities": {"cloud_brain": True}, "granted_by": "dad2"})
    first = client.post("/api/v1/brain/ask",
                        json={"household_id": hid, "senior_id": sid,
                              "snippet": "account frozen share otp immediately"}).json()
    assert first["ok"] and first["verdict"] == "SCAM" and first["tier"] == "free"
    # exhaust the free quota (20)
    for _ in range(25):
        last = client.post("/api/v1/brain/ask",
                           json={"household_id": hid, "senior_id": sid,
                                 "snippet": "hello"}).json()
    assert last["ok"] is False and last["error"] == "quota_exceeded"
    # upgrade to pro: 10x quota, verdicts flow again
    assert client.post("/api/v1/household/tier",
                       json={"household_id": hid, "tier": "pro"}).json()["ok"] is True
    assert client.get("/api/v1/household/tier",
                      params={"household_id": hid}).json() == {"tier": "pro", "quota": 200}
    again = client.post("/api/v1/brain/ask",
                        json={"household_id": hid, "senior_id": sid,
                              "snippet": "hello"}).json()
    assert again["ok"] is True and again["tier"] == "pro"


def test_checkin_and_onesignal_notifications():
    hid, sid = _household(), "dad3"
    # Daily wellness check-in
    c = client.post("/api/v1/checkin",
                    json={"household_id": hid, "senior_id": sid, "status": "safe"}).json()
    assert c["ok"] and c["acknowledged"]

    # Morning check-in journey
    m = client.post("/api/v1/notifications/send",
                    json={"household_id": hid, "journey": "morning_checkin", "senior_id": sid}).json()
    assert m["ok"] and m.get("simulated", True)

    # Missed check-in nudge to caregiver
    n = client.post("/api/v1/notifications/send",
                    json={"household_id": hid, "journey": "missed_checkin"}).json()
    assert n["ok"]

    # Emergency scam interception breakthrough alert
    e = client.post("/api/v1/notifications/send",
                    json={"household_id": hid, "journey": "emergency_alert",
                          "caller_hash": "a" * 64, "reasons": ["OTP Ask", "Freeze threat"]}).json()
    assert e["ok"]


def test_threat_radar():
    radar = client.get("/api/v1/threat-radar").json()
    assert radar["ok"] is True
    assert "household_stats" in radar
    assert radar["household_stats"]["total_threats_shielded"] >= 0
    assert radar["zero_knowledge_enforced"] is True
    assert "Not carrier regional data" in radar["note"]


def test_checkin_persists():
    hid = _household()
    c = client.post("/api/v1/checkin",
                    json={"household_id": hid, "senior_id": "radar-senior",
                          "status": "safe", "note": "morning ok"}).json()
    assert c["ok"] and c["mood"] == "ok" and c["checkin_id"] is not None


def test_relay_stats_and_blob_cap():
    before = client.get("/metrics").json()["relay"]["push_total"]
    hid = _household()
    for i in range(3):
        r = client.post("/api/v1/sync/push",
                        json={"household_id": hid, "sender": "senior",
                              "nonce": f"stat-nonce-{i}-xyz",
                              "ciphertext": _noise(96, seed=100 + i)}).json()
        assert r["ok"]
    after = client.get("/metrics").json()["relay"]
    assert after["push_total"] == before + 3
    assert after["households_total"] >= 1
    # Flood past the per-household cap via direct calls (fast, no HTTP).
    for i in range(505):
        mobile.push_blob(hid, "senior", f"cap-{i:04d}-zzzz", _noise(96, seed=200 + i))
    blobs = mobile.pull_blobs(hid, 0, limit=200)
    assert len(blobs) == 200  # capped page
    assert mobile.community_stats(hid)["household_blobs"] == mobile.MAX_BLOBS_PER_HOUSEHOLD
    nonces = [b["nonce"] for b in mobile.pull_blobs(hid, 0, limit=200)]
    assert "cap-0000-zzzz" not in nonces  # oldest pruned

