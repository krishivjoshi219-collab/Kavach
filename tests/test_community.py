"""Community shield: one family's block protects all families. Hashes only."""
from __future__ import annotations

import re

from fastapi.testclient import TestClient

import app as appmod
from agent import mobile

client = TestClient(appmod.app)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SCAM_HASH = "a" * 64


def _fresh_households(n: int) -> list[str]:
    return [client.post("/api/v1/households").json()["household_id"] for _ in range(n)]


def test_threshold_three_before_shipping():
    h = _fresh_households(4)
    target = "b" * 64
    for i in range(2):
        assert mobile.block_number(h[i], target, "bank otp scam", "block")
    assert target not in {e["number_hash"] for e in mobile.threat_feed()}
    assert mobile.block_number(h[2], target, "bank otp scam", "block")
    feed = {e["number_hash"]: e for e in mobile.threat_feed()}
    assert feed[target]["reports"] >= 3


def test_one_household_counts_once():
    h = _fresh_households(1)
    target = "c" * 64
    mobile.block_number(h[0], target, "x", "block")
    mobile.block_number(h[0], target, "x", "block")
    # A lone household re-blocking can never tip the threshold alone.
    assert target not in {e["number_hash"] for e in mobile.threat_feed()}


def test_lookup_falls_through_to_community():
    h = _fresh_households(4)
    target = "d" * 64
    assert mobile.lookup_number(h[3], target)["source"] == "none"
    for i in range(3):
        mobile.block_number(h[i], target, "digital arrest", "block")
    hit = mobile.lookup_number(h[3], target)
    assert hit == {"action": "block", "reason": hit["reason"], "source": "community"}
    assert "3 households" in hit["reason"]


def test_household_list_beats_community():
    h = _fresh_households(4)
    target = "e" * 64
    for i in range(3):
        mobile.block_number(h[i], target, "spam", "block")
    mobile.block_number(h[3], target, "neighbor, allow", "allow")
    assert mobile.lookup_number(h[3], target)["source"] == "household"


def test_unblock_retracts_my_report():
    h = _fresh_households(3)
    target = "f" * 64
    for i in range(3):
        mobile.block_number(h[i], target, "spam", "block")
    assert target in {e["number_hash"] for e in mobile.threat_feed()}
    mobile.unblock_number(h[0], target)
    assert target not in {e["number_hash"] for e in mobile.threat_feed()}


def test_allow_retracts_my_community_vote():
    # Flipping to allow/silence must retract the vote too — otherwise the
    # stale report keeps counting toward the 3-household threshold.
    h = _fresh_households(3)
    target = "1" * 64
    for i in range(3):
        mobile.block_number(h[i], target, "spam", "block")
    assert target in {e["number_hash"] for e in mobile.threat_feed()}
    assert mobile.block_number(h[0], target, "neighbor, allow", "allow") is True
    assert target not in {e["number_hash"] for e in mobile.threat_feed()}
    # Household list still wins locally.
    assert mobile.lookup_number(h[0], target)["source"] == "household"


def test_concurrent_pairing_seal_single_winner():
    # One pairing code seals exactly once, even under concurrent completes.
    import threading
    h = _fresh_households(1)
    init = client.post("/api/v1/pair/init",
                       json={"household_id": h[0], "manager_pubkey": "K" * 64}).json()
    code = init["pairing_code"]
    wins = []
    lock = threading.Lock()

    def attempt():
        out = mobile.complete_pairing(code, "P" * 64, "racer")
        with lock:
            wins.append(out is not None)

    threads = [threading.Thread(target=attempt) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sum(wins) == 1


def test_concurrent_challenge_single_decision():
    # Concurrent APPROVE + DENY: exactly one wins, the loser gets None.
    import threading

    from agent import models as _models
    ch = _models.create_challenge("s", "who", "q?")
    results = {}
    lock = threading.Lock()

    def attempt(name, decision):
        out = _models.respond_challenge(ch["id"], decision)
        with lock:
            results[name] = out

    threads = [threading.Thread(target=attempt, args=("a", "APPROVE")),
               threading.Thread(target=attempt, args=("d", "DENY"))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    winners = [k for k, v in results.items() if v is not None]
    assert len(winners) == 1


def test_feed_contains_hashes_only():
    body = client.get("/api/v1/threat-feed").json()
    assert body["ok"] is True and body["threshold"] == 3
    for e in body["entries"]:
        assert HEX64.match(e["number_hash"])
        assert isinstance(e["reports"], int) and e["reports"] >= 3
    # silence actions never feed the shield
    h = _fresh_households(3)
    target = "9" * 64
    for i in range(3):
        mobile.block_number(h[i], target, "quiet", "silence")
    assert target not in {e["number_hash"] for e in mobile.threat_feed()}
