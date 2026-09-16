# Kavach 🛡️ — a voice guardian for seniors (Alexa+ Track)

> “My codebase has an immune system — and this is what it sounds like” was the dev
> idea. Kavach is what it became: **protection for people who cannot verify, with
> proof for people who can.** A senior talks through a scary call, one gentle
> question at a time; the family gets verdicts with cited evidence — never vibes.

**What it does:** scam-call debriefs with evidence-cited verdicts (SCAM / SUSPICIOUS /
UNCERTAIN / LIKELY_SAFE), daily rhythms + check-ins, a spoken household briefing,
and family alerts sealed behind a read-back confirmation code. Nothing alerts the
family without the senior's spoken word.

**How it submits:**
1. **Real MCP Server**: Streamable HTTP, spec `2025-11-25`, 11 tools + `ui://kavach-family-board` MCP App resource + Agent Skill (`skills/kavach-guardian`).
2. **Native Android Guardian App**: `CallScreeningService` auto-reject + SMS quarantine + Google Tink ECIES hybrid crypto + Emergency Siren + Elder Autonomy Kill Switch.
3. **Interactive Scam Lab**: 5 real-world fraud scenarios for on-demand judge and family rehearsal.
4. **Caregiver Monetization Stack**: RevenueCat 3-tier model (Free / Pro $4.99 / Ultra $11.99) + Stripe Web-to-App quiz funnel (`/funnel.html`) + OneSignal retention journeys.

## URLs (fill after deploy)
- Simulator (Cloudflare Pages): `https://REPLACE.pages.dev`
- Caregiver Funnel: `https://REPLACE.pages.dev/funnel.html`
- Backend (HF Space): `https://REPLACE.hf.space` · MCP: `/mcp` · REST: `/api/chat`
- Demo video (<3 min, public): `https://youtube.com/REPLACE`

## Run locally
```bash
pip install -r mcp_server/requirements.txt
python skills/kavach-guardian/scripts/seed_demo.py
uvicorn app:app --port 7860            # / -> fallback, /api/chat, /mcp, /docs
cd simulator/web && npm i && npm run dev   # http://localhost:5173
```

Try: “Something strange happened — a call about my bank” → answer 4 short questions
→ verdict with cited red flags → family board updates live.

## Deploy
Backend → Hugging Face Spaces (Docker, free, no CC): push, set `GEMINI_API_KEY`
(optional — protocol templates work offline), add Space + Pages URLs to
`ALLOWED_ORIGINS`. Verify `/healthz`, `/readyz`, Inspector on `/mcp`.
Frontend → Cloudflare Pages: build `simulator/web/dist`, set `VITE_API_BASE`.
Full runbook: `docs/DEPLOY.md`. API: `docs/API.md`. Design: `docs/ARCHITECTURE.md`.

## Safety scope (read this)
Kavach is a companion + escalation aid, not medical/legal/financial advice. It never
diagnoses, never prescribes, never sends anything without the confirmation ceremony.
Demo household is fictional. See `docs/ARCHITECTURE.md` § safety.
