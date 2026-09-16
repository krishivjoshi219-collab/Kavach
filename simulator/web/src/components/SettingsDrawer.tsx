import { useState } from 'react'
import { defaultApiBase, getApiBase, mcpUrl, setApiBase } from '../lib/api'

export default function SettingsDrawer({
  sessionId, onNewSession, onClear, apiBase, onApiBase
}: {
  sessionId: string
  onNewSession: () => void
  onClear: () => void
  apiBase: string
  onApiBase: (v: string) => void
}) {
  const [draft, setDraft] = useState(apiBase)
  const base = getApiBase().replace(/\/$/, '')
  return (
    <div className="drawer">
      <b>⚙ Settings &amp; backend</b>
      <label htmlFor="apibase">Backend URL (HF Space or local)</label>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          id="apibase"
          value={draft}
          onChange={e => setDraft(e.target.value)}
          placeholder={defaultApiBase()}
          spellCheck={false}
        />
        <button
          className="iconbtn"
          onClick={() => {
            const v = draft.trim()
            setApiBase(v)
            onApiBase(v || defaultApiBase())
          }}
        >
          Save
        </button>
      </div>
      <div className="links">
        <a href={`${base}/healthz`} target="_blank" rel="noreferrer">healthz</a>
        <a href={`${base}/readyz`} target="_blank" rel="noreferrer">readyz</a>
        <a href={`${base}/metrics`} target="_blank" rel="noreferrer">metrics</a>
        <a href={`${base}/version`} target="_blank" rel="noreferrer">version</a>
        <a href={mcpUrl()} target="_blank" rel="noreferrer" title="MCP endpoint (POST Streamable HTTP)">
          mcp endpoint
        </a>
        <a href={`${base}/docs`} target="_blank" rel="noreferrer">api docs</a>
      </div>
      <div className="row">
        <span className="badge" title="memory scope">session {sessionId.slice(0, 18)}…</span>
        <button className="iconbtn" onClick={onNewSession}>＋ new session</button>
        <button className="iconbtn" onClick={onClear}>🗑 clear history</button>
      </div>
    </div>
  )
}
