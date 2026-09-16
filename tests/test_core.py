from agent import tools_ops
from agent.memory import load_history, save_turn


def test_verify_good():
    r = tools_ops.verify_code_file(code="def f():\n    return 1\n")
    assert r.ok


def test_verify_bad():
    r = tools_ops.verify_code_file(code="def f(:\n pass\n")
    assert not r.ok


def test_blocked_command():
    r = tools_ops.execute_command("rm -rf /")
    assert not r.ok and "blocked" in r.summary.lower()


def test_pipeline_and_triage():
    st = tools_ops.get_pipeline_status("demo-web")
    assert st.ok and st.data["status"] == "failed"
    heal = tools_ops.triage_and_heal_incident(st.data["tail"])
    assert heal.ok and "diff" in heal.data


def test_memory_roundtrip(tmp_path, monkeypatch):
    import agent.config as cfg
    monkeypatch.setattr(cfg, "DB_PATH", str(tmp_path / "t.db"))
    save_turn("s1", "user", "hello")
    assert len(load_history("s1")) == 1


def test_agent_turn_offline(monkeypatch, tmp_path):
    import agent.config as cfg
    monkeypatch.setattr(cfg, "DB_PATH", str(tmp_path / "t2.db"))
    monkeypatch.setattr(cfg, "GEMINI_API_KEY", "")
    monkeypatch.setattr(cfg, "GROQ_API_KEY", "")
    from agent.ops_agent import run_agent_turn
    out = run_agent_turn("why did my deploy fail?", "s9")
    assert out["cards"] and out["spoken"]
    assert any("get_pipeline_status" in t for t in out["tools"])
