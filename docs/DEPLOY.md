# Deploy Runbook (no credit card, $0)

## Backend → Hugging Face Spaces (Docker)
1. Create a **Docker** Space (blank). Copy the Space ID, e.g. `user/k-voiceops`.
2. Space env vars: `GEMINI_API_KEY` (free AI Studio key; optional — offline stub works
   without it), `GROQ_API_KEY` (optional failover), `ALLOWED_ORIGINS`
   (`https://<pages>.pages.dev,https://<space>.hf.space`).
   Optional lockdown: `MCP_ALLOWED_HOSTS=<space>.hf.space`.
3. Push: `git push` the repo (Dockerfile at root, serves `:7860`).
4. Verify, in order:
   - `GET https://<space>.hf.space/healthz` → `{"ok": true, ...}`
   - `GET https://<space>.hf.space/readyz` → `{"ready": true, ...}` (cold start 30–60s first hit)
   - MCP Inspector → `https://<space>.hf.space/mcp`, Streamable HTTP → 6 tools listed
   - `POST /api/chat {"text":"why did my deploy fail?","session_id":"demo"}` → cards + trace
5. Cold starts: hit `/healthz` ~1 min before demos/recordings. The video is ground truth.

## Frontend → Cloudflare Pages
1. `cd simulator/web && npm ci && npm run build` → `dist/`.
2. Pages project → upload `dist/` (or connect repo, build cmd `npm run build`, output `dist/`).
3. Env: `VITE_API_BASE=https://<space>.hf.space`, `VITE_MCP_URL=https://<space>.hf.space/mcp`.
4. Add the Pages URL to backend `ALLOWED_ORIGINS` and redeploy backend.
5. `_headers` grants mic to the page for 🎤 Talk; `_redirects` keeps SPA routing.

## Local prod parity
`docker compose up --build` → `http://localhost:7860` (healthz/readyz/metrics/docs).
Frontend dev: `cd simulator/web && npm i && npm run dev` (uses `VITE_API_BASE` or Settings override).

## Env reference
| var | default | notes |
|---|---|---|
| `GEMINI_API_KEY` | — | free AI Studio key; offline stub when empty |
| `GROQ_API_KEY` | — | free failover when Gemini 429s |
| `ALLOWED_ORIGINS` | localhost:5173,7860 | add Pages + Space URLs |
| `MCP_ALLOWED_HOSTS` / `SPACE_HOST` | — | set to enable MCP DNS-protection lockdown |
| `RATE_LIMIT_PER_MIN` | 30 | per-IP on `/api/chat` |
| `MAX_INPUT_CHARS` | 8000 | input cap |
| `DB_PATH` | ./voiceops.db | `/data/voiceops.db` on HF/compose |
| `LOG_LEVEL` | info | |
| `APP_VERSION` | 0.2.0 | surfaced at `/version` |
