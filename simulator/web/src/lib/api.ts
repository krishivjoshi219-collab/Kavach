export type Card = { type: string; title: string; body: string }
export type ChatResponse = {
  spoken: string
  text: string
  cards: Card[]
  tools: string[]
  provider: string
  request_id?: string
  latency_ms?: number
  incident_id?: number
  verdict?: string
  stage?: string
  done?: boolean
  confirm_code?: string
}
export type Turn = { id: string; q: string; at: number; resp: ChatResponse }
export type VersionInfo = {
  service: string
  version: string
  mcp_spec: string
  mcp_app: string
  llm: { mode: string }
  endpoints: string[]
}
export type FeedIncident = {
  id: number; verdict: string; channel: string; status: string
  caller_claim: string; red_flags: Array<{ label: string; meaning: string }>; created: number
}
export type Feed = {
  senior: { id: string; name: string; language: string }
  incidents: FeedIncident[]
  routines: Array<{ id: number; label: string; expected_time: string; last_confirmed: number | null; streak: number }>
  checkins: Array<{ kind: string; note: string; mood: string; created: number }>
  alerts: Array<{ id: number; kind: string; title: string; status: string }>
  contacts: Array<{ label: string; kind: string }>
}

const LS_API = 'kavach_api_base'
const LS_SENIOR = 'kavach_senior'

export function defaultApiBase(): string {
  const env = (import.meta as unknown as { env?: Record<string, string> }).env
  return env?.VITE_API_BASE || 'http://localhost:7860'
}

export function getApiBase(): string {
  try {
    return (localStorage.getItem(LS_API) || defaultApiBase()).replace(/\/$/, '')
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

export function getSeniorId(): string {
  try {
    return localStorage.getItem(LS_SENIOR) || 'demo-senior'
  } catch {
    return 'demo-senior'
  }
}

export function setSeniorId(v: string) {
  try {
    localStorage.setItem(LS_SENIOR, v)
  } catch { /* noop */ }
}

export function mcpUrl(): string {
  const env = (import.meta as unknown as { env?: Record<string, string> }).env
  if (env?.VITE_MCP_URL) return env.VITE_MCP_URL
  return `${getApiBase()}/mcp`
}

export async function postChat(text: string, sessionId: string, seniorId: string): Promise<ChatResponse> {
  const r = await fetch(`${getApiBase()}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, session_id: sessionId, senior_id: seniorId })
  })
  if (!r.ok) {
    const body = await r.text().catch(() => '')
    throw new Error(`kavach backend ${r.status}: ${body.slice(0, 200) || r.statusText}`)
  }
  return (await r.json()) as ChatResponse
}

export async function fetchFeed(seniorId: string): Promise<Feed> {
  const r = await fetch(`${getApiBase()}/api/family-feed?senior_id=${encodeURIComponent(seniorId)}`, { cache: 'no-store' })
  if (!r.ok) throw new Error(`feed ${r.status}`)
  return (await r.json()) as Feed
}

export async function fetchHealth(): Promise<{ ok: boolean; ms: number }> {
  const t0 = Date.now()
  const r = await fetch(`${getApiBase()}/healthz`, { cache: 'no-store' })
  if (!r.ok) throw new Error(`health ${r.status}`)
  return { ok: true, ms: Date.now() - t0 }
}

export async function fetchVersion(): Promise<VersionInfo | null> {
  try {
    const r = await fetch(`${getApiBase()}/version`, { cache: 'no-store' })
    if (!r.ok) return null
    return (await r.json()) as VersionInfo
  } catch {
    return null
  }
}

export function newSessionId(): string {
  return `s-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`
}

export function getSessionId(): string {
  try {
    let s = localStorage.getItem('kavach_session')
    if (!s) {
      s = newSessionId()
      localStorage.setItem('kavach_session', s)
    }
    return s
  } catch {
    return 's-ephemeral'
  }
}

export function resetSessionId(): string {
  const s = newSessionId()
  try {
    localStorage.setItem('kavach_session', s)
  } catch { /* noop */ }
  return s
}
