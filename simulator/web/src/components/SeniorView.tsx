import { useRef, useState } from 'react'
import { postChat, type ChatResponse } from '../lib/api'
import { SENIOR_EXAMPLES, speak, supportedRec } from '../lib/voice'

function VerdictCard({ c }: { c: { title: string; body: string } }) {
  const m = /Verdict:\s*(\w+)/.exec(c.title)
  const v = m ? m[1] : ''
  return (
    <div className="card">
      <h4>{c.title}</h4>
      {v && <p style={{ marginBottom: 8 }}><span className={`pill ${v}`}>{v.replace(/_/g, ' ')}</span></p>}
      <p>{c.body}</p>
    </div>
  )
}

type Turn = { q: string; resp: ChatResponse }

function fmtLat(ms?: number | null): string {
  if (ms === null || ms === undefined) return ''
  return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`
}

export default function SeniorView({
  sessionId, seniorId, onNotice
}: {
  sessionId: string
  seniorId: string
  onNotice: (m: string) => void
}) {
  const [q, setQ] = useState('')
  const [turns, setTurns] = useState<Turn[]>([])
  const [last, setLast] = useState<{ q: string; resp: ChatResponse } | null>(null)
  const [busy, setBusy] = useState(false)
  const [listening, setListening] = useState(false)
  const [notice, setNotice] = useState('')
  const box = useRef<HTMLTextAreaElement>(null)
  const endRef = useRef<HTMLDivElement>(null)

  async function ask(text: string) {
    const t = text.trim()
    if (!t || busy) return
    setBusy(true)
    setNotice('')
    try {
      const resp = await postChat(t, sessionId, seniorId)
      const turn = { q: t, resp }
      setTurns(prev => [...prev.slice(-9), turn])
      setLast(turn)
      setQ('')
      speak(resp.spoken)
      requestAnimationFrame(() => endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }))
    } catch (e) {
      const m = e instanceof Error ? e.message : String(e)
      setNotice(m)
      onNotice(m)
    }
    setBusy(false)
  }

  function voice() {
    const Ctor = supportedRec()
    if (!Ctor) {
      onNotice('Voice is not supported in this browser — typing works just as well.')
      box.current?.focus()
      return
    }
    try {
      const rec = new Ctor()
      rec.lang = 'en-IN'
      setListening(true)
      rec.onresult = e => {
        const t = e.results[0][0].transcript
        setListening(false)
        ask(t)
      }
      rec.onend = () => setListening(false)
      rec.onerror = () => {
        setListening(false)
        onNotice('Microphone trouble — check permission, or just type below.')
      }
      rec.start()
    } catch {
      setListening(false)
    }
  }

  return (
    <div className="senior">
      {/* Calm Senior Reassurance Header */}
      <div className="card" style={{
        background: '#e6f4ec',
        border: '1px solid #a8dfbc',
        borderRadius: 14,
        padding: '16px 20px',
        textAlign: 'center',
        marginBottom: 16
      }}>
        <div style={{ fontSize: 28, marginBottom: 2 }}>🛡️</div>
        <h3 style={{ margin: '0 0 4px 0', color: '#1b5e20', fontSize: 18 }}>Kavach is Guarding You</h3>
        <p style={{ margin: 0, fontSize: 14, color: '#2e7d32' }}>
          Scam calls and fake bank messages are quietly blocked. Private calls & chats never leave this phone.
        </p>
      </div>

      {!last && (
        <p className="kavach-says">
          Namaste 🙏 I am <b>Kavach</b>, your shield. If any call or message worries you,
          press the green button and tell me. Slowly — I am listening.
        </p>
      )}

      {turns.length > 0 && (
        <div className="thread" aria-live="polite">
          {turns.map((t, i) => (
            <div key={i} className="turn">
              <div className="senior-said">🧑 {t.q}</div>
              <p className="kavach-says small">🛡️ {t.resp.spoken}</p>
              {t.resp.verdict && (
                <p style={{ margin: '6px 0' }}>
                  <span className={`pill ${t.resp.verdict}`}>{t.resp.verdict.replace(/_/g, ' ')}</span>
                  {t.resp.latency_ms !== null && t.resp.latency_ms !== undefined && (
                    <span className="lat"> · {fmtLat(t.resp.latency_ms)} · {t.resp.provider}</span>
                  )}
                </p>
              )}
              {t.resp.confirm_code && (
                <div className="code" aria-label={`confirmation code ${t.resp.confirm_code}`}>{t.resp.confirm_code}</div>
              )}
              {t.resp.cards.length > 0 && (
                <div className="cards">
                  {t.resp.cards.map((c, j) =>
                    c.type === 'verdict'
                      ? <VerdictCard key={j} c={c} />
                      : <div className="card" key={j}><h4>{c.title}</h4><p>{c.body}</p></div>
                  )}
                </div>
              )}
            </div>
          ))}
          <div ref={endRef} />
        </div>
      )}
      {busy && <p className="kavach-says">🛡️ <span className="typing" aria-hidden><i /><i /><i /></span> Listening carefully… one moment.</p>}
      <label className="sr" htmlFor="seniorbox">Talk to Kavach</label>
      <textarea
        id="seniorbox"
        ref={box}
        rows={2}
        value={q}
        maxLength={8000}
        onChange={e => setQ(e.target.value)}
        onKeyDown={e => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            ask(q)
          }
        }}
        placeholder="Type here, or press the green button and speak…"
      />
      <div className="bigrow">
        <button className={`bigbtn talk${listening ? ' listening' : ''}`} onClick={voice} disabled={busy}>
          {listening ? '● Listening…' : '🎤 Talk to Kavach'}
        </button>
        <button className="bigbtn" onClick={() => ask(q)} disabled={busy || !q.trim()}>
          {busy ? '…' : 'Send ➤'}
        </button>
      </div>
      <div className="chips">
        {SENIOR_EXAMPLES.map(s => (
          <button key={s} className="chip" onClick={() => ask(s)} disabled={busy}>{s}</button>
        ))}
      </div>
      {notice && <div className="notice" role="status">{notice}</div>}
    </div>
  )
}
