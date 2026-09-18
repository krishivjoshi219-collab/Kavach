"""Versioned, signed rule packs: the shield learns without going blind.

Design: the pack is BUILT from agent.redflags.RULES (single source of truth,
zero drift between server verdicts and published packs). The relay signs the
canonical JSON with Ed25519; the app applies a pack only if the signature
verifies AND the version is newer, else keeps baked-in/last-good rules.

Key handling: RULE_PACK_SIGNING_KEY env holds the base64 32-byte private seed
(stable identity in production). Unset = ephemeral dev key + test_mode=True
(honest TEST MODE for the hackathon). The public key ships inside every
/response so the app can pin it; release builds also bake it in.
"""
from __future__ import annotations

import base64
import json
import os

from . import redflags

PACK_VERSION = 1
KEY_ID = "kavach-rules-v1"
THRESHOLDS = {"scam": 5, "scam_with_core": 4, "suspicious": 3}
CORE_CODES = ["OTP_ASK", "THREAT"]


def _load_keypair() -> tuple[bytes, bytes, bool]:
    """Returns (private_seed_32, public_key_32, test_mode)."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    seed_b64 = os.getenv("RULE_PACK_SIGNING_KEY", "")
    if seed_b64:
        try:
            seed = base64.b64decode(seed_b64)
            priv = Ed25519PrivateKey.from_private_bytes(seed)
            pub = priv.public_key().public_bytes_raw()
            return seed, pub, False
        except ValueError:
            pass  # bad env key falls back to ephemeral dev key, honestly flagged
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key().public_bytes_raw()
    seed = priv.private_bytes_raw()
    return seed, pub, True


_SEED, _PUB, _TEST_MODE = _load_keypair()


def build_pack() -> dict:
    """Serialize RULES + thresholds into the versioned pack dict."""
    rules = [{"code": code, "label": label, "pattern": pat,
              "weight": weight, "meaning": meaning}
             for code, label, pat, weight, meaning in redflags.RULES]
    return {"pack_version": PACK_VERSION, "key_id": KEY_ID,
            "thresholds": dict(THRESHOLDS), "core_codes": list(CORE_CODES),
            "rules": rules,
            "changelog": [("v1: initial pack — 8 weighted rules, EN+HI patterns, "
                            "word-boundary guards, bijli/paise seeds.")]}


def _canonical(pack: dict) -> bytes:
    return json.dumps(pack, sort_keys=True, separators=(",", ":")).encode()


def sign_pack(pack: dict) -> str:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    priv = Ed25519PrivateKey.from_private_bytes(_SEED)
    return base64.b64encode(priv.sign(_canonical(pack))).decode()


def public_key_b64() -> str:
    return base64.b64encode(_PUB).decode()


def verify_pack(pack: dict, signature_b64: str, pub_b64: str) -> bool:
    """What the app does: verify before applying. Same math, no trust."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(pub_b64))
        pub.verify(base64.b64decode(signature_b64), _canonical(pack))
        return True
    except Exception:  # noqa: BLE001 - any verify failure is a reject, by design
        return False


def serve_pack() -> dict:
    pack = build_pack()
    return {"pack": pack, "signature": sign_pack(pack),
            "public_key": public_key_b64(), "key_id": KEY_ID,
            "test_mode": _TEST_MODE}


def is_test_mode() -> bool:
    return _TEST_MODE
