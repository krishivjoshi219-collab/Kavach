import { useCallback, useEffect, useState } from 'react'
import { fetchFeed, postDemoAttack, type Feed } from '../lib/api'
import AppEmbed from './AppEmbed'

function timeAgo(ts: number): string {
  const s = Math.max(1, Math.floor(Date.now() / 1000 - ts))
  if (s < 60) return `${s}s ago`
  if (s < 3600) return `${Math.floor(s / 60)}m ago`
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`
  return `${Math.floor(s / 86400)}d ago`
}

function maskOtp(s: string): string {
  return s.replace(/\b\d{4,8}\b/g, '******')
}

function safetyScore(feed: Feed): number {
  const scams = feed.incidents.filter(c => c.verdict === 'SCAM').length
  const safe = feed.incidents.filter(c => c.verdict === 'LIKELY_SAFE').length
  const checkins = feed.checkins.length
  const base = 72 + Math.min(18, safe * 3 + checkins * 2) - Math.min(30, scams * 2)
  return Math.max(40, Math.min(100, base))
}

function ScoreRing({ value }: { value: number }) {
  const r = 26
  const c = 2 * Math.PI * r
  const off = c - (value / 100) * c
  return (
    <svg width="72" height="72" viewBox="0 0 72 72" role="img" aria-label={`Safety score ${value}`}>
      <circle cx="36" cy="36" r={r} fill="none" stroke="#e3d5bd" strokeWidth="9" />
      <circle cx="36" cy="36" r={r} fill="none" stroke={value >= 80 ? '#1f7a4d' : value >= 60 ? '#b3541e' : '#b3261e'}
        strokeWidth="9" strokeLinecap="round" strokeDasharray={c} strokeDashoffset={off}
        transform="rotate(-90 36 36)" />
      <text x="36" y="41" textAnchor="middle" fontSize="18" fontWeight="800" fill="#2b2118">{value}</text>
    </svg>
  )
}

export default function FamilyBoard({
  seniorId, onNotice
}: {
  seniorId: string
  onNotice: (m: string) => void
}) {
  const [feed, setFeed] = useState<Feed | null>(null)
  const [open, setOpen] = useState<number | null>(null)
  const [demoBusy, setDemoBusy] = useState(false)
  const [demoMsg, setDemoMsg] = useState('')

  async function liveAttack() {
    if (demoBusy) return
    setDemoBusy(true)
    setDemoMsg('')
    try {
      const r = await postDemoAttack(seniorId, 'bank_otp')
      setDemoMsg(`🔴 LIVE ATTACK: case #${r.incident_id} ${r.verdict} — code ${r.confirm_code}. Refreshing proof…`)
      await load()
      setOpen(r.incident_id)
    } catch (e) {
      onNotice(e instanceof Error ? e.message : String(e))
    }
    setDemoBusy(false)
  }

  const load = useCallback(async () => {
    try {
      setFeed(await fetchFeed(seniorId))
    } catch (e) {
      onNotice(e instanceof Error ? e.message : String(e))
    }
  }, [seniorId, onNotice])

  useEffect(() => {
    load()
    const t = setInterval(load, 20000)
    return () => clearInterval(t)
  }, [load])

  if (!feed) return <div className="family"><div className="famhead">Loading the household…</div></div>
  const latest = feed.incidents[0]
  const warRoom = latest && (latest.verdict === 'SCAM' || latest.verdict === 'SUSPICIOUS')
  return (
    <div className="family">
      {warRoom && (
        <div className="warroom" role="alert" aria-live="assertive">
          <h4>🚨 War room — latest threat needs eyes</h4>
          <p>
            Case #{latest.id} {latest.verdict} via {latest.channel} · {timeAgo(latest.created)}.
            Open proof, block the hash, check the vault.
          </p>
        </div>
      )}
      <div className="famhead">
        <div className="row" style={{ marginTop: 0, alignItems: 'center' }}>
          <h3 style={{ margin: 0 }}>🏠 {feed.senior.name}’s household</h3>
          <span style={{ marginLeft: 'auto' }}><ScoreRing value={safetyScore(feed)} /></span>
        </div>
        <div className="meta">
          <span>{feed.incidents.length} case(s)</span>
          <span>{feed.alerts.filter(a => a.status === 'sent').length} alerts sent</span>
          <span>{feed.checkins.length} check-ins</span>
          <button onClick={load}>↻ refresh</button>
          <button onClick={liveAttack} disabled={demoBusy}>
            {demoBusy ? '…' : '🔴 Simulate live attack'}
          </button>
        </div>
        {demoMsg && <p style={{ marginTop: 8 }}>{demoMsg}</p>}
      </div>
      <div className="famgrid">
        <div className="card">
          <h4>Case file</h4>
          {feed.incidents.length === 0 && <p>Clean slate — nothing on record.</p>}
          {feed.incidents.map(c => (
            <div key={c.id} className={`card case ${c.verdict}`} style={{ marginTop: 8 }}>
              <div className="row" style={{ marginTop: 0 }}>
                <span className={`pill ${c.verdict}`}>{c.verdict.replace(/_/g, ' ')}</span>
                <b>#{c.id}</b>
                <span style={{ color: '#7a6a55' }}>{c.channel} · {timeAgo(c.created)}</span>
                <button className="mini" style={{ marginLeft: 'auto' }}
                  onClick={() => setOpen(open === c.id ? null : c.id)}>
                  {open === c.id ? 'hide proof' : 'see proof'}
                </button>
              </div>
              <p style={{ marginTop: 6 }}>{c.caller_claim || 'unknown caller'}</p>
              {open === c.id && (
                <ul className="flags">
                  {c.red_flags.length === 0 && <li>No red flags — cleared on evidence.</li>}
                  {c.red_flags.map((f, i) => (
                    <li key={i}><b>{f.label}.</b> {f.meaning}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
        <div style={{ display: 'grid', gap: 12, alignContent: 'start' }}>
          <div className="card">
            <h4>Daily rhythms</h4>
            {feed.routines.map(r => (
              <p key={r.id}>• {r.label} — usually {r.expected_time}
                {r.last_confirmed ? ` ✓ (${r.streak}🔥)` : ''}</p>
            ))}
          </div>
          <div className="card">
            <h4>Recent check-ins</h4>
            {feed.checkins.length === 0 && <p>None yet today.</p>}
            {feed.checkins.slice(0, 4).map((c, i) => (
              <p key={i}>• “{c.note.slice(0, 80)}” — {c.mood} · {timeAgo(c.created)}</p>
            ))}
          </div>
          <div className="card">
            <h4>Safe contacts</h4>
            {feed.contacts.map((c, i) => (
              <p key={i}>• {c.label} <span style={{ color: '#7a6a55' }}>({c.kind})</span></p>
            ))}
          </div>
        </div>
      </div>
      <AppEmbed seniorId={seniorId} />
      <div className="card vault">
        <h4>📥 Quarantine vault (E2E full text, OTP masked)</h4>
        {feed.incidents.filter(c => c.verdict === 'SCAM' || c.verdict === 'SUSPICIOUS').length === 0
          && <p>Clean — run 🔴 Simulate live attack to test.</p>}
        {feed.incidents.filter(c => c.verdict === 'SCAM' || c.verdict === 'SUSPICIOUS').slice(0, 5).map(c => (
          <p key={c.id}>• #{c.id} {c.channel} — {maskOtp(c.caller_claim || 'unknown caller')}</p>
        ))}
      </div>
    </div>
  )
}
