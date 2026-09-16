"""SQLite session memory: state across turns/sessions (Alexa creative criterion)."""
from __future__ import annotations

import json
import os
import sqlite3
import time

from . import config


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(config.DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS sessions(
      id TEXT PRIMARY KEY, history TEXT NOT NULL, updated REAL NOT NULL)""")
    return conn


def load_history(session_id: str, limit_turns: int = 12) -> list[dict]:
    conn = _connect()
    try:
        row = conn.execute("SELECT history FROM sessions WHERE id=?", (session_id,)).fetchone()
    finally:
        conn.close()
    if not row:
        return []
    try:
        hist = json.loads(row[0])
    except json.JSONDecodeError:
        return []
    return hist[-limit_turns:]


def save_turn(session_id: str, role: str, content: str) -> None:
    hist = load_history(session_id, limit_turns=50)
    hist.append({"role": role, "content": content[:4000]})
    hist = hist[-50:]
    conn = _connect()
    try:
        conn.execute("INSERT OR REPLACE INTO sessions(id,history,updated) VALUES(?,?,?)",
                     (session_id, json.dumps(hist), time.time()))
        conn.commit()
    finally:
        conn.close()
