"""Every test gets a fresh isolated SQLite DB (config.DB_PATH is read dynamically)."""
import pytest

import agent.config as cfg


@pytest.fixture(autouse=True)
def _isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "DB_PATH", str(tmp_path / "t.db"))
