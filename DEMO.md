# Demo Script (<3 min video)
0:00–0:20 — Pages UI: click 🎤, say “Alexa, why did my deploy fail?”
0:20–1:00 — HF `/mcp`: Inspector lists 6 tools; server logs show
  `get_pipeline_status(demo-web)` → FAILED → `triage_and_heal_incident`.
1:00–2:00 — Agent: culprit line, AST `ast.parse` + `py_compile` verify loop (max 3), diff.
2:00–2:50 — Cards/carousel: Status → Culprit → Verified patch → “tests pass”; voice speaks summary.
Show `request_id` + latency footer + `/healthz` 200 as proof.
