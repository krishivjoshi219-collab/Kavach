# Friction Log (bonus up to 10%)

## F1 — Streamable HTTP Mount 307s broke strict MCP clients
- Task: serve MCP at bare `/mcp` inside FastAPI.
- Steps: `app.mount("/mcp", subapp)` → every POST 307-redirected to `/mcp/`.
- Expected: direct 200. Actual: Mount trailing-slash redirect; some clients drop bodies on 307.
- Severity: Critical. Workaround: direct Starlette `Route("/mcp")` + `Route("/mcp/")`
  to one `StreamableHTTPASGIApp`, sharing the session-manager lifespan.
- Suggestion: document the FastAPI-mount recipe per spec version in the Python SDK.

## F2 — `session_manager.run()` single-entry rule vs test suites
- Task: pytest covering readiness + MCP handshake.
- Steps: two `TestClient` lifespan sessions → second raised
  “run() can only be called once per instance”.
- Expected: re-enterable in tests. Actual: one-shot task group.
- Severity: Important. Workaround: single shared lifespan session per test process;
  per-test SQLite isolation via conftest instead of app restarts.
- Suggestion: support stop/restart of the session manager for test harnesses.

## F3 — MCP DNS-rebinding defaults 421 everything off-localhost
- Task: deploy the MCP server to Hugging Face Spaces.
- Steps: default allowlist is localhost-only → every HF request 421 Invalid Host.
- Expected: work behind any host. Actual: SDK only supports exact + `host:*` patterns.
- Severity: Critical. Workaround: open-demo default + opt-in lockdown via
  `MCP_ALLOWED_HOSTS` (documented; no fake `*.domain` globs — the SDK can't match them).
- Suggestion: first-class `allowed_hosts=["*"]`-style public-demo mode in settings.

## F4 — Python SDK has no MCP Apps authoring helper
- Task: ship `ui://` family board from Python.
- Steps: TS docs assume `@modelcontextprotocol/ext-apps`; Python needed hand-built
  `resource(mime_type="text/html;profile=mcp-app")` + tool `_meta.ui.resourceUri`.
- Expected: symmetric helpers. Actual: works, but undiscoverable.
- Severity: Important. Workaround: spec-direct implementation + text fallback + our own
  AppBridge host in the simulator to prove interop.
- Suggestion: port the ext-apps authoring helper to the Python SDK with an example.

## F5 — Narration LLMs invent facts unless caged
- Task: warm senior-facing tone via free-tier LLM.
- Steps: early prompts let the model invent verdicts and advice.
- Expected: tone-only changes. Actual: added facts, skipped protocol softness.
- Severity: Critical (safety domain). Workaround: rephrase-only system prompt, 400-token
  cap, template fallback; verdicts computed by rules, never by LLM.
- Suggestion: cookbook pattern for "LLM as narrator, rules as decider" in safety contexts.
