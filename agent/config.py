"""Shared config for Kavach — voice guardian + scam shield for seniors."""
from __future__ import annotations

import os

APP_NAME = "kavach"
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
#: OpenCode Zen (OpenAI-compatible gateway).
#: Server-side only — the key never leaves the relay, never ships in the APK.
#: NOTE: Zen FREE-tier ids only work from inside OpenCode itself; the relay
#: must use a paid/billed model id. Misconfigured = silent offline fallback.
ZEN_API_KEY = os.getenv("OPENCODE_API_KEY", "") or os.getenv("ZEN_API_KEY", "")
ZEN_MODEL = os.getenv("ZEN_MODEL", "muse-spark-1.3")
ZEN_BASE = os.getenv("ZEN_BASE", "https://opencode.ai/zen/v1").rstrip("/")
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "8000"))
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "30"))
ALLOWED_ORIGINS = [o.strip() for o in os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:7860").split(",") if o.strip()]
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "kavach.db"))
MCP_SPEC_VERSION = "2025-11-25"
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()
DEFAULT_SENIOR_ID = os.getenv("KAVACH_SENIOR_ID", "demo-senior")


def llm_status() -> dict:
    """Which LLM providers are configured (no secrets leaked)."""
    if ZEN_API_KEY:
        mode = "zen"
    elif GEMINI_API_KEY:
        mode = "gemini"
    elif GROQ_API_KEY:
        mode = "groq"
    else:
        mode = "offline-stub"
    return {"mode": mode, "zen_configured": bool(ZEN_API_KEY),
            "gemini_configured": bool(GEMINI_API_KEY),
            "groq_configured": bool(GROQ_API_KEY),
            "zen_model": ZEN_MODEL,
            "gemini_model": GEMINI_MODEL, "groq_model": GROQ_MODEL}
