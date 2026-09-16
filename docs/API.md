# API Reference

Base: `https://<space>.hf.space` (local: `http://localhost:7860`).

## `GET /healthz` — liveness
Always 200 when the process is up. `{ok, service, version, mcp, spec, time}`.

## `GET /readyz` — readiness
200 `{ready: true, checks: {mcp_session_manager: true, db_writable: true}}` when able to
serve; 503 otherwise. Poll this from uptime monitors, not `/healthz`.

## `GET /version`
`{service, version, mcp_spec: "2025-11-25", llm: {mode, gemini_configured, groq_configured, ...},
endpoints: [...]}`. No secrets. The simulator reads `llm.mode` for its provider badge.

## `GET /metrics`
`{uptime_s, requests_total, chat_total, chat_errors, chat_latency_ms_sum,
avg_chat_latency_ms, mcp_total, rate_limited}`. In-memory counters, reset on restart.

## `POST /api/chat` — REST bridge for the simulator
Rate-limited per IP (`RATE_LIMIT_PER_MIN`, default 30/min → 429 JSON).
```json
{ "text": "why did my deploy fail?", "session_id": "demo" }
```
`session_id` matches `^[\w\-.]{1,64}$`. Response:
```json
{ "spoken": "…", "text": "…", "cards": [{"type","title","body"}],
  "tools": ["…"], "provider": "router+tools|gemini|groq|offline-stub",
  "session_id": "demo", "request_id": "…", "latency_ms": 123 }
```
Every response carries `x-request-id` (also in body). Quote it in bug reports.

## `POST /mcp`, `POST /mcp/` — MCP Streamable HTTP (spec 2025-11-25)
Both paths serve the same endpoint (no redirects). Headers:
`Content-Type: application/json`, `Accept: application/json, text/event-stream`,
`MCP-Protocol-Version: 2025-11-25`. Handshake: `initialize` → `notifications/initialized`
→ `tools/list` → `tools/call`. Tools: `get_pipeline_status`, `triage_and_heal_incident`,
`verify_code_file`, `inspect_repo_structure`, `execute_command`, `propose_patch`.

## Errors
- `422` validation (`text` empty/>8000 chars, bad `session_id`).
- `429` `{ok:false, error:"rate_limited", request_id}` — back off and retry.
- `500` `{ok:false, error:"internal", request_id}` — never leaks tracebacks.
- MCP DNS protection: default open demo mode; setting `MCP_ALLOWED_HOSTS` locks Hosts
  (misconfigured hosts get `421 Invalid Host header`).
