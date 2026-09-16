# K-VoiceOps for Alexa+ — Voice DevOps Triage (Hybrid: Real MCP + Simulated UI)

Production endpoints: `/healthz` `/readyz` `/version` `/metrics` `/api/chat` `/mcp` `/mcp/` `/docs` — full reference in `docs/API.md`, deploy runbook in `docs/DEPLOY.md`, architecture in `docs/ARCHITECTURE.md`.

> Alexa+ Track entry. Ask “Alexa, why did my deploy fail?” → real MCP server (Streamable HTTP,
> spec `2025-11-25`) runs AST-verified triage → simulated Alexa+ web UI shows voice + cards/carousel.

## URLs (fill after deploy)
- Simulator (Cloudflare Pages): `https://REPLACE.pages.dev`
- Backend (HF Space): `https://REPLACE.hf.space` · MCP: `/mcp` · REST: `/api/chat` · Health: `/healthz`
- Demo video (<3 min, public): `https://youtube.com/REPLACE`

## Run locally
```bash
pip install -r mcp_server/requirements.txt
uvicorn app:app --port 7860            # / -> fallback UI, /api/chat, /mcp, /healthz
# simulator:
cd simulator/web && npm i && VITE_API_BASE=http://localhost:7860 npm run dev
```

## Deploy
**Backend → Hugging Face Spaces (Docker, free, no CC):**
1. Create Space (Docker blank), set env `GEMINI_API_KEY` (free AI Studio key), optional `GROQ_API_KEY`.
2. Push this repo (or `Dockerfile`+`app.py`+`agent/`+`mcp_server/`). Space serves `:7860`.
3. Verify `GET /healthz`, MCP Inspector → `https://<space>.hf.space/mcp` (bare path works;
   `/mcp/` also works; Streamable HTTP, spec 2025-11-25, 6 tools).
4. Optional lockdown: set `MCP_ALLOWED_HOSTS=<space>.hf.space` (enables DNS-rebinding
   protection); default is open demo mode so any HF hostname works.
5. Update `alexa_skill/skill.json` endpoint + this README.

**Frontend → Cloudflare Pages (free, unlimited bandwidth):**
1. `cd simulator/web && npm run build` → deploy `dist/`.
2. Env: `VITE_API_BASE=https://<space>.hf.space`, `VITE_MCP_URL=https://<space>.hf.space/mcp`.
3. Add Pages domain to backend `ALLOWED_ORIGINS`.

## What judges test
- `POST /api/chat {"text":"why did my deploy fail?","session_id":"demo"}` → spoken + cards + tool trace.
- MCP Inspector on `/mcp`: `get_pipeline_status`, `triage_and_heal_incident`, `verify_code_file`.
- Video shows voice → MCP logs → verified patch card.

## Stack (no AWS, no credit card)
Python FastMCP + FastAPI + SQLite memory + Gemini Flash (free) / Groq fallback / offline stub.
See `PRODUCT_FEEDBACK.md`, `FRICTION_LOG.md`, `DEMO.md`, `OPEN_SOURCE.md`, `docs/`.
