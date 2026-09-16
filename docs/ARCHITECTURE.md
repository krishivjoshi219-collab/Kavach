# Architecture (Kavach)

```
 Senior (voice)                     Kavach backend :7860                      Family
 ┌──────────────────┐  POST /api/chat  ┌──────────────────────────────┐  GET /api/family-feed ┌──────────────┐
 │ Senior view      │─────────────────▶│ protocol governor (stages    │◀──────────────────────│ Family board │
 │ big type, Talk   │◀──spoken+cards───│ channel→who→what→pressure→   │──proof cards──────────│ + MCP App    │
 └──────────────────┘                  │ verdict; cannot skip)        │   iframe via bridge   │  ui://…      │
                                       │  ┌────────────────────────┐  │                       └──────────────┘
 MCP Inspector / agents                │  │ redflags (8 rules,     │  │
 ┌──────────────────┐  Streamable HTTP │  │ weighted, explainable) │  │  Free LLMs (optional)
 │ 11 tools + ui:// │─────────────────▶│  └───────────┬────────────┘  │  ┌──────────────┐
 │ resource         │  2025-11-25      │  ┌───────────▼────────────┐  │  │ Gemini/Groq  │
 └──────────────────┘                  │  │ SQLite: seniors, cases, │──│  │ narration    │
                                       │  │ routines, alerts, flows │  │  └──────────────┘
                                       │  └────────────────────────┘  │  Offline templates
                                       │  /healthz /readyz /metrics   │  when no key
                                       └──────────────────────────────┘
```

## Why it wins (rubric mapping)
- **Tech**: real MCP (verified handshake), MCP App `ui://` resource with bridge demo,
  governed protocols + evidence-cited verdicts at runtime — not a wrapper.
- **Design**: two faces — senior view engineered for dignity (22px type, one question
  at a time, replay, no blame language) and a family proof board. Voice-first.
- **Impact**: elder fraud is a $10B+/year epidemic; aging-alone households grow
  everywhere. A guardian that proves its work serves people who cannot verify.
- **Idea**: protection for the unverifiable, proof for the verifier. No other entry
  pairs a governed safety protocol with an MCP App family loop.

## Safety (load-bearing)
- Scope: scam debriefs, routines, check-ins, briefings, family alerts. NEVER medical,
  legal, or investment advice — the skill file and prompts forbid it; evals pin it.
- Dignity: no blame language anywhere ("you did the right thing telling me").
- Gating: `confirm_family_alert` requires the exact 6-letter code; wrong code sends
  nothing. Sandbox: `execute`-style tools do not exist in this server at all.
- Determinism where it matters: verdicts come from weighted rules over evidence;
  the LLM narrates and rephrases only. Evals: 10 scam scripts caught, 5 legit calls
  never flagged SCAM, stage order asserted.
- Data: fictional demo household; per-senior ids isolate families; DB on volume.
