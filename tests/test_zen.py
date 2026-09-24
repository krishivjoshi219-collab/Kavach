"""Zen narration: free-model first, silent fallback always. Key never in repo.

No importlib.reload: reload() re-executes config.py (clobbering the
monkeypatched DB_PATH mid-suite → writes could hit real ./kavach.db) and
re-snapshots kavach_agent's by-value config imports. Attribute patching is
surgical and race-free.
"""
from __future__ import annotations

import os

from agent import config, kavach_agent


def test_offline_fallback_with_no_keys(monkeypatch):
    for attr in ("ZEN_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"):
        monkeypatch.setattr(config, attr, "")
        monkeypatch.setattr(kavach_agent, attr, "")
    assert kavach_agent._llm_narrate("sys", "hello") == ("offline-stub", "")
    assert config.llm_status()["mode"] == "offline-stub"


def test_zen_first_with_mocked_gateway(monkeypatch):
    monkeypatch.setattr(config, "ZEN_API_KEY", "test-key-not-real")
    monkeypatch.setattr(kavach_agent, "ZEN_API_KEY", "test-key-not-real")

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
    provider, text = kavach_agent._llm_narrate("sys", "scam call about OTP")
    assert provider == "zen" and text == "Ruko, beta."
    assert calls["url"].endswith("/chat/completions")
    assert config.llm_status()["mode"] == "zen"


def test_status_leaks_no_secrets():
    status = config.llm_status()
    for var in ("OPENCODE_API_KEY", "ZEN_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"):
        secret = os.getenv(var, "")
        if secret:
            assert secret not in str(status)
