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

const STRINGS = {
  en: {
    shieldTitle: 'Kavach is Guarding You',
    shieldSub: 'Scam calls and fake bank messages are quietly blocked. Private calls & chats never leave this phone.',
    live: '● SHIELD LIVE',
    hello: (<>Namaste 🙏 I am <b>Kavach</b>, your shield. If any call or message worries you, press the green button and tell me. Slowly — I am listening.</>),
    placeholder: 'Type here, or press the green button and speak…',
    talk: '🎤 Talk to Kavach',
  },
  hi: {
    shieldTitle: 'कवच आपकी रक्षा कर रहा है',
    shieldSub: 'फ़र्ज़ी कॉल और नकली बैंक संदेश चुपचाप रोके जाते हैं। आपकी निजी बातें इस फ़ोन से बाहर नहीं जातीं।',
    live: '● ढाल सक्रिय',
    hello: (<>नमस्ते 🙏 मैं <b>कवच</b> हूँ, आपकी ढाल। कोई कॉल या संदेश चिंता दे, तो हरी बटन दबाकर बताइए। आराम से — मैं सुन रहा हूँ।</>),
    placeholder: 'यहाँ लिखें, या हरी बटन दबाकर बोलें…',
    talk: '🎤 कवच से बात करें',
  },
} as const

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
  const [lang, setLang] = useState<'en' | 'hi'>('en')
  const t = STRINGS[lang]
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
      {/* Live shield presence — the senior SEES protection, not settings */}
      <div className="shieldbar">
        <div className="eye" aria-hidden>🛡️</div>
        <h3>{t.shieldTitle}</h3>
        <p>{t.shieldSub}</p>
        <div>
          <span className="live"><span className="livedot" aria-hidden />{t.live}</span>
        </div>
        <div className="langrow" role="group" aria-label="Language / भाषा">
          <button className={`langbtn${lang === 'en' ? ' on' : ''}`} onClick={() => setLang('en')} aria-pressed={lang === 'en'}>English</button>
          <button className={`langbtn${lang === 'hi' ? ' on' : ''}`} onClick={() => setLang('hi')} aria-pressed={lang === 'hi'}>हिंदी</button>
        </div>
      </div>

      {!last && <p className="kavach-says">{t.hello}</p>}

      {turns.length > 0 && (
        <div className="thread" aria-live="polite">
          {turns.map((tn, i) => (
            <div key={i} className={`turn${tn.resp.verdict ? ` v-${tn.resp.verdict}` : ''}`}>
              <div className="senior-said">🧑 {tn.q}</div>
              <p className="kavach-says small">🛡️ {tn.resp.spoken}</p>
              {tn.resp.verdict && (
                <p style={{ margin: '6px 0' }}>
                  <span className={`pill ${tn.resp.verdict}`}>{tn.resp.verdict.replace(/_/g, ' ')}</span>
                  {tn.resp.latency_ms !== null && tn.resp.latency_ms !== undefined && (
                    <span className="lat"> · {fmtLat(tn.resp.latency_ms)} · {tn.resp.provider}</span>
                  )}
                </p>
              )}
              {tn.resp.confirm_code && (
                <div className="code" aria-label={`confirmation code ${tn.resp.confirm_code}`}>{tn.resp.confirm_code}</div>
              )}
              {tn.resp.cards.length > 0 && (
                <div className="cards">
                  {tn.resp.cards.map((c, j) =>
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
        placeholder={t.placeholder}
      />
      <div className="composer-meta">
        <span>{listening ? '🎤 सुन रहे हैं… / listening…' : '🔒 Nothing leaves this phone unencrypted'}</span>
        <span className="count">{q.length}/8000</span>
        {turns.length > 0 && (
          <button className="linkbtn" onClick={() => { setTurns([]); setLast(null); }}>
            clear
          </button>
        )}
      </div>
      <div className="bigrow">
        <button className={`bigbtn talk${listening ? ' listening' : ''}`} onClick={voice} disabled={busy}>
          {listening ? '● Listening…' : t.talk}
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
