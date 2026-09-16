"""ReAct-style agent loop with free-tier LLM (Gemini primary, Groq fallback, offline stub)."""
from __future__ import annotations

import re
from typing import Any

from . import tools_ops
from .config import GEMINI_API_KEY, GEMINI_MODEL, GROQ_API_KEY, GROQ_MODEL, MAX_INPUT_CHARS
from .memory import load_history, save_turn
from .prompts import SYSTEM_PROMPT


def sanitize(text: str) -> str:
    text = text[:MAX_INPUT_CHARS]
    # strip common prompt-injection directives
    text = re.sub(r"(?i)ignore (all )?previous instructions.*", "[filtered]", text)
    return text.strip()


def _llm_complete(prompt: str) -> tuple[str, str]:
    """Returns (provider, text). Never raises: falls back to offline stub."""
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL)
            resp = model.generate_content(prompt, request_options={"timeout": 40})
            return "gemini", (resp.text or "").strip()[:3000]
        except Exception as e:  # noqa: BLE001
            err = str(e)[:200]
        else:
            err = ""
    else:
        err = "no GEMINI_API_KEY"
    if GROQ_API_KEY:
        try:
            import httpx
            r = httpx.post("https://api.groq.com/openai/v1/chat/completions",
                           headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                           json={"model": GROQ_MODEL,
                                 "messages": [{"role": "user", "content": prompt[:6000]}],
                                 "temperature": 0.2, "max_tokens": 600}, timeout=40)
            r.raise_for_status()
            txt = r.json()["choices"][0]["message"]["content"]
            return "groq", txt.strip()[:3000]
        except Exception as e:  # noqa: BLE001
            err += f" | groq: {str(e)[:200]}"
    # Offline deterministic stub: route by intent keywords
    return "offline-stub", ""


def run_agent_turn(user_text: str, session_id: str = "default") -> dict[str, Any]:
    user_text = sanitize(user_text)
    history = load_history(session_id)
    low = user_text.lower()

    cards: list[dict[str, Any]] = []
    tool_trace: list[str] = []

    # Intent routing (deterministic, free, testable)
    if any(k in low for k in ("pipeline", "deploy", "ci ", "build fail", "why did")):
        name = "demo-api" if "api" in low else "demo-web"
        st = tools_ops.get_pipeline_status(name)
        tool_trace.append(f"get_pipeline_status({name}) -> {st.summary}")
        if st.ok and st.data.get("status") == "failed":
            heal = tools_ops.triage_and_heal_incident(st.data.get("tail", ""))
            tool_trace.append(f"triage_and_heal_incident -> {heal.summary}")
            cards = [
                {"type": "status", "title": f"Pipeline {name}: FAILED",
                 "body": st.data.get("tail", "")},
                {"type": "culprit", "title": "Culprit",
                 "body": f"{heal.data.get('culprit', {})}"},
                {"type": "diff", "title": "Verified patch",
                 "body": heal.data.get("diff", "")[:2000]},
                {"type": "verify", "title": "Verification",
                 "body": heal.summary},
            ]
            spoken = (f"Your {name} pipeline failed in {st.data.get('failing_job')}. "
                      f"I found the culprit and verified a patch. {heal.summary}")
            result_text = f"{spoken}\n\nTrace: {' | '.join(tool_trace)}"
        else:
            cards = [{"type": "status", "title": f"Pipeline {name}: {st.data.get('status')}",
                      "body": st.data.get("tail", "")}]
            spoken = f"Pipeline {name} is {st.data.get('status')}. {st.data.get('tail','')}"
            result_text = spoken
        provider = "router+tools"
    elif "verify" in low or "check" in low and ("code" in low or "file" in low or "```" in user_text):
        m = re.search(r"```(?:python)?\n(.*?)```", user_text, re.DOTALL)
        code = m.group(1) if m else user_text
        vr = tools_ops.verify_code_file(code=code)
        tool_trace.append(f"verify_code_file -> {vr.summary}")
        cards = [{"type": "verify", "title": "AST verification",
                  "body": vr.summary + "\n" + str(vr.data)}]
        spoken = ("Code verified clean." if vr.ok
                  else f"Found a syntax issue. {vr.summary}")
        result_text, provider = f"{spoken}\nTrace: {' | '.join(tool_trace)}", "router+tools"
    else:
        # General turn: LLM if keys exist, else helpful stub
        ctx = "\n".join(f"{h['role']}: {h['content'][:500]}" for h in history[-6:])
        prompt = f"{SYSTEM_PROMPT}\n\nHistory:\n{ctx}\n\nUser: {user_text}\n\nAnswer:"
        provider, llm_text = _llm_complete(prompt)
        if not llm_text:
            llm_text = ("I'm K-VoiceOps. Ask me 'why did my deploy fail?' or "
                        "'verify this code: ```python ...```'. "
                        f"(offline stub; add GEMINI_API_KEY for full LLM. history turns: {len(history)})")
        cards = [{"type": "status", "title": "K-VoiceOps", "body": llm_text[:1500]}]
        spoken = llm_text.split("\n")[0][:280]
        result_text = llm_text

    save_turn(session_id, "user", user_text)
    save_turn(session_id, "assistant", result_text[:2000])
    return {"spoken": spoken, "text": result_text, "cards": cards,
            "tools": tool_trace, "provider": provider, "session_id": session_id}
