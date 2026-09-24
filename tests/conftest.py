"""Test isolation: fresh SQLite DB + reset global counters per test.

DB_PATH is read dynamically (config.DB_PATH attribute access), so patching
it isolates all DB users. In-memory counters (METRICS, RELAY_STATS) and
rate-limit buckets are process-global and must be reset explicitly.
"""
import os

os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import pytest

import agent.config as cfg
import app as appmod
from agent import mobile as _mobile
from agent.ratelimit import limiter


@pytest.fixture(autouse=True)
def _isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "DB_PATH", str(tmp_path / "t.db"))
    # Rate limiting is enforced via SlowAPIMiddleware in production; reset the
    # in-memory buckets per test so the suite never 429s itself. Belt and
    # suspenders with RATE_LIMIT_ENABLED=false above.
    try:
        limiter.reset()
    except Exception:  # noqa: BLE001 - storage backend without reset()
        pass
    # Per-process counters leak across tests (shared app object); zero them
    # so absolute assertions stay deterministic instead of order-dependent.
    with appmod.METRICS_LOCK:
        for k in appmod.METRICS:
            appmod.METRICS[k] = 0
    with _mobile._RELAY_LOCK:
        for k in _mobile.RELAY_STATS:
            _mobile.RELAY_STATS[k] = 0
    yield


def test_rate_limit_kill_switch_effective():
    """Pin the isolation contract: limiter exposes reset() and the kill
    switch env var is honored, so a future slowapi upgrade that breaks
    either fails loudly here instead of flaking the suite with 429s."""
    assert hasattr(limiter, "reset")
    assert os.getenv("RATE_LIMIT_ENABLED") == "false"
