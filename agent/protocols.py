"""Protocol governor: state machines the agent cannot skip.

Debrief stages: opening -> channel -> who -> what -> pressure -> verdict -> guidance.
Every incident passes every stage; verdicts always cite evidence.
"""
from __future__ import annotations

from typing import Any

from . import models, redflags

OPENING = ("I am here, and there is no rush. Someone contacted you and it worried you — "
           "let us go through it together, one small question at a time. "
           "Was it a phone call, a message, or someone at the door?")

STAGE_Q = {
    "channel": "Was it a phone call, a message on SMS or WhatsApp, or someone at the door?",
    "who": "Who did they say they were — which bank, office, or person?",
    "what": "In your own words, what did they ask you to do? Take your time.",
    "pressure": "Did they hurry you, threaten you, or say something bad happens today? "
                "A simple yes or no is perfect.",
}


def start_debrief(session_id: str, senior_id: str) -> dict[str, Any]:
    models.set_flow(session_id, "debrief", "channel", None, {"senior_id": senior_id})
    return {"spoken": OPENING, "stage": "channel", "done": False,
            "cards": [{"type": "status", "title": "Safe space started",
                       "body": "One question at a time. Nothing you say can go wrong here."}]}


def _transcript(data: dict) -> str:
    return "\n".join(f"{who}: {line}" for who, line in data.get("lines", []))


def debrief_turn(session_id: str, user_text: str) -> dict[str, Any]:
    flow = models.get_flow(session_id)
    if not flow or flow["kind"] != "debrief":
        senior = flow["data"].get("senior_id", "demo-senior") if flow else "demo-senior"
        return start_debrief(session_id, senior)
    data = flow["data"]
    senior_id = data.get("senior_id", "demo-senior")
    stage = flow["stage"]
    data.setdefault("lines", []).append(("senior", user_text))
    if stage == "channel":
        data["channel"] = user_text[:120]
    elif stage == "who":
        data["caller_claim"] = user_text[:200]
    elif stage == "what":
        data["asked"] = user_text[:500]
    elif stage == "pressure":
        data["pressure"] = user_text[:200]

    order = ["channel", "who", "what", "pressure"]
    if stage in order:
        nxt = order[order.index(stage) + 1] if stage != "pressure" else "verdict"
        if nxt == "verdict":
            return _reach_verdict(session_id, senior_id, data)
        models.set_flow(session_id, "debrief", nxt, None, data)
        ack = {"channel": "Noted. ", "who": "Thank you. ",
               "what": "Good, that helps a lot. "}.get(stage, "")
        return {"spoken": ack + STAGE_Q[nxt], "stage": nxt, "done": False,
                "cards": [{"type": "status", "title": "Listening…",
                           "body": "Saved. " + STAGE_Q[nxt]}]}
    return _reach_verdict(session_id, senior_id, data)


def _reach_verdict(session_id: str, senior_id: str, data: dict) -> dict[str, Any]:
    transcript = _transcript(data)
    signals = redflags.extract_signals(transcript)
    contact = models.find_contact(senior_id, data.get("caller_claim", ""))
    verdict, conf, reasons = redflags.score_verdict(
        signals, transcript, known_contact=bool(contact))
    incident_id = models.create_incident(
        senior_id, _canon_channel(data.get("channel", "")), data.get("caller_claim", ""),
        transcript, signals, verdict, conf)
    models.clear_flow(session_id)
    guide = redflags.GUIDANCE[verdict]
    if verdict == "SCAM":
        spoken = ("I have heard enough, and I am sure: this is a scam. "
                  "You did exactly the right thing telling me. Hang up if they call back, "
                  "share nothing, and I will tell your family. You are safe.")
    elif verdict == "SUSPICIOUS":
        spoken = ("This looks suspicious — two warning signs. Do not share codes or install "
                  "anything. Hang up and call the official number yourself. "
                  "I have saved everything and told your family file.")
    elif verdict == "LIKELY_SAFE":
        spoken = ("Good news — this looks like an ordinary call, nothing was asked of you. "
                  "But remember: if anyone ever asks for codes or money, stop and tell me first.")
    else:
        spoken = ("I cannot settle this one yet — and that is alright. Share nothing for now, "
                  "ask a family member to listen in, and everything is saved here for them.")
    cards = [
        {"type": "verdict", "title": f"Verdict: {verdict} ({int(conf * 100)}%)",
         "body": "\n".join(f"• {r}" for r in reasons) or "No red flags found."},
        {"type": "guidance", "title": "What to do now",
         "body": "\n".join(f"{i + 1}. {g}" for i, g in enumerate(guide))},
    ]
    if contact:
        cards.append({"type": "status", "title": "Known contact match",
                      "body": f"“{contact['label']}” is in the safe list."})
    return {"spoken": spoken, "stage": "verdict", "done": True,
            "incident_id": incident_id, "verdict": verdict,
            "confidence": conf, "cards": cards,
            "tools": [f"extract_signals -> {len(signals)} red flags",
                      f"verify_contact -> {'known' if contact else 'unknown'}",
                      f"log_incident -> case #{incident_id}"]}


def _canon_channel(raw: str) -> str:
    low = raw.lower()
    if "whatsapp" in low or "sms" in low or "message" in low or "text" in low:
        return "message"
    if "door" in low or "visit" in low or "came" in low:
        return "visit"
    return "call"


def checkin_turn(senior_id: str, user_text: str) -> dict[str, Any]:
    low = user_text.lower()
    bad_words = ["not", "bad", "dizzy", "pain", "sad", "worried", "scared", "tired", "alone"]
    mood = "needs_care" if any(w in low for w in bad_words) else "ok"
    models.add_checkin(senior_id, "voice", user_text, mood)
    if mood == "ok":
        spoken = ("Lovely to hear. I have marked today as a good day. "
                  "I am right here whenever you need me.")
        cards = [{"type": "status", "title": "Check-in: doing well",
                  "body": "Logged with today's date for the family board."}]
    else:
        spoken = ("Thank you for telling me honestly — that was brave. "
                  "Would you like me to tell your family you need a little extra care today? "
                  "Just say the word.")
        cards = [{"type": "status", "title": "Check-in: needs a little care",
                  "body": "Logged. Say “tell my family” and I will prepare the message."}]
    return {"spoken": spoken, "done": True, "mood": mood, "cards": cards,
            "tools": ["note_checkin -> logged"]}


def briefing(senior_id: str) -> dict[str, Any]:
    senior = models.get_senior(senior_id) or {"name": "friend"}
    incidents = models.list_incidents(senior_id, 5)
    routines = models.list_routines(senior_id)
    checkins = models.list_checkins(senior_id, 3)
    open_cases = [i for i in incidents if i["status"] != "closed"]
    lines = [f"Good day, {senior['name']}. Here is your household at a glance."]
    if open_cases:
        lines.append(f"{len(open_cases)} open case(s) — the newest is case "
                     f"#{open_cases[0]['id']}: {open_cases[0]['verdict']}.")
    else:
        lines.append("No open cases. All quiet on the safety front.")
    pending = [r for r in routines if not r["last_confirmed"]]
    if pending:
        lines.append(f"Still to enjoy today: {', '.join(r['label'] for r in pending)}.")
    lines.append(f"{len(checkins)} recent check-ins, the last one felt "
                 f"“{checkins[0]['mood'] if checkins else '—'}”.")
    body = "\n".join(f"• Case #{i['id']}: {i['verdict']} ({i['channel']})" for i in incidents)
    cards = [
        {"type": "status", "title": "Household briefing",
         "body": body or "No incidents on record. A clean slate."},
        {"type": "status", "title": "Today's rhythms",
         "body": "\n".join(f"• {r['label']} — usually {r['expected_time']}"
                            f"{' ✓' if r['last_confirmed'] else ''}" for r in routines)
         or "No routines set."},
    ]
    return {"spoken": " ".join(lines), "done": True, "cards": cards,
            "tools": ["incident_history -> read", "routine_board -> read"]}
