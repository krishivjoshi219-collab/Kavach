# Deploy Runbook — Kavach (no credit card, $0)

## Backend → Hugging Face Spaces (Docker)
1. Create a **Docker** Space (blank).
2. Env: `GEMINI_API_KEY` (optional — protocol templates work fully offline),
   `ALLOWED_ORIGINS=https://<pages>.pages.dev,https://<space>.hf.space`.
   Optional lockdown: `MCP_ALLOWED_HOSTS=<space>.hf.space`.
3. Push the repo (Dockerfile at root serves `:7860`, `DB_PATH=/data/kavach.db`).
4. Verify in order: `/healthz` → `/readyz` (`ready:true`, cold start 30–60s first hit)
   → Inspector on `https://<space>.hf.space/mcp` (11 tools + `ui://` resource)
   → `POST /api/chat {"text":"Something strange happened","session_id":"demo"}`.
5. Warm `/healthz` ~1 min before demos/recordings. The video is ground truth.

## Frontend → Cloudflare Pages
1. `cd simulator/web && npm ci && npm run build` → `dist/`.
2. New Pages project from `dist/` (or repo: build `npm run build`, output `dist/`).
3. Env: `VITE_API_BASE=https://<space>.hf.space`, `VITE_MCP_URL=https://<space>.hf.space/mcp`.
4. Add the Pages URL to backend `ALLOWED_ORIGINS`. `_headers` grants mic for 🎤 Talk.

## Local prod parity
`docker compose up --build` → `http://localhost:7860`. Frontend dev: `npm run dev`.

## Env reference
| var | default | notes |
|---|---|---|
| `GEMINI_API_KEY` / `GROQ_API_KEY` | — | narration only; verdicts never depend on them |
| `KAVACH_SENIOR_ID` | demo-senior | default household |
| `ALLOWED_ORIGINS` | localhost:5173,7860 | add Pages + Space URLs |
| `MCP_ALLOWED_HOSTS` / `SPACE_HOST` | — | set to enable MCP DNS lockdown |
| `RATE_LIMIT_PER_MIN` | 30 | per-IP on `/api/chat` |
| `MAX_INPUT_CHARS` | 8000 | input cap |
| `DB_PATH` | ./kavach.db | `/data/kavach.db` hosted |
| `LOG_LEVEL` / `APP_VERSION` | info / 0.1.0 | surfaced at `/version` |
