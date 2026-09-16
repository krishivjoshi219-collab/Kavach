# Architecture

```
 Pages (simulator/web)                HF Space (app.py :7860)              Free LLMs
 ┌─────────────────────┐              ┌──────────────────────────────┐      ┌──────────┐
 │ Voice/Text composer │──POST /api──▶│ FastAPI: req-id, CORS,       │      │ Gemini   │
 │ Cards/carousel UI   │◀──spoken+───▶│ rate-limit, security headers │─────▶│ Flash    │
 │ Health pill, history│   cards      │                              │      │ Groq ↩   │
 └─────────────────────┘              │  ┌────────────────────────┐  │      └──────────┘
                                      │  │ ops_agent (intent      │  │
 MCP Inspector / Alexa skill          │  │ router → tools or LLM) │  │
 ┌─────────────────────┐              │  └───────────┬────────────┘  │
 │ POST /mcp + /mcp/   │──Streamable─▶│  ┌───────────▼────────────┐  │
 │ initialize→call     │  HTTP 2025   │  │ tools_ops (ported from │  │
 └─────────────────────┘  ‑11‑25     │  │ K-Cli-for-Devs: AST    │  │
                                      │  │ verify, exec guard,    │  │
                                      │  │ triage loop ≤3)        │  │
                                      │  └───────────┬────────────┘  │
                                      │  ┌───────────▼────────────┐  │
                                      │  │ SQLite memory: 50-turn │  │
                                      │  │ sessions, /data volume │  │
                                      │  └────────────────────────┘  │
                                      │  /healthz /readyz /version   │
                                      │  /metrics /docs              │
                                      └──────────────────────────────┘
```

## Request lifecycle (`POST /api/chat`)
1. Middleware stamps `x-request-id`, counts metrics, adds security headers, logs one line.
2. slowapi rate-limit (429 JSON on excess). Pydantic validates `text`/`session_id` (422).
3. `run_agent_turn`: sanitize → SQLite history → deterministic intent router:
   - pipeline/deploy wording → `get_pipeline_status` → on FAILED, `triage_and_heal_incident`
     (culprit parse → candidate patch → `ast.parse` + `py_compile` verify, ≤3 tries);
   - verify/check + code fence → `verify_code_file`;
   - else Gemini → Groq failover → offline stub (never raises).
4. History saved (user + assistant, capped), response returns `spoken + cards + tools +
   provider + request_id + latency_ms`.

## Security notes
- `execute_command` denylist (`rm -rf`, mkfs, fork bombs, socket bind, …) + 30s timeout +
  6k output cap. No shell=True.
- Inputs capped (8k), prompt-injection regex strip, session-id charset lock.
- CORS allowlist (no credentials), security headers, rate limits, no traceback leaks.
- MCP DNS-rebinding protection: open demo by default; strict allowlist via
  `MCP_ALLOWED_HOSTS`/`SPACE_HOST` for locked-down deploys.
- Non-root Docker user, `/data` volume for SQLite, healthcheck on `/healthz`.

## Judging-criteria mapping
- **Tech**: real MCP tools called at runtime (Inspector-verifiable) + AST ground truth.
- **Design**: Pages simulator with voice, cards, tool timeline, health, settings, history.
- **Impact**: any team with CI спрашивает "why did deploy fail?" by voice.
- **Idea**: verification-first agentic loop with cross-session memory, not a Q&A wrapper.
