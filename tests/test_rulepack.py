"""Rule packs: the shield learns. Tests prove: parity, signature, anti-tamper."""
from __future__ import annotations

from fastapi.testclient import TestClient

import app as appmod
from agent import redflags, rulepack

client = TestClient(appmod.app)


def test_pack_mirrors_source_of_truth():
    pack = rulepack.build_pack()
    assert pack["pack_version"] >= 1
    assert [r["code"] for r in pack["rules"]] == [c for c, *_ in redflags.RULES]
    assert pack["thresholds"] == {"scam": 5, "scam_with_core": 4, "suspicious": 3}


def test_sign_verify_roundtrip():
    served = rulepack.serve_pack()
    assert rulepack.verify_pack(served["pack"], served["signature"],
                                served["public_key"])


def test_tampered_pack_rejected():
    served = rulepack.serve_pack()
    evil = dict(served["pack"])
    evil["rules"] = [dict(r, weight=0) for r in served["pack"]["rules"]]
    assert not rulepack.verify_pack(evil, served["signature"], served["public_key"])


def test_wrong_key_rejected():
    import base64

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    other = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
    served = rulepack.serve_pack()
    assert not rulepack.verify_pack(served["pack"], served["signature"],
                                    base64.b64encode(other).decode())


def test_endpoint_serves_verifiable_pack():
    r = client.get("/api/v1/rules/pack")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True and body["pack"]["pack_version"] >= 1
    assert rulepack.verify_pack(body["pack"], body["signature"], body["public_key"])


def test_pack_still_catches_scam_and_spares_legit():
    pack = rulepack.build_pack()
    codes = {r["code"] for r in pack["rules"]}
    assert {"OTP_ASK", "THREAT", "KYC_PRIZE", "ID_HARVEST"} <= codes
    sig = redflags.extract_signals("HDFC BANK FROZEN share OTP now police arrest today")
    v, _, _ = redflags.score_verdict(sig, "x")
    assert v == "SCAM"
    sig2 = redflags.extract_signals("Your UPI txn of Rs 500 is successful")
    v2, _, _ = redflags.score_verdict(sig2, "x")
    assert v2 != "SCAM"
