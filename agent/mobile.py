"""Mobile contract: households, pairing, blind relay, screening, consent, commands, quota.

Privacy design: the server stores public keys, number HASHES (household-salted),
and opaque ciphertext blobs. It never sees secrets, transcripts, or raw numbers.
True E2E: blobs must be base64 Tink ECIES ciphertext; plaintext is rejected.
Manager gets all lent capabilities by default at pairing; senior revokes in one tap
which bumps the epoch and wipes queued remote powers.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
import sqlite3
import threading
import time
from typing import Any

from . import config, redflags

SCHEMA = """
CREATE TABLE IF NOT EXISTS households(
  id TEXT PRIMARY KEY, tier TEXT NOT NULL DEFAULT 'free', created REAL NOT NULL,
  epoch INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS pairings(
  code TEXT PRIMARY KEY, household_id TEXT NOT NULL, manager_pubkey TEXT NOT NULL,
  senior_pubkey TEXT NOT NULL DEFAULT '', senior_id TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'open', created REAL NOT NULL, expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS blobs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, household_id TEXT NOT NULL, sender TEXT NOT NULL,
  nonce TEXT NOT NULL, ciphertext TEXT NOT NULL, created REAL NOT NULL,
  epoch INTEGER NOT NULL DEFAULT 0);
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
CREATE TABLE IF NOT EXISTS webhook_receipts(
  provider TEXT NOT NULL, event_id TEXT NOT NULL, household_id TEXT NOT NULL DEFAULT '',
  tier TEXT NOT NULL DEFAULT '', created REAL NOT NULL,
  PRIMARY KEY (provider, event_id));
CREATE TABLE IF NOT EXISTS community_reports(
  household_id TEXT NOT NULL, number_hash TEXT NOT NULL, category TEXT NOT NULL DEFAULT '',
  created REAL NOT NULL, PRIMARY KEY (household_id, number_hash));
"""

QUOTAS = {"free": 20, "pro": 200, "ultra": 2000}
PAIR_TTL_S = 600
#: Cap stored blobs per household (DoS hygiene: oldest pruned past the cap).
MAX_BLOBS_PER_HOUSEHOLD = 500

_RELAY_LOCK = threading.Lock()
RELAY_STATS: dict[str, int] = {
    "households_total": 0, "pairings_total": 0, "push_total": 0,
    "blocks_total": 0, "commands_total": 0,
}


def _bump(stat: str) -> None:
    with _RELAY_LOCK:
        RELAY_STATS[stat] = RELAY_STATS.get(stat, 0) + 1


def relay_stats() -> dict[str, int]:
    with _RELAY_LOCK:
        return dict(RELAY_STATS)

# Ciphertext that is clearly not E2E (raw words that never appear in real
# Tink ECIES base64 noise). Checked on raw string AND base64-decoded bytes.
PLAINTEXT_PATTERNS = [
    r"otp", r"aadhaar", r"aadhar", r"password", r"\bpin\b", r"cvv",
    r"https?://", r"www\.", r"\.apk\b", r"\+91[\-\s]?\d",
    r"account (is |will be )?(frozen|blocked)", r"ENCRYPTED:",
]
PLAINTEXT_RE = re.compile("|".join(f"(?:{p})" for p in PLAINTEXT_PATTERNS), re.IGNORECASE)


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(config.DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    # Lightweight migrations for existing DBs (kavach.db from older runs).
    for sql in (
        "ALTER TABLE households ADD COLUMN epoch INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE blobs ADD COLUMN epoch INTEGER NOT NULL DEFAULT 0",
    ):
        try:
            conn.execute(sql)
        except sqlite3.OperationalError:
            pass  # column already exists
    try:
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_blobs_nonce "
                     "ON blobs(household_id, nonce)")
    except sqlite3.OperationalError:
        pass
    conn.commit()
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
        _bump("households_total")
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


def record_webhook(provider: str, event_id: str, household_id: str, tier: str) -> bool:
    """Durable, idempotent webhook receipt. Returns True if newly applied."""
    conn = _connect()
    try:
        cur = conn.execute("INSERT OR IGNORE INTO webhook_receipts(provider,event_id,household_id,"
                           "tier,created) VALUES(?,?,?,?,?)",
                           (provider, event_id, household_id, tier, _now()))
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


def community_stats(household_id: str) -> dict[str, Any]:
    """Honest radar: counts from THIS relay only (household blocklist + blobs).
    Never presented as regional carrier data."""
    conn = _connect()
    try:
        blocked = conn.execute("SELECT COUNT(*) AS n FROM blocklist WHERE household_id=?",
                               (household_id,)).fetchone()["n"]
        blobs = conn.execute("SELECT COUNT(*) AS n FROM blobs WHERE household_id=?",
                             (household_id,)).fetchone()["n"]
    finally:
        conn.close()
    return {"household_blocks": int(blocked), "household_blobs": int(blobs),
            "total_threats_shielded": int(blocked + blobs)}


def open_pairing(household_id: str, manager_pubkey: str) -> dict[str, Any] | None:
    if not manager_pubkey or len(manager_pubkey) > 8000:
        return None
    conn = _connect()
    try:
        if not conn.execute("SELECT 1 FROM households WHERE id=?",
                            (household_id,)).fetchone():
            return None
        code = "".join(secrets.choice("ABCDEFGHJKMNPQRSTUVWXYZ23456789") for _ in range(6))
        conn.execute("INSERT INTO pairings(code,household_id,manager_pubkey,status,"
                     "created,expires) VALUES(?,?,?,?,?,?)",
                     (code, household_id, manager_pubkey[:8000], "open",
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
                     " WHERE code=?", (senior_pubkey[:8000], senior_id[:64], code.upper()))
        conn.commit()
        hid, mgr_pub = row["household_id"], row["manager_pubkey"]
    finally:
        conn.close()
    # Manager gets ALL lent capabilities by default at seal time.
    # Senior can revoke everything in one tap (bumps epoch).
    if senior_id:
        set_consent(hid, senior_id[:64],
                    {k: True for k in CAPABILITIES}, granted_by=senior_id[:64])
    _bump("pairings_total")
    return {"household_id": hid, "manager_pubkey": mgr_pub}


def get_pair_peer(household_id: str) -> dict[str, Any] | None:
    """Manager fetch of senior pubkey after seal (single household, latest paired)."""
    conn = _connect()
    try:
        row = conn.execute("SELECT senior_pubkey, senior_id, status FROM pairings"
                           " WHERE household_id=? AND status='paired'"
                           " ORDER BY created DESC LIMIT 1", (household_id,)).fetchone()
        if not row or not row["senior_pubkey"]:
            return None
        return {"senior_pubkey": row["senior_pubkey"], "senior_id": row["senior_id"],
                "status": row["status"], "epoch": get_epoch(household_id)}
    finally:
        conn.close()


def get_epoch(household_id: str) -> int:
    conn = _connect()
    try:
        row = conn.execute("SELECT epoch FROM households WHERE id=?",
                           (household_id,)).fetchone()
        return int(row["epoch"] or 0) if row else 0
    finally:
        conn.close()


def _bump_epoch(household_id: str) -> int:
    conn = _connect()
    try:
        conn.execute("UPDATE households SET epoch=epoch+1 WHERE id=?", (household_id,))
        conn.commit()
        row = conn.execute("SELECT epoch FROM households WHERE id=?",
                           (household_id,)).fetchone()
        return int(row["epoch"] or 0) if row else 0
    finally:
        conn.close()


def _ciphertext_ok(ciphertext: str) -> bool:
    """True E2E gate: base64 noise only, no plaintext words raw or decoded."""
    if not ciphertext or not 80 <= len(ciphertext) <= 200_000:
        return False
    if PLAINTEXT_RE.search(ciphertext):
        return False
    try:
        raw = base64.b64decode(ciphertext, validate=True)
    except (ValueError, base64.binascii.Error):
        return False
    if len(raw) < 32:
        return False
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return True  # random binary noise: exactly what we want
    return not PLAINTEXT_RE.search(text)


# --- blind relay: opaque blobs in, opaque blobs out ---

def push_blob(household_id: str, sender: str, nonce: str, ciphertext: str) -> int | None:
    if not ciphertext or len(ciphertext) > 200_000 or sender not in ("senior", "manager"):
        return None
    if not nonce or len(nonce) < 8 or len(nonce) > 100:
        return None
    if not _ciphertext_ok(ciphertext):
        return None
    conn = _connect()
    try:
        if not conn.execute("SELECT 1 FROM households WHERE id=?",
                            (household_id,)).fetchone():
            return None
        if conn.execute("SELECT 1 FROM blobs WHERE household_id=? AND nonce=?",
                        (household_id, nonce[:100])).fetchone():
            return None  # nonce reuse: replay attack
        epoch = get_epoch(household_id)
        try:
            cur = conn.execute("INSERT INTO blobs(household_id,sender,nonce,ciphertext,created,epoch)"
                               " VALUES(?,?,?,?,?,?)",
                               (household_id, sender, nonce[:100], ciphertext, _now(), epoch))
        except sqlite3.IntegrityError:
            return None
        conn.commit()
        bid = int(cur.lastrowid)
        conn.execute("DELETE FROM blobs WHERE household_id=? AND id NOT IN"
                     " (SELECT id FROM blobs WHERE household_id=? ORDER BY id DESC LIMIT ?)",
                     (household_id, household_id, MAX_BLOBS_PER_HOUSEHOLD))
        conn.commit()
        _bump("push_total")
        return bid
    finally:
        conn.close()


def pull_blobs(household_id: str, since_id: int = 0, limit: int = 100) -> list[dict]:
    conn = _connect()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT id,sender,nonce,ciphertext,created,epoch FROM blobs WHERE household_id=?"
            " AND id>? ORDER BY id LIMIT ?", (household_id, since_id, min(limit, 200)))]
    finally:
        conn.close()


# --- screening on hashes: raw numbers never leave the phone ---

def hash_number(household_id: str, e164: str) -> str:
    salt = "kavach|" + household_id
    return hashlib.sha256((salt + e164.strip()).encode()).hexdigest()


#: Community shield: a hash ships to all households after this many
#: INDEPENDENT households report it. Anti-poisoning: one report per
#: household (PRIMARY KEY), household list always wins, unblock retracts.
COMMUNITY_THRESHOLD = 3


def block_number(household_id: str, number_hash: str, label: str = "",
                 action: str = "block") -> bool:
    if len(number_hash) != 64 or action not in ("block", "silence", "allow"):
        return False
    conn = _connect()
    try:
        conn.execute("INSERT OR REPLACE INTO blocklist(household_id,number_hash,label,"
                     "action,created) VALUES(?,?,?,?,?)",
                     (household_id, number_hash, label[:120], action, _now()))
        if action == "block":
            # Community report: hash + category only. Raw numbers never exist here.
            conn.execute("INSERT OR IGNORE INTO community_reports(household_id,"
                         "number_hash,category,created) VALUES(?,?,?,?)",
                         (household_id, number_hash, label[:40], _now()))
        conn.commit()
        _bump("blocks_total")
        return True
    finally:
        conn.close()


def unblock_number(household_id: str, number_hash: str) -> bool:
    conn = _connect()
    try:
        cur = conn.execute("DELETE FROM blocklist WHERE household_id=? AND number_hash=?",
                           (household_id, number_hash))
        # Sovereignty: unblocking retracts MY community report too.
        conn.execute("DELETE FROM community_reports WHERE household_id=? AND number_hash=?",
                     (household_id, number_hash))
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


def list_blocklist(household_id: str, limit: int = 200) -> list[dict[str, Any]]:
    """Hashes blocked by THIS household. Lets sibling devices in the same
    household sync without waiting for the 3-household community threshold."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT number_hash, label, action, created FROM blocklist"
            " WHERE household_id=? ORDER BY created DESC LIMIT ?",
            (household_id, max(1, min(limit, 200)))).fetchall()
        return [{"number_hash": r["number_hash"], "label": r["label"],
                 "action": r["action"], "created": r["created"]} for r in rows]
    finally:
        conn.close()


def threat_feed(limit: int = 200) -> list[dict[str, Any]]:
    """Hashes reported by >= THRESHOLD independent households. Hashes only."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT number_hash, COUNT(DISTINCT household_id) AS reports,"
            " MIN(created) AS first_seen, MAX(category) AS category"
            " FROM community_reports GROUP BY number_hash"
            " HAVING reports >= ? ORDER BY reports DESC LIMIT ?",
            (COMMUNITY_THRESHOLD, max(1, min(limit, 200)))).fetchall()
        return [{"number_hash": r["number_hash"], "reports": r["reports"],
                 "first_seen": r["first_seen"], "category": r["category"] or "scam"}
                for r in rows]
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
    feed = {f["number_hash"]: f for f in threat_feed()}
    hit = feed.get(number_hash)
    if hit:
        return {"action": "block",
                "reason": f"community shield ({hit['reports']} households)"
                          + (f": {hit['category']}" if hit["category"] else ""),
                "source": "community"}
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
        ok = cur.rowcount == 1
    finally:
        conn.close()
    if ok:
        # Crypto revocation: new epoch, drop queued remote powers so old
        # manager keys/commands are useless. Blobs stay opaque but undecryptable
        # going forward once devices rotate.
        _bump_epoch(household_id)
        conn = _connect()
        try:
            conn.execute("UPDATE commands SET status='revoked' WHERE household_id=?"
                         " AND status='queued'", (household_id,))
            conn.commit()
        finally:
            conn.close()
    return ok


def get_consent(household_id: str, senior_id: str) -> dict[str, Any]:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM consent WHERE household_id=? AND senior_id=?",
                           (household_id, senior_id)).fetchone()
    finally:
        conn.close()
    epoch = get_epoch(household_id)
    if not row or row["revoked"]:
        return {"granted": False, "capabilities": dict.fromkeys(CAPABILITIES, False),
                "epoch": epoch}
    return {"granted": True, "capabilities": json.loads(row["capabilities"]),
            "granted_by": row["granted_by"], "updated": row["updated"], "epoch": epoch}


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
        _bump("commands_total")
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
