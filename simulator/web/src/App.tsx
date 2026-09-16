import { useCallback, useEffect, useRef, useState } from 'react'
import { GenericCard, ToolTimeline } from './components/Cards'
import Composer from './components/Composer'
import HealthPill from './components/HealthPill'
import SettingsDrawer from './components/SettingsDrawer'
import {
  fetchVersion, getApiBase, getSessionId, postChat, resetSessionId,
  type ChatResponse, type Turn
} from './lib/api'
import { speak } from './lib/voice'

const HIST_KEY = 'kv_history'

function loadHistory(): Turn[] {
  try {
    const raw = localStorage.getItem(HIST_KEY)
    if (!raw) return []
    const arr = JSON.parse(raw) as Turn[]
    return Array.isArray(arr) ? arr.slice(-20) : []
  } catch {
    return []
  }
}

export default function App() {
  const [turns, setTurns] = useState<Turn[]>(loadHistory)
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [settings, setSettings] = useState(false)
  const [apiBase, setApiBase] = useState(getApiBase)
  const [sessionId, setSessionId] = useState(getSessionId)
  const [llmMode, setLlmMode] = useState('')
  const noticeTimer = useRef<number | null>(null)
  const bottom = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchVersion().then(v => {
      if (v) setLlmMode(v.llm.mode)
    })
  }, [apiBase])

  useEffect(() => {
    try {
      localStorage.setItem(HIST_KEY, JSON.stringify(turns.slice(-20)))
    } catch { /* private mode */ }
    bottom.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [turns, busy])

  const flash = useCallback((m: string) => {
    setNotice(m)
    if (noticeTimer.current) window.clearTimeout(noticeTimer.current)
    noticeTimer.current = window.setTimeout(() => setNotice(''), 6000)
  }, [])

  async function ask(text: string) {
    setBusy(true)
    setNotice('')
    const id = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`
    try {
      const resp: ChatResponse = await postChat(text, sessionId)
      setTurns(t => [...t.slice(-19), { id, q: text, at: Date.now(), resp }])
      speak(resp.spoken)
    } catch (e) {
      flash(e instanceof Error ? e.message : String(e))
    }
    setBusy(false)
  }

  function copyId(id: string) {
    try {
      const nav = navigator as Navigator & { clipboard?: { writeText(s: string): Promise<void> } }
      if (nav.clipboard) nav.clipboard.writeText(id).then(() => flash('request id copied ✓'))
      else flash(id)
    } catch {
      flash(id)
    }
  }

  return (
    <div className="wrap">
      <header className="hero">
        <div className="hero-top">
          <div className="brand">
            <span className="ring" aria-hidden>◉</span>
            K-VoiceOps · Alexa+ Simulator
          </div>
          <span className="spacer" />
          <button className="iconbtn" onClick={() => setSettings(s => !s)} aria-expanded={settings}>
            ⚙ {settings ? 'hide' : 'settings'}
          </button>
        </div>
        <p className="sub">
          Voice DevOps triage → AST-verified patches · real MCP (Streamable HTTP, spec 2025-11-25)
        </p>
        <div className="badges">
          <span className="badge hot">Alexa+ Track</span>
          <HealthPill llmMode={llmMode} />
        </div>
      </header>

      {settings && (
        <SettingsDrawer
          sessionId={sessionId}
          apiBase={apiBase}
          onApiBase={v => {
            setApiBase(v)
            flash(`Backend set to ${v}`)
          }}
          onNewSession={() => {
            setSessionId(resetSessionId())
            flash('New session started — memory is fresh.')
          }}
          onClear={() => {
            setTurns([])
            try {
              localStorage.removeItem(HIST_KEY)
            } catch { /* noop */ }
          }}
        />
      )}

      <Composer busy={busy} onAsk={ask} onNotice={flash} />
      {notice && <div className="notice" role="status">{notice}</div>}

      {turns.length === 0 && !busy && (
        <div className="empty">
          <h3 style={{ margin: '0 0 6px' }}>Ask about a broken deploy — get a verified fix.</h3>
          <p className="sub" style={{ margin: 0 }}>
            The simulator talks to the same agent as the MCP server. Pick a prompt above or speak.
          </p>
          <div className="steps">
            <div className="step"><b>1 · Voice / text</b>“Alexa, why did my deploy fail?”</div>
            <div className="step"><b>2 · MCP tools</b>pipeline status → log triage → AST verify</div>
            <div className="step"><b>3 · Verified patch</b>diff card + spoken summary, tests cited</div>
          </div>
        </div>
      )}

      <main aria-live="polite">
        {turns.map(t => (
          <div className="turn" key={t.id}>
            <div className="user">🧑 {t.q}</div>
            <div className="alexa">
              <p className="spoken">🔵 {t.resp.spoken}</p>
              <div className="meta">
                <span>{t.resp.provider}</span>
                {t.resp.latency_ms != null && <span>{t.resp.latency_ms}ms</span>}
                {t.resp.request_id && (
                  <button onClick={() => t.resp.request_id && copyId(t.resp.request_id)}>
                    #{t.resp.request_id} ⧉
                  </button>
                )}
                <button onClick={() => speak(t.resp.spoken)}>🔊 replay</button>
              </div>
              {t.resp.cards.length > 0 && (
                <div className="cards">
                  {t.resp.cards.map((c, i) => (
                    <GenericCard key={i} c={c} />
                  ))}
                </div>
              )}
              <ToolTimeline tools={t.resp.tools} />
            </div>
          </div>
        ))}
        {busy && (
          <div className="turn">
            <div className="alexa"><p className="spoken">🔵 Working — running MCP tools…</p></div>
          </div>
        )}
        <div ref={bottom} />
      </main>

      <footer>
        Backend {apiBase} · MCP {apiBase.replace(/\/$/, '')}/mcp · cards + voice run fully client-side
      </footer>
    </div>
  )
}
