# Product Feedback (mandatory per rules — one block per tool/API/SDK)

## 1. MCP Python SDK (`mcp>=1.12,<2`, FastMCP Streamable HTTP, spec 2025-11-25)
- Used for: 11 guardian tools + `ui://kavach-family-board` resource with `_meta.ui`
  linkage (MCP Apps extension `io.modelcontextprotocol/ui`).
- Worked well: `stateless_http=True` fits serverless hosts; `resource(mime_type=...)`
  + tool `meta=` made the MCP App linkage expressible in pure Python; Inspector
  verified handshake, tools/list, resources/list, tools/call first try.
- Needs work: no first-class MCP Apps authoring helper in the Python SDK (hand-built
  per spec); `session_manager.run()` single-entry rule surprised us in tests;
  DNS-rebinding defaults are localhost-only (we ship open-demo + opt-in lockdown).
- Zero→hello-world: ~1h to first Inspector-verified tool.
- Build again? Yes — the right primitive for Alexa+ skills.

## 2. MCP Apps extension (Jan 2026, `ui://` + postMessage bridge)
- Used for: interactive family board rendered from a tool result.
- Worked well: text fallback keeps non-UI hosts working; iframe sandbox model is sane.
- Needs work: host support matrix is still growing; authoring docs assume TypeScript.
- Build again? Yes — highest novelty-per-line in this project.

## 3. Google Gemini 2.0 Flash (AI Studio free tier, no CC) / Groq fallback
- Used for: narration only (warm rephrasing). Verdicts and stages never depend on it.
- Worked well: fast, free, fine at low temperature for tone.
- Needs work: 429s under bursts → Groq failover + template fallback; narration must be
  constrained or it invents facts (we cage it: rephrase-only system prompt).
- Build again? Yes, caged as narrator, never as decider.

## 4. Hugging Face Spaces (Docker, no CC)
- Used for: public Python backend (`/mcp` + `/api/*` + board app).
- Worked well: free Docker, env vars, public URL. Cold starts 30–60s (documented).
- Build again? Yes for Python MCP demos.

## 5. Cloudflare Pages (simulator)
- Used for: two-face web app (senior voice view + family board + AppBridge embed).
- Worked well: instant deploys, mic permission via `_headers`, SPA `_redirects`.
- Build again? Yes — ideal demo frontend.
