import { useState } from 'react'
import { EXAMPLES, speak, supportedRec } from '../lib/voice'

export default function Composer({
  busy, onAsk, onNotice
}: {
  busy: boolean
  onAsk: (text: string) => void
  onNotice: (m: string) => void
}) {
  const [q, setQ] = useState(EXAMPLES[0])
  const [listening, setListening] = useState(false)
  const MAX = 8000

  function submit(text: string) {
    const t = text.trim()
    if (!t || busy) return
    onAsk(t)
  }

  function voice() {
    const Ctor = supportedRec()
    if (!Ctor) {
      onNotice('Voice input is not supported in this browser — typed it instead.')
      submit(q)
      return
    }
    try {
      const rec = new Ctor()
      rec.lang = 'en-US'
      setListening(true)
      rec.onresult = e => {
        const t = e.results[0][0].transcript
        setQ(t)
        setListening(false)
        submit(t)
      }
      rec.onend = () => setListening(false)
      rec.onerror = () => {
        setListening(false)
        onNotice('Mic error — check the microphone permission, typed mode still works.')
      }
      rec.start()
    } catch {
      setListening(false)
      onNotice('Could not start voice capture in this browser.')
    }
  }

  return (
    <div className="composer">
      <label className="sr" htmlFor="askbox">Ask K-VoiceOps</label>
      <textarea
        id="askbox"
        rows={3}
        value={q}
        maxLength={MAX}
        onChange={e => setQ(e.target.value)}
        onKeyDown={e => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            submit(q)
          }
        }}
        placeholder='Try: “Alexa, why did my deploy fail?”'
      />
      <div className="row">
        <button className="btn" onClick={() => submit(q)} disabled={busy || !q.trim()}>
          {busy ? 'Working…' : 'Ask'}
        </button>
        <button
          className={`btn talk${listening ? ' listening' : ''}`}
          onClick={voice}
          disabled={busy}
          title="Speak instead of typing"
        >
          {listening ? '● Listening…' : '🎤 Talk'}
        </button>
        <button className="btn ghost" onClick={() => speak(q)} disabled={!q.trim()} title="Read the prompt aloud">
          🔊 Read
        </button>
        <span className="count">{q.length}/{MAX} · Enter to send</span>
      </div>
      <div className="chips">
        {EXAMPLES.map(s => (
          <button key={s} className="chip" onClick={() => { setQ(s); submit(s) }} disabled={busy}>
            {s.split('\n')[0].slice(0, 42)}
          </button>
        ))}
      </div>
    </div>
  )
}
