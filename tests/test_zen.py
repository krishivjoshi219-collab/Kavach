"""Zen narration: free-model first, silent fallback always. Key never in repo."""
from __future__ import annotations

import os

from agent import config, kavach_agent


def test_offline_fallback_with_no_keys(monkeypatch):
    for var in ("OPENCODE_API_KEY", "ZEN_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    import importlib
    importlib.reload(config)
    importlib.reload(kavach_agent)
    try:
        assert kavach_agent._llm_narrate("sys", "hello") == ("offline-stub", "")
        assert config.llm_status()["mode"] == "offline-stub"
    finally:
        importlib.reload(config)
        importlib.reload(kavach_agent)


def test_zen_first_with_mocked_gateway(monkeypatch):
    monkeypatch.setenv("OPENCODE_API_KEY", "test-key-not-real")
    import importlib
    importlib.reload(config)
    importlib.reload(kavach_agent)

    calls = {}

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "  Ruko, beta.  "}}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        calls["url"] = url
        calls["model"] = json["model"]
        assert headers["Authorization"] == "Bearer test-key-not-real"
        return FakeResp()

    import httpx
    monkeypatch.setattr(httpx, "post", fake_post)
    try:
        provider, text = kavach_agent._llm_narrate("sys", "scam call about OTP")
        assert provider == "zen" and text == "Ruko, beta."
        assert calls["url"].endswith("/chat/completions")
        assert config.llm_status()["mode"] == "zen"
    finally:
        monkeypatch.delenv("OPENCODE_API_KEY", raising=False)
        importlib.reload(config)
        importlib.reload(kavach_agent)


def test_status_leaks_no_secrets():
    status = config.llm_status()
    for var in ("OPENCODE_API_KEY", "ZEN_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"):
        secret = os.getenv(var, "")
        if secret:
            assert secret not in str(status)
