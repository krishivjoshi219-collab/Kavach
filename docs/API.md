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

## Mobile Contract & Zero-Knowledge Relay (`/api/v1/*`)
- `POST /api/v1/households` — Generates unique household ID.
- `POST /api/v1/pair/init` — Starts pairing ceremony; stores manager public key; returns 6-char pairing code (10m TTL).
- `POST /api/v1/pair/complete` — Consumes pairing code; binds senior public key and senior ID.
- `POST /api/v1/sync/push` — Ingests encrypted ciphertext blob (relay only, server never inspects payload).
- `GET  /api/v1/sync/pull?household_id=&since_id=` — Retrieves encrypted blobs.
- `POST /api/v1/screen/lookup` — Privacy-preserving check against household-salted number hash.
- `POST /api/v1/screen/block` — Adds salted number hash to household blocklist (`block`, `silence`, `allow`).
- `POST /api/v1/screen/unblock` — Removes number hash from household blocklist.
- `POST /api/v1/consent/set` — Senior sets granted capabilities (`screen_calls`, `forward_sms`, `remote_cut`, `cloud_brain`, `share_routines`).
- `POST /api/v1/consent/revoke?household_id=&senior_id=` — Instant elder autonomy kill switch; revokes all capabilities.
- `GET  /api/v1/consent?household_id=&senior_id=` — Returns capability grant status.
- `POST /api/v1/device/command` — Queues consent-gated remote action (`cut_call`, `sound_siren`, `show_message`).
- `GET  /api/v1/device/commands?household_id=&target=` — Retrieves queued commands for device.
- `POST /api/v1/device/commands/{id}/ack` — Acknowledges command delivery.
- POST /api/v1/brain/ask — Quota-gated cloud inference (requires cloud_brain consent; quota depends on tier).
- POST /api/v1/household/tier — Synchronizes subscription tier (free, pro, ultra) with quotas.
- GET  /api/v1/household/tier?household_id= — Retrieves current tier and quota.
- POST /api/v1/checkin — Records senior daily wellness check-in (status: safe, uneasy, need_call).
- POST /api/v1/notifications/send — Dispatches OneSignal safety journeys (morning_checkin, missed_checkin, emergency_alert).
- GET  /api/v1/threat-radar?household_id= — Aggregated community threat indicators and regional scam statistics.

## Errors
- `422` validation · `429` `{ok:false, error:"rate_limited", request_id}` — back off
- `500` `{ok:false, error:"internal", request_id}` — never leaks tracebacks
- MCP DNS protection: open demo mode by default; `MCP_ALLOWED_HOSTS` locks Hosts (else 421)
