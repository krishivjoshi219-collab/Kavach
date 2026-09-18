import { useEffect, useState } from 'react'
import FamilyBoard from './components/FamilyBoard'
import HealthPill from './components/HealthPill'
import SeniorView from './components/SeniorView'
import SettingsDrawer from './components/SettingsDrawer'
import { fetchVersion, getApiBase, getSeniorId, getSessionId, resetSessionId } from './lib/api'

export default function App() {
  const [face, setFace] = useState<'senior' | 'family'>('senior')
  const [settings, setSettings] = useState(false)
  const [apiBase, setApiBase] = useState(getApiBase)
  const [seniorId, setSeniorId] = useState(getSeniorId)
  const [sessionId, setSessionId] = useState(getSessionId)
  const [llmMode, setLlmMode] = useState('')
  const [notice, setNotice] = useState('')

  useEffect(() => {
    fetchVersion().then(v => {
      if (v) setLlmMode(v.llm.mode)
    })
  }, [apiBase])

  return (
    <div className="wrap">
      <header className="hero">
        <div className="hero-top">
          <div className="brand"><span className="mark">🛡️</span> Kavach</div>
          <span className="spacer" />
          <button className="iconbtn" onClick={() => setSettings(s => !s)} aria-expanded={settings}>
            ⚙ {settings ? 'hide' : 'settings'}
          </button>
        </div>
        <p className="sub">
          A voice guardian for seniors — pause pressure, verify independently, bring trusted family.
          No call uploads. Test mode: no charges.
        </p>
        <div className="badges">
          <span className="badge hot">Next Gen</span>
          <span className="badge test">TEST MODE</span>
          <HealthPill llmMode={llmMode} />
        </div>
      </header>

      {settings && (
        <SettingsDrawer
          sessionId={sessionId}
          seniorId={seniorId}
          onSenior={v => {
            setSeniorId(v)
            setNotice(`Switched to household “${v}”.`)
          }}
          apiBase={apiBase}
          onApiBase={v => {
            setApiBase(v)
            setNotice(`Backend set to ${v}`)
          }}
          onNewSession={() => {
            setSessionId(resetSessionId())
            setNotice('Fresh conversation started.')
          }}
        />
      )}

      <div className="tabs" role="tablist">
        <button role="tab" aria-selected={face === 'senior'}
          className={`tab${face === 'senior' ? ' active' : ''}`} onClick={() => setFace('senior')}>
          🧓 Senior shield<small>big · calm · हिंदी + English</small>
        </button>
        <button role="tab" aria-selected={face === 'family'}
          className={`tab${face === 'family' ? ' active' : ''}`} onClick={() => setFace('family')}>
          🏠 Family war-room<small>cases · vault · proof</small>
        </button>
      </div>

      {notice && <div className="notice" role="status">{notice}</div>}

      <main aria-live="polite">
        {face === 'senior'
          ? <SeniorView sessionId={sessionId} seniorId={seniorId} onNotice={setNotice} />
          : <FamilyBoard seniorId={seniorId} onNotice={setNotice} />}
      </main>

      <footer>
        Kavach · every verdict cites evidence · nothing alerts family without spoken approval ·
        backend {apiBase}
      </footer>
    </div>
  )
}
