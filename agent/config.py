"""Shared config for K-VoiceOps (no AWS, no credit card: Gemini/Groq free + HF + Pages)."""
from __future__ import annotations

import os

APP_NAME = "k-voiceops"
APP_VERSION = os.getenv("APP_VERSION", "0.2.0")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "8000"))
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "30"))
ALLOWED_ORIGINS = [o.strip() for o in os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:7860").split(",") if o.strip()]
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "voiceops.db"))
MCP_SPEC_VERSION = "2025-11-25"
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()


def llm_status() -> dict:
    """Which LLM providers are configured (no secrets leaked)."""
    if GEMINI_API_KEY:
        mode = "gemini"
    elif GROQ_API_KEY:
        mode = "groq"
    else:
        mode = "offline-stub"
    return {"mode": mode, "gemini_configured": bool(GEMINI_API_KEY),
            "groq_configured": bool(GROQ_API_KEY),
            "gemini_model": GEMINI_MODEL, "groq_model": GROQ_MODEL}
