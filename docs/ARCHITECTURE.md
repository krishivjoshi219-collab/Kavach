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

## Android Guardian App & Zero-Knowledge Relay
- **Zero-knowledge Blind Relay**: Server receives only salted hashes (`hash(salt, number)`) and opaque ECIES ciphertext encrypted with Google Tink (`HybridKeyTemplates.ECIES_P256_HKDF_HMAC_SHA256_AES128_GCM`). Plaintext calls, transcripts, and personal contact lists never touch server disks.
- **On-Device Screening**: Android `CallScreeningService` analyzes incoming numbers and auto-rejects known scam hashes locally without cloud queries.
- **SMS Phishing Quarantine**: Android `BroadcastReceiver` intercepts scam SMS using on-device `RuleEngine`, alerting the senior and relaying encrypted notifications to the family manager.
- **Remote Intervention (Consent-Gated)**: Family manager can issue a remote `cut_call` command to end an active scam call on the senior's phone, or sound a synchronized emergency siren.
- **Autonomy Kill Switch**: All manager powers are strictly lent. Senior can tap the prominent Kill Switch at any time to instantly revoke all remote permissions via `/api/v1/consent/revoke`.
- **Monetization (RevenueCat)**: 3-tier model (`Free`, `Pro` $4.99/mo, `Ultra` $11.99/mo) funding cloud AI inference while keeping basic protection free with $0 cloud marginal cost.

## Why it wins (rubric mapping)
- **Tech**: real MCP (verified handshake), MCP App `ui://` resource with bridge demo,
  governed protocols + evidence-cited verdicts at runtime, plus native Android CallScreening
  with Google Tink E2E hybrid crypto — not a wrapper.
- **Design**: two faces — senior view engineered for dignity (22px type, one question
  at a time, replay, no blame language) and a family proof board. Voice-first.
- **Impact**: elder fraud is a $10B+/year epidemic; aging-alone households grow
  everywhere. A guardian that proves its work serves people who cannot verify.
- **Idea**: protection for the unverifiable, proof for the verifier. No other entry
  pairs a governed safety protocol with an MCP App family loop and zero-knowledge mobile relay.

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

