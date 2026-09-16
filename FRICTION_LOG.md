# Friction Log (bonus up to 10%)

## F1 — Streamable HTTP vs SSE confusion
- Task: expose MCP over HTTP for Inspector + Alexa skill.
- Steps: tried SSE transport first, then `stateless_http=True` + `streamable_http_app()` mounted at `/mcp`.
- Expected: one documented path. Actual: two transports in examples, version-gated behavior.
- Severity: Important. Workaround: pinned `mcp>=1.12`, stateless mode, mount under FastAPI.
- Suggestion: single canonical FastAPI-mount example per spec version.

## F2 — HF cold starts break voice demo pacing
- Task: live voice → patch demo on free Space.
- Steps: first request after idle took ~45s.
- Expected: <5s. Actual: model-load + container wake.
- Severity: Important. Workaround: `/healthz` warm-up before recording; video as ground truth;
  latency + request-id shown in UI.
- Suggestion: document “demo warm-up” pattern for hackathon judges.

## F3 — Free-LLM 429s mid-agent-loop
- Task: sustained multi-turn triage on free quota.
- Steps: burst of retries hit Gemini 429.
- Expected: graceful degrade. Actual: raw 429 exception killed turn.
- Severity: Critical. Workaround: deterministic intent router (triage runs without LLM) +
  Groq failover + offline stub; never 500.
- Suggestion: first-class 429→failover snippet in Gemini/Groq docs.

## F4 — Pages↔HF CORS on new domains
- Task: point Pages build at HF backend.
- Steps: preflight blocked until `ALLOWED_ORIGINS` updated.
- Expected: wildcard dev default. Actual: manual allowlist sync.
- Severity: Nice-to-have. Workaround: `ALLOWED_ORIGINS` env + documented redeploy step.
- Suggestion: checklist in Pages custom-domain flow reminding to update API CORS.
