"""SQLite domain model: seniors, contacts, incidents, check-ins, routines, alerts, flows."""
from __future__ import annotations

import json
import os
import secrets
import sqlite3
import time
from typing import Any

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS seniors(
  id TEXT PRIMARY KEY, name TEXT NOT NULL, language TEXT NOT NULL DEFAULT 'en',
  notes TEXT NOT NULL DEFAULT '', created REAL NOT NULL, updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS safe_contacts(
  id INTEGER PRIMARY KEY AUTOINCREMENT, senior_id TEXT NOT NULL, label TEXT NOT NULL,
  detail TEXT NOT NULL DEFAULT '', kind TEXT NOT NULL DEFAULT 'family', created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS incidents(
  id INTEGER PRIMARY KEY AUTOINCREMENT, senior_id TEXT NOT NULL, status TEXT NOT NULL,
  channel TEXT NOT NULL DEFAULT 'call', caller_claim TEXT NOT NULL DEFAULT '',
  transcript TEXT NOT NULL DEFAULT '', red_flags TEXT NOT NULL DEFAULT '[]',
  verdict TEXT NOT NULL DEFAULT 'UNCERTAIN', confidence REAL NOT NULL DEFAULT 0,
  created REAL NOT NULL, updated REAL NOT NULL, closed REAL);
CREATE TABLE IF NOT EXISTS checkins(
  id INTEGER PRIMARY KEY AUTOINCREMENT, senior_id TEXT NOT NULL, kind TEXT NOT NULL,
  note TEXT NOT NULL DEFAULT '', mood TEXT NOT NULL DEFAULT 'ok', created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS routines(
  id INTEGER PRIMARY KEY AUTOINCREMENT, senior_id TEXT NOT NULL, label TEXT NOT NULL,
  expected_time TEXT NOT NULL DEFAULT '', window_min INTEGER NOT NULL DEFAULT 60,
  last_confirmed REAL, streak INTEGER NOT NULL DEFAULT 0, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS alerts(
  id INTEGER PRIMARY KEY AUTOINCREMENT, senior_id TEXT NOT NULL,
  incident_id INTEGER, kind TEXT NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft', confirm_code TEXT NOT NULL DEFAULT '',
  created REAL NOT NULL, sent_at REAL);
CREATE TABLE IF NOT EXISTS flows(
  session_id TEXT PRIMARY KEY, kind TEXT NOT NULL, stage TEXT NOT NULL,
  incident_id INTEGER, data TEXT NOT NULL DEFAULT '{}', updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS sessions(
  id TEXT PRIMARY KEY, history TEXT NOT NULL, updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS family_challenges(
  id TEXT PRIMARY KEY, senior_id TEXT NOT NULL, claim_who TEXT NOT NULL DEFAULT '',
  question TEXT NOT NULL DEFAULT '', nonce TEXT NOT NULL DEFAULT '',
  state TEXT NOT NULL DEFAULT 'pending', decision TEXT NOT NULL DEFAULT '',
  created REAL NOT NULL, expires REAL NOT NULL, resolved REAL);
"""


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(config.DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _now() -> float:
    return time.time()


def ensure_seed(senior_id: str = "demo-senior") -> dict[str, Any]:
    """Create the demo household on first run. Fictional data, clearly labeled."""
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM seniors WHERE id=?", (senior_id,)).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO seniors(id,name,language,notes,created,updated)"
                " VALUES(?,?,?,?,?,?)",
                (senior_id, "Asha", "en",
                 "Demo household (fictional). Speaks English, mornings are routine.",
                 _now(), _now()))
            for label, detail, kind in [
                    ("Priya (daughter)", "+91-98XXX-XXX01", "family"),
                    ("Family doctor — Dr. Rao", "+91-98XXX-XXX02", "family"),
                    ("HDFC Bank official helpline", "1800-XXX-XXXX (printed on card)", "bank")]:
                conn.execute(
                    "INSERT INTO safe_contacts(senior_id,label,detail,kind,created)"
                    " VALUES(?,?,?,?,?)", (senior_id, label, detail, kind, _now()))
            for label, expected in [("Breakfast", "08:30"), ("Morning walk", "07:00"),
                                    ("Evening medicines", "20:00")]:
                conn.execute(
                    "INSERT INTO routines(senior_id,label,expected_time,created)"
                    " VALUES(?,?,?,?)", (senior_id, label, expected, _now()))
            conn.commit()
            row = conn.execute("SELECT * FROM seniors WHERE id=?", (senior_id,)).fetchone()
        return dict(row)
    finally:
        conn.close()


def get_senior(senior_id: str) -> dict[str, Any] | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM seniors WHERE id=?", (senior_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_contacts(senior_id: str) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        return [dict(r) for r in
                conn.execute("SELECT * FROM safe_contacts WHERE senior_id=? ORDER BY id",
                             (senior_id,))]
    finally:
        conn.close()


def find_contact(senior_id: str, text: str) -> dict[str, Any] | None:
    """Match a caller description against the safe list (name or detail fragment)."""
    text = text.lower()
    for c in list_contacts(senior_id):
        label = c["label"].lower()
        first = label.split()[0].strip("()")
        if first and len(first) > 2 and first in text:
            return c
        if c["detail"] and c["detail"].lower() in text and len(c["detail"]) > 4:
            return c
    return None


def create_incident(senior_id: str, channel: str, caller_claim: str,  # noqa: PLR0913, vcc:ignore
                    transcript: str, red_flags: list[dict], verdict: str,
                    confidence: float) -> int:
    conn = _connect()
    try:
        cur = conn.execute(
            "INSERT INTO incidents(senior_id,status,channel,caller_claim,transcript,"
            "red_flags,verdict,confidence,created,updated) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (senior_id, "verdict", channel, caller_claim[:500], transcript[-4000:],
             json.dumps(red_flags), verdict, confidence, _now(), _now()))
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


INCIDENT_COLUMNS = {
    "senior_id", "status", "channel", "caller_claim", "transcript",
    "red_flags", "verdict", "confidence", "created", "updated", "closed",
}


def update_incident(incident_id: int, **fields: Any) -> None:
    fields["updated"] = _now()
    invalid = set(fields) - INCIDENT_COLUMNS
    if invalid:
        raise ValueError(f"Invalid incident fields: {invalid}")
    sets = ", ".join(f"{k}=?" for k in fields)
    conn = _connect()
    try:
        conn.execute(f"UPDATE incidents SET {sets} WHERE id=?",  # noqa: vcc:ignore
                     (*fields.values(), incident_id))
        conn.commit()
    finally:
        conn.close()


def get_incident(incident_id: int) -> dict[str, Any] | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_incidents(senior_id: str, limit: int = 20) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM incidents WHERE senior_id=? ORDER BY id DESC LIMIT ?",
            (senior_id, limit))]
    finally:
        conn.close()


def add_checkin(senior_id: str, kind: str, note: str, mood: str = "ok") -> int:
    conn = _connect()
    try:
        cur = conn.execute(
            "INSERT INTO checkins(senior_id,kind,note,mood,created) VALUES(?,?,?,?,?)",
            (senior_id, kind, note[:1000], mood, _now()))
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_checkins(senior_id: str, limit: int = 10) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM checkins WHERE senior_id=? ORDER BY id DESC LIMIT ?",
            (senior_id, limit))]
    finally:
        conn.close()


def list_routines(senior_id: str) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM routines WHERE senior_id=? ORDER BY id", (senior_id,))]
    finally:
        conn.close()


def confirm_routine(routine_id: int) -> None:
    conn = _connect()
    try:
        conn.execute("UPDATE routines SET last_confirmed=?, streak=streak+1 WHERE id=?",
                     (_now(), routine_id))
        conn.commit()
    finally:
        conn.close()


def draft_alert(senior_id: str, kind: str, title: str, body: str,
                incident_id: int | None = None) -> dict[str, Any]:
    code = "".join(secrets.choice("ABCDEFGHJKMNPQRSTUVWXYZ23456789") for _ in range(6))
    conn = _connect()
    try:
        cur = conn.execute(
            "INSERT INTO alerts(senior_id,incident_id,kind,title,body,status,"
            "confirm_code,created) VALUES(?,?,?,?,?,?,?,?)",
            (senior_id, incident_id, kind, title[:200], body[:2000],
             "pending_confirm", code, _now()))
        conn.commit()
        return {"id": int(cur.lastrowid), "confirm_code": code}
    finally:
        conn.close()


def get_pending_alert(senior_id: str) -> dict[str, Any] | None:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM alerts WHERE senior_id=? AND status='pending_confirm'"
            " ORDER BY id DESC LIMIT 1", (senior_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def confirm_alert(alert_id: int, code: str) -> bool:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM alerts WHERE id=?", (alert_id,)).fetchone()
        if not row or row["status"] != "pending_confirm":
            return False
        if row["confirm_code"].upper() != code.strip().upper():
            return False
        conn.execute("UPDATE alerts SET status='sent', sent_at=? WHERE id=?",
                     (_now(), alert_id))
        conn.commit()
        return True
    finally:
        conn.close()


def list_alerts(senior_id: str, limit: int = 20) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM alerts WHERE senior_id=? ORDER BY id DESC LIMIT ?",
            (senior_id, limit))]
    finally:
        conn.close()


def set_flow(session_id: str, kind: str, stage: str,
             incident_id: int | None = None, data: dict | None = None) -> None:
    conn = _connect()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO flows(session_id,kind,stage,incident_id,data,updated)"
            " VALUES(?,?,?,?,?,?)",
            (session_id, kind, stage, incident_id, json.dumps(data or {}), _now()))
        conn.commit()
    finally:
        conn.close()


def get_flow(session_id: str) -> dict[str, Any] | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM flows WHERE session_id=?", (session_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["data"] = json.loads(d["data"] or "{}")
        return d
    finally:
        conn.close()


def clear_flow(session_id: str) -> None:
    conn = _connect()
    try:
        conn.execute("DELETE FROM flows WHERE session_id=?", (session_id,))
        conn.commit()
    finally:
        conn.close()


def create_challenge(senior_id: str, claim_who: str, question: str, ttl_s: int = 300) -> dict[str, Any]:
    import uuid as _uuid
    cid = "ch_" + _uuid.uuid4().hex[:12]
    nonce = secrets.token_urlsafe(24)
    now = _now()
    conn = _connect()
    try:
        conn.execute("INSERT INTO family_challenges(id,senior_id,claim_who,question,nonce,"
                     "state,created,expires) VALUES(?,?,?,?,?,?,?,?)",
                     (cid, senior_id, claim_who[:200], question[:500], nonce,
                      "pending", now, now + ttl_s))
        conn.commit()
    finally:
        conn.close()
    return {"id": cid, "nonce": nonce, "state": "pending", "expires_in_s": ttl_s}


def get_challenge(challenge_id: str) -> dict[str, Any] | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM family_challenges WHERE id=?", (challenge_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        if d["state"] == "pending" and d["expires"] < _now():
            conn.execute("UPDATE family_challenges SET state='expired' WHERE id=?", (challenge_id,))
            conn.commit()
            d["state"] = "expired"
        return d
    finally:
        conn.close()


def respond_challenge(challenge_id: str, decision: str) -> dict[str, Any] | None:
    decision = decision.upper()
    if decision not in ("APPROVE", "DENY", "NEED_HELP"):
        return None
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM family_challenges WHERE id=?", (challenge_id,)).fetchone()
        if not row or row["state"] != "pending" or row["expires"] < _now():
            return None
        conn.execute("UPDATE family_challenges SET state='resolved', decision=?, resolved=? WHERE id=?",
                     (decision, _now(), challenge_id))
        conn.commit()
        out = dict(conn.execute("SELECT * FROM family_challenges WHERE id=?", (challenge_id,)).fetchone())
        return out
    finally:
        conn.close()


def load_history(session_id: str, limit_turns: int = 12) -> list[dict]:
    conn = _connect()
    try:
        row = conn.execute("SELECT history FROM sessions WHERE id=?", (session_id,)).fetchone()
    finally:
        conn.close()
    if not row:
        return []
    try:
        return json.loads(row["history"])[-limit_turns:]
    except (json.JSONDecodeError, TypeError):
        return []


def save_turn(session_id: str, role: str, content: str) -> None:
    hist = load_history(session_id, limit_turns=50)
    hist.append({"role": role, "content": content[:2000]})
    hist = hist[-50:]
    conn = _connect()
    try:
        conn.execute("INSERT OR REPLACE INTO sessions(id,history,updated) VALUES(?,?,?)",
                     (session_id, json.dumps(hist), _now()))
        conn.commit()
    finally:
        conn.close()
