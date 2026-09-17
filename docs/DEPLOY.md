# Deploy Runbook — Kavach E2E relay (no credit card, $0, no website)

Backend only. No Pages, no domain, no store needed for Next Gen (video + code).

## Recommended: Render Free (public relay, no card)

1. Push repo to GitHub. Render → New → Web Service → select repo.
2. Build: Dockerfile at root. No build command needed.
3. Env (all optional — empty = offline verdicts + TEST MODE billing):
   - `ALLOWED_ORIGINS=*` (demo) or locked origins later
   - `GEMINI_API_KEY` / `GROQ_API_KEY` (narration only; verdicts never depend on them)
   - `RC_WEBHOOK_AUTH` (empty = webhook TEST MODE with promo unlock)
   - `DB_PATH` defaults to `/data/kavach.db` (ephemeral disk — reseeds on restart; fine for demo)
4. Render injects `$PORT` — image honors it with 7860 fallback. Health check path: `/healthz`.
5. Verify: `GET /readyz` → `ready:true` (30-50s cold first hit), then `scripts/warm.sh https://<you>.onrender.com`.
6. Point both APK flavors at it: `BuildConfig.KAVACH_API = https://<you>.onrender.com`.
7. Warm `/healthz` ~1 min before demos/recordings. The video is ground truth.

## Local parity (recording, deterministic, no sleep)

`docker compose up --build` → `http://localhost:7860`. Then `scripts/warm.sh`.

## Backups (no card)

- SnapDeploy free Docker (10 deploys/day, auto-wake) — same image.
- Back4app Containers free — same image.
- Cloudflare Tunnel from laptop — emergency public URL only.

## Skip (card required)

HF Docker Spaces (now PRO-only), Koyeb (card hold), Oracle/Fly/Cloud Run (cards).

## Env reference
| var | default | notes |
|---|---|---|
| `GEMINI_API_KEY` / `GROQ_API_KEY` | — | narration only; verdicts never depend on them |
| `KAVACH_SENIOR_ID` | demo-senior | default household |
| `ALLOWED_ORIGINS` | localhost:5173,localhost:7860 | `*` for demo relay |
| `MCP_ALLOWED_HOSTS` / `SPACE_HOST` | — | MCP DNS lockdown (dormant unless /mcp exposed) |
| `RATE_LIMIT_PER_MIN` | 30 | per-IP on `/api/chat` + demo/challenge |
| `MAX_INPUT_CHARS` | 8000 | input cap |
| `DB_PATH` | ./kavach.db | `/data/kavach.db` hosted (ephemeral on free tier) |
| `RC_WEBHOOK_AUTH` | — | empty = TEST MODE; set Bearer to enforce |
| `LOG_LEVEL` / `APP_VERSION` | info / 0.1.0 | surfaced at `/version` |
