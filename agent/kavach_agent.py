"""Kavach agent: protocol-first dispatcher + LLM narration.

Safety design: scam debriefs and check-ins run as governed protocols
(every stage visited, verdicts evidence-cited). The LLM narrates and
rephrases — it never invents verdicts or skips stages.
"""
from __future__ import annotations

import re
from typing import Any

from . import models, protocols
from .config import (
    DEFAULT_SENIOR_ID,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    MAX_INPUT_CHARS,
    ZEN_API_KEY,
    ZEN_BASE,
    ZEN_MODEL,
)

DEBRIEF_HINTS = ["scam", "fraud", "strange", "something happened", "unknown number",
                 "otp", "someone called", "bank called", "about my bank", "my bank",
                 "bank account", "suspicious", "fishy", "cheat", "doubt",
                 "police", "threaten", "blocked", "frozen", "arrest",
                 "kyc", "prize", "lottery", "offer", "caller", "phishing"]
CHECKIN_HINTS = ["check in", "checking in", "good morning", "good evening", "i am ok",
                 "i'm ok", "not feeling", "dizzy", "all well"]
BRIEF_HINTS = ["briefing", "digest", "summary", "how is", "overview", "status report",
               "anything happen", "catch me up"]
HISTORY_HINTS = ["incident", "history", "past case", "previous", "last time", "cases"]
ALERT_HINTS = ["tell my family", "alert", "notify", "send the message", "approve"]
ROUTINE_HINTS = ["breakfast", "medicines", "medicine", "walk", "lunch", "dinner",
                 "did the", "finished my"]

_LLM_TIMEOUT_S = 15
_LLM_MAX_TOKENS = 400


def sanitize(text: str) -> str:
    text = text[:MAX_INPUT_CHARS]
    text = re.sub(r"(?i)ignore (all )?previous instructions.*", "[filtered]", text)
    text = re.sub(r"(?i)disregard .*instructions.*", "[filtered]", text)
    return text.strip()


def _llm_narrate(system: str, user: str) -> tuple[str, str]:
    """Returns (provider, text). Never raises; empty text means use templates.

    Chain: Zen (free, OpenAI-compatible) -> Gemini -> Groq -> offline stub.
    Narration only — verdicts are decided by rules before this is ever called.
    """
    import httpx as _httpx
    prompt = system + "\n\nContext:\n" + user[:2500]
    if ZEN_API_KEY:
        try:
            r = _httpx.post(f"{ZEN_BASE}/chat/completions",
                           headers={"Authorization": f"Bearer {ZEN_API_KEY}"},
                           json={"model": ZEN_MODEL,
                                 "messages": [{"role": "user", "content": prompt[:4000]}],
                                 "temperature": 0.3, "max_tokens": _LLM_MAX_TOKENS},
                           timeout=_LLM_TIMEOUT_S)
            r.raise_for_status()
            txt = r.json()["choices"][0]["message"]["content"].strip()
            if txt:
                return "zen", txt[:1500]
        except Exception:  # noqa: BLE001, S110 - silent failover to Gemini below
            pass
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            resp = genai.GenerativeModel(GEMINI_MODEL).generate_content(
                prompt, request_options={"timeout": _LLM_TIMEOUT_S})
            if resp.text and resp.text.strip():
                return "gemini", resp.text.strip()[:1500]
        except Exception:  # noqa: BLE001, S110 - silent failover to GROQ below
            pass
    if GROQ_API_KEY:
        try:
            r = _httpx.post("https://api.groq.com/openai/v1/chat/completions",
                           headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                           json={"model": GROQ_MODEL,
                                 "messages": [{"role": "user", "content": prompt[:4000]}],
                                 "temperature": 0.3, "max_tokens": _LLM_MAX_TOKENS},
                           timeout=_LLM_TIMEOUT_S)
            r.raise_for_status()
            txt = r.json()["choices"][0]["message"]["content"].strip()
            if txt:
                return "groq", txt[:1500]
        except Exception:  # noqa: BLE001, S110 - silent failover to offline stub below
            pass
    return "offline-stub", ""


NARRATOR = ("You are Kavach, a warm guardian speaking to an elderly person. "
            "Rephrase the staff note below in 2-4 short, calm spoken sentences. "
            "Simple words. No jargon. Never add facts, verdicts, or advice "
            "beyond the note. Never mention medicine brands or dosages.")


def _speak(template: str) -> tuple[str, str]:
    provider, text = _llm_narrate(NARRATOR, template)
    if text:
        return provider, text
    return "template", template


def run_agent_turn(user_text: str, session_id: str = "default",
                   senior_id: str = DEFAULT_SENIOR_ID) -> dict[str, Any]:
    user_text = sanitize(user_text)
    models.ensure_seed(senior_id)
    low = user_text.lower()

    flow = models.get_flow(session_id)
    if flow and flow["kind"] == "debrief":
        out = protocols.debrief_turn(session_id, user_text)
        return _finish(session_id, user_text, out, "protocol+verifier")

    if any(h in low for h in ALERT_HINTS):
        return _handle_alert(session_id, user_text, senior_id)
    if any(h in low for h in DEBRIEF_HINTS):
        flow_out = protocols.start_debrief(session_id, senior_id)
        # Fold the trigger message in as context for the who-stage later.
        return _finish(session_id, user_text, flow_out, "protocol+verifier")
    if any(h in low for h in CHECKIN_HINTS):
        out = protocols.checkin_turn(senior_id, user_text)
        return _finish(session_id, user_text, out, "protocol+memory")
    if any(h in low for h in BRIEF_HINTS):
        out = protocols.briefing(senior_id)
        return _finish(session_id, user_text, out, "protocol+memory")
    if any(h in low for h in HISTORY_HINTS):
        return _finish(session_id, user_text, _history(senior_id), "protocol+memory")
    if any(h in low for h in ROUTINE_HINTS):
        return _finish(session_id, user_text, _routine_confirm(senior_id, user_text),
                       "protocol+memory")

    provider, text = _llm_narrate(
        NARRATOR + " If the person describes a suspicious call or message, reply with exactly: "
                   "START_DEBRIEF. If they seem unwell or low, reply with exactly: START_CHECKIN. "
                   "Otherwise answer briefly and warmly in two sentences.",
        user_text)
    if text.strip() == "START_DEBRIEF":
        return _finish(session_id, user_text,
                       protocols.start_debrief(session_id, senior_id), provider)
    if text.strip() == "START_CHECKIN":
        return _finish(session_id, user_text,
                       protocols.checkin_turn(senior_id, user_text), provider)
    if not text:
        text = ("I am Kavach, here to keep you safe. If a strange call or message worries you, "
                "tell me “something strange happened” and we will go through it together. "
                "Or say “checking in” so I can mark your day.")
        provider = "template"
    out = {"spoken": text.split(". ")[0][:280], "text": text,
           "cards": [{"type": "status", "title": "Kavach", "body": text[:1200]}],
           "tools": []}
    return _finish(session_id, user_text, out, provider)


def _finish(session_id: str, user_text: str, out: dict, provider: str) -> dict[str, Any]:
    spoken = out.get("spoken", "")
    if provider in ("gemini", "groq", "zen") and out.get("done"):
        _, warm = _speak(spoken)
        if warm:
            spoken = warm
    models.save_turn(session_id, "user", user_text)
    models.save_turn(session_id, "assistant", out.get("text", spoken)[:1500])
    return {"spoken": spoken, "text": out.get("text", spoken),
            "cards": out.get("cards", []), "tools": out.get("tools", []),
            "provider": out.get("provider", provider), "session_id": session_id,
            **{k: v for k, v in out.items() if k in
               ("incident_id", "verdict", "confidence", "mood", "stage", "done",
                "confirm_code", "alert_id")}}


def _history(senior_id: str) -> dict[str, Any]:
    incidents = models.list_incidents(senior_id, 10)
    if not incidents:
        spoken = "A clean slate — no incidents on record. Long may it continue."
    else:
        latest = incidents[0]
        spoken = (f"{len(incidents)} case(s) on file. The latest is case #{latest['id']}: "
                  f"{latest['verdict']}, from a {latest['channel']}. All closed or watched.")
    body = "\n".join(f"• Case #{i['id']} — {i['verdict']} via {i['channel']}: "
                     f"{(i['caller_claim'] or 'unknown caller')[:60]}" for i in incidents)
    return {"spoken": spoken, "done": True,
            "cards": [{"type": "status", "title": f"Case file ({len(incidents)})",
                       "body": body or "Nothing on file."}],
            "tools": ["incident_history -> read"]}


def _routine_confirm(senior_id: str, user_text: str) -> dict[str, Any]:
    low = user_text.lower()
    match = None
    for r in models.list_routines(senior_id):
        first = r["label"].lower().split()[0]
        if first in low or r["label"].lower() in low:
            match = r
            break
    if match:
        models.confirm_routine(match["id"])
        spoken = (f"Wonderful — {match['label']} marked for today. "
                  f"That is {match['streak'] + 1} days in a row. Keep shining.")
        tools = [f"confirm_routine({match['label']}) -> streak {match['streak'] + 1}"]
    else:
        labels = ", ".join(r["label"] for r in models.list_routines(senior_id))
        spoken = f"Tell me which one — was it {labels}?"
        tools = ["routine_board -> read"]
    return {"spoken": spoken, "done": True,
            "cards": [{"type": "status", "title": "Daily rhythms", "body": spoken}],
            "tools": tools}


CODE_RE = re.compile(r"\b([A-Z0-9]{6})\b")


def _handle_alert(session_id: str, user_text: str, senior_id: str) -> dict[str, Any]:
    pending = models.get_pending_alert(senior_id)
    m = CODE_RE.search(user_text.upper())
    if pending and m and models.confirm_alert(pending["id"], m.group(1)):
        spoken = ("Done — your family has the message with everything I saved. "
                  "You did the brave thing telling me.")
        cards = [{"type": "verify", "title": "Family alert sent ✓",
                  "body": pending["title"] + "\n" + pending["body"][:800]}]
        out = {"spoken": spoken, "done": True, "cards": cards,
               "tools": [f"confirm_alert(#{pending['id']}) -> sent"]}
        return _finish(session_id, user_text, out, "protocol+ceremony")
    if pending:
        spoken = (f"I have the message ready: “{pending['title']}”. To send it, read back "
                  f"the code on your screen, letter by letter: "
                  f"{' '.join(pending['confirm_code'])}. Nothing sends without your word.")
        cards = [{"type": "status", "title": "Awaiting your word",
                  "body": f"Code: {pending['confirm_code']}\n\n{pending['body'][:800]}"}]
        out = {"spoken": spoken, "done": False, "confirm_code": pending["confirm_code"],
               "alert_id": pending["id"], "cards": cards, "tools": ["alert drafted -> awaiting code"]}
        return _finish(session_id, user_text, out, "protocol+ceremony")
    incidents = models.list_incidents(senior_id, 1)
    context = (f"Latest case #{incidents[0]['id']}: {incidents[0]['verdict']}"
               if incidents else "No cases yet — a general hello.")
    draft = models.draft_alert(senior_id, "family_note", "Asha asked me to reach out",
                               context + "\n" + user_text[:500],
                               incidents[0]["id"] if incidents else None)
    spoken = (f"Message written and sealed. To send it to your family, read back the code: "
              f"{' '.join(draft['confirm_code'])}. I will not send anything until you say it.")
    cards = [{"type": "status", "title": "Message drafted — your word needed",
              "body": f"Code: {draft['confirm_code']}"}]
    out = {"spoken": spoken, "done": False, "confirm_code": draft["confirm_code"],
           "alert_id": draft["id"], "cards": cards,
           "tools": [f"draft_alert(#{draft['id']}) -> code issued"]}
    return _finish(session_id, user_text, out, "protocol+ceremony")
