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

export default function SeniorView({
  sessionId, seniorId, onNotice
}: {
  sessionId: string
  seniorId: string
  onNotice: (m: string) => void
}) {
  const [q, setQ] = useState('')
  const [last, setLast] = useState<{ q: string; resp: ChatResponse } | null>(null)
  const [busy, setBusy] = useState(false)
  const [listening, setListening] = useState(false)
  const [notice, setNotice] = useState('')
  const box = useRef<HTMLTextAreaElement>(null)

  async function ask(text: string) {
    const t = text.trim()
    if (!t || busy) return
    setBusy(true)
    setNotice('')
    try {
      const resp = await postChat(t, sessionId, seniorId)
      setLast({ q: t, resp })
      setQ('')
      speak(resp.spoken)
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

  const code = last?.resp.confirm_code
  return (
    <div className="senior">
      {!last && (
        <p className="kavach-says">
          Namaste 🙏 I am <b>Kavach</b>, your shield. If any call or message worries you,
          press the green button and tell me. Slowly — I am listening.
        </p>
      )}
      {last && (
        <>
          <p className="kavach-says">🛡️ {last.resp.spoken}</p>
          <div className="senior-said">🧑 {last.q}</div>
          <div className="meta">
            {last.resp.latency_ms !== null && last.resp.latency_ms !== undefined && (
              <span>{(last.resp.latency_ms / 1000).toFixed(1)}s</span>
            )}
            <button onClick={() => speak(last.resp.spoken)}>🔊 hear again</button>
          </div>
          {code && (
            <div className="code" aria-label={`confirmation code ${code}`}>{code}</div>
          )}
          {last.resp.cards.length > 0 && (
            <div className="cards">
              {last.resp.cards.map((c, i) =>
                c.type === 'verdict'
                  ? <VerdictCard key={i} c={c} />
                  : <div className="card" key={i}><h4>{c.title}</h4><p>{c.body}</p></div>
              )}
            </div>
          )}
        </>
      )}
      {busy && <p className="kavach-says">🛡️ Listening carefully… one moment.</p>}
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
