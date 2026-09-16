"""Mobile contract: households, pairing, blind relay, screening, consent, commands, quota.

Privacy design: the server stores public keys, number HASHES (household-salted),
and opaque ciphertext blobs. It never sees secrets, transcripts, or raw numbers.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import time
from typing import Any

from . import config, redflags

SCHEMA = """
CREATE TABLE IF NOT EXISTS households(
  id TEXT PRIMARY KEY, tier TEXT NOT NULL DEFAULT 'free', created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS pairings(
  code TEXT PRIMARY KEY, household_id TEXT NOT NULL, manager_pubkey TEXT NOT NULL,
  senior_pubkey TEXT NOT NULL DEFAULT '', senior_id TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'open', created REAL NOT NULL, expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS blobs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, household_id TEXT NOT NULL, sender TEXT NOT NULL,
  nonce TEXT NOT NULL, ciphertext TEXT NOT NULL, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS blocklist(
  household_id TEXT NOT NULL, number_hash TEXT NOT NULL, label TEXT NOT NULL DEFAULT '',
  action TEXT NOT NULL DEFAULT 'block', created REAL NOT NULL,
  PRIMARY KEY (household_id, number_hash));
CREATE TABLE IF NOT EXISTS consent(
  household_id TEXT NOT NULL, senior_id TEXT NOT NULL, capabilities TEXT NOT NULL,
  granted_by TEXT NOT NULL DEFAULT '', revoked INTEGER NOT NULL DEFAULT 0,
  created REAL NOT NULL, updated REAL NOT NULL,
  PRIMARY KEY (household_id, senior_id));
CREATE TABLE IF NOT EXISTS commands(
  id INTEGER PRIMARY KEY AUTOINCREMENT, household_id TEXT NOT NULL, target TEXT NOT NULL,
  type TEXT NOT NULL, payload_cipher TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT
  'queued', created REAL NOT NULL, delivered REAL);
CREATE TABLE IF NOT EXISTS usage(
  household_id TEXT NOT NULL, month TEXT NOT NULL, brain_calls INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (household_id, month));
"""

QUOTAS = {"free": 20, "pro": 200, "ultra": 2000}
PAIR_TTL_S = 600


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(config.DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _now() -> float:
    return time.time()


def _month() -> str:
    return time.strftime("%Y-%m", time.gmtime())


# --- households & pairing (public keys only; no secrets touch the server) ---

def create_household() -> str:
    hid = "hh_" + secrets.token_hex(6)
    conn = _connect()
    try:
        conn.execute("INSERT INTO households(id,tier,created) VALUES(?,?,?)",
                     (hid, "free", _now()))
        conn.commit()
        return hid
    finally:
        conn.close()


def get_tier(household_id: str) -> str:
    conn = _connect()
    try:
        row = conn.execute("SELECT tier FROM households WHERE id=?", (household_id,)).fetchone()
        return row["tier"] if row else "free"
    finally:
        conn.close()


def set_tier(household_id: str, tier: str, source: str = "revenuecat") -> bool:
    if tier not in QUOTAS:
        return False
    conn = _connect()
    try:
        cur = conn.execute("UPDATE households SET tier=? WHERE id=?", (tier, household_id))
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


def open_pairing(household_id: str, manager_pubkey: str) -> dict[str, Any] | None:
    if not manager_pubkey or len(manager_pubkey) > 200:
        return None
    conn = _connect()
    try:
        if not conn.execute("SELECT 1 FROM households WHERE id=?",
                            (household_id,)).fetchone():
            return None
        code = "".join(secrets.choice("ABCDEFGHJKMNPQRSTUVWXYZ23456789") for _ in range(6))
        conn.execute("INSERT INTO pairings(code,household_id,manager_pubkey,status,"
                     "created,expires) VALUES(?,?,?,?,?,?)",
                     (code, household_id, manager_pubkey[:200], "open",
                      _now(), _now() + PAIR_TTL_S))
        conn.commit()
        return {"pairing_code": code, "expires_in_s": PAIR_TTL_S}
    finally:
        conn.close()


def complete_pairing(code: str, senior_pubkey: str, senior_id: str) -> dict[str, Any] | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM pairings WHERE code=?", (code.upper(),)).fetchone()
        if not row or row["status"] != "open" or row["expires"] < _now():
            return None
        conn.execute("UPDATE pairings SET senior_pubkey=?, senior_id=?, status='paired'"
                     " WHERE code=?", (senior_pubkey[:200], senior_id[:64], code.upper()))
        conn.commit()
        return {"household_id": row["household_id"], "manager_pubkey": row["manager_pubkey"]}
    finally:
        conn.close()


# --- blind relay: opaque blobs in, opaque blobs out ---

def push_blob(household_id: str, sender: str, nonce: str, ciphertext: str) -> int | None:
    if not ciphertext or len(ciphertext) > 200_000 or sender not in ("senior", "manager"):
        return None
    conn = _connect()
    try:
        if not conn.execute("SELECT 1 FROM households WHERE id=?",
                            (household_id,)).fetchone():
            return None
        cur = conn.execute("INSERT INTO blobs(household_id,sender,nonce,ciphertext,created)"
                           " VALUES(?,?,?,?,?)",
                           (household_id, sender, nonce[:100], ciphertext, _now()))
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def pull_blobs(household_id: str, since_id: int = 0, limit: int = 100) -> list[dict]:
    conn = _connect()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT id,sender,nonce,ciphertext,created FROM blobs WHERE household_id=?"
            " AND id>? ORDER BY id LIMIT ?", (household_id, since_id, min(limit, 200)))]
    finally:
        conn.close()


# --- screening on hashes: raw numbers never leave the phone ---

def hash_number(household_id: str, e164: str) -> str:
    salt = "kavach|" + household_id
    return hashlib.sha256((salt + e164.strip()).encode()).hexdigest()


def block_number(household_id: str, number_hash: str, label: str = "",
                 action: str = "block") -> bool:
    if len(number_hash) != 64 or action not in ("block", "silence", "allow"):
        return False
    conn = _connect()
    try:
        conn.execute("INSERT OR REPLACE INTO blocklist(household_id,number_hash,label,"
                     "action,created) VALUES(?,?,?,?,?)",
                     (household_id, number_hash, label[:120], action, _now()))
        conn.commit()
        return True
    finally:
        conn.close()


def unblock_number(household_id: str, number_hash: str) -> bool:
    conn = _connect()
    try:
        cur = conn.execute("DELETE FROM blocklist WHERE household_id=? AND number_hash=?",
                           (household_id, number_hash))
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


def lookup_number(household_id: str, number_hash: str) -> dict[str, Any]:
    conn = _connect()
    try:
        row = conn.execute("SELECT action,label FROM blocklist WHERE household_id=?"
                           " AND number_hash=?", (household_id, number_hash)).fetchone()
    finally:
        conn.close()
    if row:
        return {"action": row["action"], "reason": row["label"] or "household list",
                "source": "household"}
    return {"action": "allow", "reason": "not on any list", "source": "none"}


# --- consent: every manager power is lent by the senior, revocable in one tap ---

CAPABILITIES = ["screen_calls", "forward_sms", "remote_cut", "cloud_brain", "share_routines"]


def set_consent(household_id: str, senior_id: str, capabilities: dict[str, bool],
                granted_by: str) -> bool:
    clean = {k: bool(capabilities.get(k, False)) for k in CAPABILITIES}
    conn = _connect()
    try:
        conn.execute("INSERT OR REPLACE INTO consent(household_id,senior_id,capabilities,"
                     "granted_by,revoked,created,updated) VALUES(?,?,?,?,?,?,?)",
                     (household_id, senior_id, json.dumps(clean), granted_by[:64], 0,
                      _now(), _now()))
        conn.commit()
        return True
    finally:
        conn.close()


def revoke_consent(household_id: str, senior_id: str) -> bool:
    conn = _connect()
    try:
        cur = conn.execute("UPDATE consent SET revoked=1, updated=? WHERE household_id=?"
                           " AND senior_id=?", (_now(), household_id, senior_id))
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


def get_consent(household_id: str, senior_id: str) -> dict[str, Any]:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM consent WHERE household_id=? AND senior_id=?",
                           (household_id, senior_id)).fetchone()
    finally:
        conn.close()
    if not row or row["revoked"]:
        return {"granted": False, "capabilities": dict.fromkeys(CAPABILITIES, False)}
    return {"granted": True, "capabilities": json.loads(row["capabilities"]),
            "granted_by": row["granted_by"], "updated": row["updated"]}


def may(capability: str, household_id: str, senior_id: str) -> bool:
    if capability not in CAPABILITIES:
        return False
    return bool(get_consent(household_id, senior_id).get("capabilities", {}).get(capability))


# --- remote commands: manager intent, senior device acts (consent-gated) ---

COMMAND_TYPES = ["cut_call", "sound_siren", "show_message"]


def queue_command(household_id: str, target: str, type_: str,
                  payload_cipher: str = "") -> dict[str, Any] | None:
    if type_ not in COMMAND_TYPES or target not in ("senior", "manager"):
        return None
    conn = _connect()
    try:
        cur = conn.execute("INSERT INTO commands(household_id,target,type,payload_cipher,"
                           "status,created) VALUES(?,?,?,?,?,?)",
                           (household_id, target, type_, payload_cipher[:5000],
                            "queued", _now()))
        conn.commit()
        return {"command_id": int(cur.lastrowid)}
    finally:
        conn.close()


def pending_commands(household_id: str, target: str) -> list[dict]:
    conn = _connect()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT id,type,payload_cipher,created FROM commands WHERE household_id=?"
            " AND target=? AND status='queued' ORDER BY id LIMIT 20",
            (household_id, target))]
    finally:
        conn.close()


def ack_command(command_id: int) -> bool:
    conn = _connect()
    try:
        cur = conn.execute("UPDATE commands SET status='delivered', delivered=? WHERE id=?"
                           " AND status='queued'", (_now(), command_id))
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


# --- cloud brain with quotas: paid tiers fund the inference ---

def brain_ask(household_id: str, snippet: str) -> dict[str, Any]:
    """Server-side verdict over an already-scrubbed snippet. Quota-gated by tier."""
    tier = get_tier(household_id)
    month = _month()
    conn = _connect()
    try:
        row = conn.execute("SELECT brain_calls FROM usage WHERE household_id=? AND month=?",
                           (household_id, month)).fetchone()
        used = row["brain_calls"] if row else 0
        if used >= QUOTAS.get(tier, 20):
            return {"ok": False, "error": "quota_exceeded", "tier": tier,
                    "summary": "Monthly cloud-brain quota used up. Upgrade for more."}
        conn.execute("INSERT INTO usage(household_id,month,brain_calls) VALUES(?,?,1)"
                     " ON CONFLICT(household_id,month) DO UPDATE SET brain_calls="
                     "brain_calls+1", (household_id, month))
        conn.commit()
    finally:
        conn.close()
    signals = redflags.extract_signals(snippet[:2000])
    verdict, conf, reasons = redflags.score_verdict(signals, snippet[:2000])
    return {"ok": True, "tier": tier, "verdict": verdict, "confidence": conf,
            "reasons": reasons, "guidance": redflags.GUIDANCE[verdict],
            "used": used + 1, "quota": QUOTAS.get(tier, 20)}
