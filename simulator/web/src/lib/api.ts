export type Card = { type: string; title: string; body: string }
export type ChatResponse = {
  spoken: string
  text: string
  cards: Card[]
  tools: string[]
  provider: string
  request_id?: string
  latency_ms?: number
}
export type Turn = { id: string; q: string; at: number; resp: ChatResponse }
export type VersionInfo = {
  service: string
  version: string
  mcp_spec: string
  llm: { mode: string }
  endpoints: string[]
}

const LS_API = 'kv_api_base'

export function defaultApiBase(): string {
  const env = (import.meta as unknown as { env?: Record<string, string> }).env
  return env?.VITE_API_BASE || 'http://localhost:7860'
}

export function getApiBase(): string {
  try {
    return localStorage.getItem(LS_API) || defaultApiBase()
  } catch {
    return defaultApiBase()
  }
}

export function setApiBase(v: string) {
  try {
    if (v && v !== defaultApiBase()) localStorage.setItem(LS_API, v)
    else localStorage.removeItem(LS_API)
  } catch { /* private mode */ }
}

export function mcpUrl(): string {
  const env = (import.meta as unknown as { env?: Record<string, string> }).env
  if (env?.VITE_MCP_URL) return env.VITE_MCP_URL
  return `${getApiBase().replace(/\/$/, '')}/mcp`
}

export async function postChat(text: string, sessionId: string): Promise<ChatResponse> {
  const r = await fetch(`${getApiBase().replace(/\/$/, '')}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, session_id: sessionId })
  })
  if (!r.ok) {
    const body = await r.text().catch(() => '')
    throw new Error(`backend ${r.status}: ${body.slice(0, 200) || r.statusText}`)
  }
  return (await r.json()) as ChatResponse
}

export async function fetchHealth(): Promise<{ ok: boolean; ms: number }> {
  const t0 = Date.now()
  const r = await fetch(`${getApiBase().replace(/\/$/, '')}/healthz`, { cache: 'no-store' })
  if (!r.ok) throw new Error(`health ${r.status}`)
  return { ok: true, ms: Date.now() - t0 }
}

export async function fetchVersion(): Promise<VersionInfo | null> {
  try {
    const r = await fetch(`${getApiBase().replace(/\/$/, '')}/version`, { cache: 'no-store' })
    if (!r.ok) return null
    return (await r.json()) as VersionInfo
  } catch {
    return null
  }
}

export function newSessionId(): string {
  return `web-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`
}

export function getSessionId(): string {
  try {
    let s = localStorage.getItem('kv_session')
    if (!s) {
      s = newSessionId()
      localStorage.setItem('kv_session', s)
    }
    return s
  } catch {
    return 'web-ephemeral'
  }
}

export function resetSessionId(): string {
  const s = newSessionId()
  try {
    localStorage.setItem('kv_session', s)
  } catch { /* noop */ }
  return s
}
