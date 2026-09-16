"""Real MCP server: Streamable HTTP, MCP spec 2025-11-25. Runtime hook for Alexa+ track."""
from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from agent import tools_ops


def _transport_security() -> TransportSecuritySettings:
    """DNS-rebinding protection config that works on localhost AND hosted domains.

    The MCP SDK only supports exact hosts and `host:*` port-wildcards (no `*.domain`
    globs), and its default allowlist is localhost-only — which would 421 every
    request on HF Spaces (`<space>.hf.space`). So:
    - If MCP_ALLOWED_HOSTS / SPACE_HOST is set: enable protection with
      localhost defaults + those exact hosts.
    - Else: disable DNS-rebinding checks (public demo MCP, no auth/cookies;
      set MCP_ENABLE_DNS_PROTECTION=1 to force localhost-only lockdown).
    """
    extra = [h.strip() for h in os.getenv("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]
    space_host = os.getenv("SPACE_HOST", "").strip()
    if space_host:
        extra.append(space_host)
    force_on = os.getenv("MCP_ENABLE_DNS_PROTECTION") == "1"
    force_off = os.getenv("MCP_DISABLE_DNS_PROTECTION") == "1"
    if (extra or force_on) and not force_off:
        hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*",
                 "127.0.0.1", "localhost"]
        for h in extra:
            hosts += [h] if h in hosts else [h, f"{h}:*"] if ":" not in h else [h]
        return TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=hosts,
            allowed_origins=["http://localhost:*"] + [f"https://{h}" for h in extra],
        )
    return TransportSecuritySettings(enable_dns_rebinding_protection=False)


mcp = FastMCP("k-voiceops", stateless_http=True, streamable_http_path="/",
              transport_security=_transport_security())


@mcp.tool()
def get_pipeline_status(name: str = "demo-web") -> dict:
    """Get CI pipeline status (demo-web | demo-api)."""
    r = tools_ops.get_pipeline_status(name)
    return {"ok": r.ok, "summary": r.summary, "data": r.data}


@mcp.tool()
def verify_code_file(code: str, language: str = "python") -> dict:
    """Verify code via AST parse + compiler ground truth."""
    r = tools_ops.verify_code_file(code=code, language=language)
    return {"ok": r.ok, "summary": r.summary, "data": r.data}


@mcp.tool()
def inspect_repo_structure(root: str = ".", max_entries: int = 60) -> dict:
    """List repo files safely (skips .git/node_modules/dist)."""
    r = tools_ops.inspect_repo_structure(root, max_entries)
    return {"ok": r.ok, "summary": r.summary, "data": r.data}


@mcp.tool()
def execute_command(command: str, cwd: str = ".", timeout_seconds: int = 30) -> dict:
    """Run a sandboxed shell command (denylist-guarded, timeout-enforced)."""
    r = tools_ops.execute_command(command, cwd, timeout_seconds)
    return {"ok": r.ok, "summary": r.summary, "data": r.data}


@mcp.tool()
def triage_and_heal_incident(log: str, language: str = "python") -> dict:
    """Triage a failure log -> culprit -> verified patch (max 3 attempts)."""
    r = tools_ops.triage_and_heal_incident(log, language)
    return {"ok": r.ok, "summary": r.summary, "data": r.data}


@mcp.tool()
def propose_patch(before: str, after: str) -> dict:
    """Diff before/after and verify the patched code."""
    r = tools_ops.propose_patch(before, after)
    return {"ok": r.ok, "summary": r.summary, "data": r.data}


# Helper kept for `mcp dev` style standalone runs.
def build_mcp_subapp():
    return mcp.streamable_http_app()
