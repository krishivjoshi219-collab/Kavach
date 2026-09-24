"""Kavach MCP server: guardian tools + family-board MCP App. Spec 2025-11-25."""
from __future__ import annotations

import json
import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from agent import models, protocols, redflags
from agent.config import DEFAULT_SENIOR_ID
from agent.kavach_agent import run_agent_turn

UI_URI = "ui://kavach-family-board"


def _transport_security() -> TransportSecuritySettings:
    extra = [h.strip() for h in os.getenv("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]
    space_host = os.getenv("SPACE_HOST", "").strip()
    if space_host:
        extra.append(space_host)
    force_on = os.getenv("MCP_ENABLE_DNS_PROTECTION") == "1"
    force_off = os.getenv("MCP_DISABLE_DNS_PROTECTION") == "1"
    if (extra or force_on) and not force_off:
        hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*", "127.0.0.1", "localhost"]
        for h in extra:
            hosts += [h] if h in hosts else [h, f"{h}:*"] if ":" not in h else [h]
        return TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=hosts,
            allowed_origins=["http://localhost:*"] + [f"https://{h}" for h in extra],
        )
    return TransportSecuritySettings(enable_dns_rebinding_protection=False)


mcp = FastMCP("kavach", stateless_http=True, streamable_http_path="/",
              transport_security=_transport_security())


def _board_path() -> str:
    return os.path.join(os.path.dirname(__file__), "ui", "family_board.html")


@mcp.resource(UI_URI, name="kavach-family-board",
              title="Kavach family board",
              description="Interactive incident + routine board for the family.",
              mime_type="text/html;profile=mcp-app")
def family_board_resource() -> str:
    """MCP App UI resource (spec extension io.modelcontextprotocol/ui)."""
    with open(_board_path(), encoding="utf-8") as f:
        return f.read()


@mcp.tool(meta={"ui": {"resourceUri": UI_URI}})
def family_board(senior_id: str = DEFAULT_SENIOR_ID) -> dict:
    """Open the interactive family board (MCP App) + text snapshot fallback."""
    models.ensure_seed(senior_id)
    incidents = models.list_incidents(senior_id, 10)
    return {"ok": True, "ui_resource": UI_URI,
            "summary": f"{len(incidents)} case(s) on file.",
            "incidents": [{"id": i["id"], "verdict": i["verdict"], "channel": i["channel"],
                           "status": i["status"]} for i in incidents]}


@mcp.tool()
def debrief_caller(text: str, session_id: str = "default",
                   senior_id: str = DEFAULT_SENIOR_ID) -> dict:
    """Talk through a suspicious call/message, one gentle question at a time."""
    models.ensure_seed(senior_id)
    flow = models.get_flow(session_id)
    if flow and flow["kind"] == "debrief":
        out = protocols.debrief_turn(session_id, text)
    else:
        out = protocols.start_debrief(session_id, senior_id)
    return {"ok": True, "spoken": out["spoken"], "stage": out.get("stage"),
            "done": out.get("done"), "incident_id": out.get("incident_id"),
            "verdict": out.get("verdict"), "cards": out.get("cards", [])}


@mcp.tool()
def report_incident(channel: str, caller_claim: str, details: str,
                    senior_id: str = DEFAULT_SENIOR_ID) -> dict:
    """Log an incident directly (e.g. entered by family) with instant analysis."""
    models.ensure_seed(senior_id)
    signals = redflags.extract_signals(details + "\n" + caller_claim)
    contact = models.find_contact(senior_id, caller_claim)
    verdict, conf, reasons = redflags.score_verdict(
        signals, details, known_contact=bool(contact))
    iid = models.create_incident(senior_id, channel, caller_claim, details,
                                 signals, verdict, conf)
    return {"ok": True, "incident_id": iid, "verdict": verdict,
            "confidence": conf, "reasons": reasons,
            "guidance": redflags.GUIDANCE[verdict]}


@mcp.tool()
def incident_history(senior_id: str = DEFAULT_SENIOR_ID, limit: int = 10) -> dict:
    """Read the case file: past incidents with verdicts."""
    models.ensure_seed(senior_id)
    incidents = models.list_incidents(senior_id, max(1, min(limit, 50)))
    out = []
    for i in incidents:
        try:
            flags = json.loads(i["red_flags"])
            if not isinstance(flags, list):
                flags = []
        except (json.JSONDecodeError, TypeError):
            flags = []  # corrupt row: show the case, not a 500
        out.append({**i, "red_flags": flags})
    return {"ok": True, "count": len(out), "incidents": out}


@mcp.tool()
def checkin(note: str, mood: str = "ok",
            senior_id: str = DEFAULT_SENIOR_ID) -> dict:
    """Log a daily check-in (mood ok | needs_care)."""
    models.ensure_seed(senior_id)
    out = protocols.checkin_turn(senior_id, note if mood != "ok" else f"all well. {note}")
    return {"ok": True, "spoken": out["spoken"], "mood": out["mood"],
            "cards": out["cards"]}


@mcp.tool()
def confirm_routine(label: str, senior_id: str = DEFAULT_SENIOR_ID) -> dict:
    """Mark a daily rhythm (breakfast, walk, medicines…) done."""
    models.ensure_seed(senior_id)
    for r in models.list_routines(senior_id):
        if r["label"].lower() in label.lower() or label.lower() in r["label"].lower():
            models.confirm_routine(r["id"])
            return {"ok": True, "routine": r["label"],
                    "streak": r["streak"] + 1,
                    "summary": f"{r['label']} confirmed — {r['streak'] + 1} days in a row."}
    return {"ok": False,
            "summary": "No matching rhythm.",
            "known": [r["label"] for r in models.list_routines(senior_id)]}


@mcp.tool()
def verify_contact(description: str, senior_id: str = DEFAULT_SENIOR_ID) -> dict:
    """Check a caller against the household safe list."""
    models.ensure_seed(senior_id)
    hit = models.find_contact(senior_id, description)
    if hit:
        return {"ok": True, "match": True, "contact": hit,
                "summary": f"“{hit['label']}” is saved as safe."}
    return {"ok": True, "match": False,
            "summary": "Unknown — treat with care until verified."}


@mcp.tool()
def draft_family_alert(title: str, body: str,
                       senior_id: str = DEFAULT_SENIOR_ID,
                       incident_id: int | None = None) -> dict:
    """Draft a family message. Nothing sends without the spoken code."""
    models.ensure_seed(senior_id)
    d = models.draft_alert(senior_id, "family_note", title, body, incident_id)
    return {"ok": True, "alert_id": d["id"], "confirm_code": d["confirm_code"],
            "summary": "Draft sealed. Read the code aloud to send."}


@mcp.tool()
def confirm_family_alert(code: str, senior_id: str = DEFAULT_SENIOR_ID) -> dict:
    """Send a drafted family message by reading back its confirmation code."""
    models.ensure_seed(senior_id)
    pending = models.get_pending_alert(senior_id)
    if not pending:
        return {"ok": False, "summary": "No message awaiting approval."}
    if models.confirm_alert(pending["id"], code):
        return {"ok": True, "summary": f"Message #{pending['id']} sent to family."}
    return {"ok": False, "summary": "That code does not match. Nothing was sent."}


@mcp.tool()
def daily_briefing(senior_id: str = DEFAULT_SENIOR_ID) -> dict:
    """Spoken household digest: cases, rhythms, recent check-ins."""
    models.ensure_seed(senior_id)
    out = protocols.briefing(senior_id)
    return {"ok": True, "spoken": out["spoken"], "cards": out["cards"]}


@mcp.tool()
def ask_kavach(text: str, session_id: str = "default",
               senior_id: str = DEFAULT_SENIOR_ID) -> dict:
    """Free-form turn with Kavach (routes to protocols, memory, or LLM)."""
    out = run_agent_turn(text, session_id, senior_id)
    return {"ok": True, **{k: out.get(k) for k in
                           ("spoken", "text", "cards", "tools", "provider",
                            "incident_id", "verdict", "stage", "done")}}


def build_mcp_subapp():
    """Helper for standalone `mcp dev`-style runs."""
    return mcp.streamable_http_app()
