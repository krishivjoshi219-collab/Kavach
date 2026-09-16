# API Reference (Kavach)

Base: `https://<space>.hf.space` (local: `http://localhost:7860`).

## `GET /healthz` — liveness · `GET /readyz` — readiness (DB + MCP manager + board file)
## `GET /version` — build, `mcp_spec`, `mcp_app` (`ui://kavach-family-board`), LLM mode (no secrets)
## `GET /metrics` — uptime, request/chat/error counters, avg latency

## `POST /api/chat` — conversation (rate-limited per IP, 429 JSON)
```json
{ "text": "Something strange happened", "session_id": "s-1", "senior_id": "demo-senior" }
```
Response: `{spoken, text, cards, tools, provider, session_id, request_id, latency_ms,
incident_id?, verdict?, stage?, done?, confirm_code?}`. Every response carries
`x-request-id`. Validation: `text` 1–8000 chars; ids match `^[\w\-.]{1,64}$` (422).

## `GET /api/family-feed?senior_id=` — senior profile, incidents (with parsed red flags),
routines, check-ins, alerts (metadata only), safe-contact labels.

## `POST /mcp`, `/mcp/` — MCP Streamable HTTP (spec 2025-11-25)
Headers: `Content-Type: application/json`, `Accept: application/json, text/event-stream`,
`MCP-Protocol-Version: 2025-11-25`. Handshake: `initialize` → `notifications/initialized`
→ `tools/list` / `resources/list` → `tools/call`.
Tools: `debrief_caller`, `report_incident`, `incident_history`, `checkin`,
`confirm_routine`, `verify_contact`, `draft_family_alert`, `confirm_family_alert`,
`daily_briefing`, `ask_kavach`, `family_board` (links `ui://` resource via `_meta`).
Resource: `ui://kavach-family-board` (`text/html;profile=mcp-app`, extension
`io.modelcontextprotocol/ui`) with text fallback — also served at
`GET /apps/family-board.html`.

## Errors
- `422` validation · `429` `{ok:false, error:"rate_limited", request_id}` — back off
- `500` `{ok:false, error:"internal", request_id}` — never leaks tracebacks
- MCP DNS protection: open demo mode by default; `MCP_ALLOWED_HOSTS` locks Hosts (else 421)
