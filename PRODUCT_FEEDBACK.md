# Product Feedback (mandatory per rules — one block per tool/API/SDK)

## 1. MCP Python SDK (`mcp>=1.12`, FastMCP Streamable HTTP, spec 2025-11-25)
- Used for: 6 tools (`get_pipeline_status`, `triage_and_heal_incident`, `verify_code_file`,
  `inspect_repo_structure`, `execute_command`, `propose_patch`) at `/mcp`.
- Worked well: `FastMCP(stateless_http=True)` + `streamable_http_app()` mount under FastAPI;
  Inspector connects first try; `@mcp.tool()` auto-schema from type hints.
- Needs work: stateless mode + session memory must be hand-wired (we use SQLite);
  version pinning across `2025-11-25` drafts is confusing in docs.
- Zero→hello-world: ~1h (pip install, 2 tools, Inspector).
- Build again? Yes — correct primitive for Alexa+ Agent Skills.

## 2. Google Gemini 2.0 Flash (AI Studio free tier, no CC)
- Used for: general-turn reasoning + voice shortening; deterministic router handles triage offline.
- Worked well: fast, generous free quota, OpenAI-style quick start.
- Needs work: 429s under bursts → we added Groq fallback + offline stub; JSON mode not enforced.
- Zero→hello-world: 15 min with API key.
- Build again? Yes — best $0 brain for hackathons.

## 3. Groq Llama-3.3-70B (free fallback)
- Used for: failover when Gemini 429s via OpenAI-compatible endpoint.
- Worked well: low latency, no CC.
- Needs work: smaller context; must truncate history to 6 turns.
- Build again? Yes, as fallback only.

## 4. Hugging Face Spaces (Docker)
- Used for: public Python backend (`/mcp` + `/api/chat` + fallback `/`).
- Worked well: free Docker, env vars, public URL, no CC.
- Needs work: cold starts 30–60s (documented; video is proof); disk is ephemeral → SQLite on `/data`.
- Zero→hello-world: ~30 min pushing Dockerfile.
- Build again? Yes for Python MCP demos.

## 5. Cloudflare Pages (simulator web)
- Used for: Vite React Alexa+ simulator (voice + cards/carousel).
- Worked well: instant deploys, unlimited bandwidth, env-based API base.
- Needs work: must sync CORS allowlist with backend on each new domain.
- Build again? Yes — ideal demo frontend.
