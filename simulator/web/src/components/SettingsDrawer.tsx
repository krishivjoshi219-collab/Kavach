import { useState } from 'react'
import { defaultApiBase, getApiBase, getSeniorId, mcpUrl, setApiBase, setSeniorId } from '../lib/api'

export default function SettingsDrawer({
  sessionId, seniorId, onSenior, onNewSession, apiBase, onApiBase
}: {
  sessionId: string
  seniorId: string
  onSenior: (v: string) => void
  onNewSession: () => void
  apiBase: string
  onApiBase: (v: string) => void
}) {
  const [draft, setDraft] = useState(apiBase)
  const [seniorDraft, setSeniorDraft] = useState(seniorId)
  const base = getApiBase()
  return (
    <div className="drawer">
      <b>⚙ Settings &amp; backend</b>
      <label htmlFor="apibase">Backend URL (HF Space or local)</label>
      <div style={{ display: 'flex', gap: 8 }}>
        <input id="apibase" value={draft} onChange={e => setDraft(e.target.value)}
          placeholder={defaultApiBase()} spellCheck={false} />
        <button className="iconbtn" style={{ color: '#2b2118', borderColor: '#c9b892' }}
          onClick={() => {
            const v = draft.trim()
            setApiBase(v)
            onApiBase(v || defaultApiBase())
          }}>
          Save
        </button>
      </div>
      <label htmlFor="seniorid">Senior profile id</label>
      <div style={{ display: 'flex', gap: 8 }}>
        <input id="seniorid" value={seniorDraft} onChange={e => setSeniorDraft(e.target.value)}
          placeholder={getSeniorId()} spellCheck={false} />
        <button className="iconbtn" style={{ color: '#2b2118', borderColor: '#c9b892' }}
          onClick={() => {
            const v = seniorDraft.trim() || 'demo-senior'
            setSeniorId(v)
            onSenior(v)
          }}>
          Switch
        </button>
      </div>
      <div className="links">
        <a href={`${base}/healthz`} target="_blank" rel="noreferrer">healthz</a>
        <a href={`${base}/readyz`} target="_blank" rel="noreferrer">readyz</a>
        <a href={`${base}/metrics`} target="_blank" rel="noreferrer">metrics</a>
        <a href={`${base}/version`} target="_blank" rel="noreferrer">version</a>
        <a
          href={`${base}/api/family-feed?senior_id=${encodeURIComponent(seniorId)}`}
          target="_blank"
          rel="noreferrer"
        >
          family-feed
        </a>
        <a href={`${base}/apps/family-board.html`} target="_blank" rel="noreferrer">board app</a>
        <a href={mcpUrl()} target="_blank" rel="noreferrer" title="MCP endpoint (POST Streamable HTTP)">mcp</a>
        <a href={`${base}/docs`} target="_blank" rel="noreferrer">api docs</a>
      </div>
      <div className="row">
        <span className="badge" style={{ color: '#7a6a55', borderColor: '#c9b892' }}
          title="conversation scope">session {sessionId.slice(0, 14)}…</span>
        <button className="iconbtn" style={{ color: '#2b2118', borderColor: '#c9b892' }} onClick={onNewSession}>
          ＋ new conversation
        </button>
      </div>
    </div>
  )
}
