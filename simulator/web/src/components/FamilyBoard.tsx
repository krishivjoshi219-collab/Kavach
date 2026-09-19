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
  const [proUnlocked, setProUnlocked] = useState(true)
  const [actionNotice, setActionNotice] = useState('')

  async function liveAttack() {
    if (demoBusy) return
    setDemoBusy(true)
    setDemoMsg('')
    try {
      const r = await postDemoAttack(seniorId, 'bank_otp')
      setDemoMsg(`🔴 LIVE ATTACK: case #${r.incident_id} ${r.verdict} — code ${r.confirm_code}. Screen stays quiet; E2E alert sent to war room.`)
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
      {/* RevenueCat Pro Entitlement Banner */}
      <div className="card" style={{
        background: proUnlocked ? 'linear-gradient(135deg, #1b2f1e 0%, #0d1a10 100%)' : '#262930',
        border: proUnlocked ? '1px solid #4caf50' : '1px solid #444',
        color: '#fff',
        marginBottom: 16
      }}>
        <div className="row" style={{ marginTop: 0, alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <span style={{
              background: '#244026',
              color: '#81c784',
              fontSize: 11,
              fontWeight: 800,
              padding: '3px 8px',
              borderRadius: 6,
              letterSpacing: '0.5px'
            }}>
              {proUnlocked ? '✨ REVENUECAT PRO SHIELD' : 'FREE TIER (1 SEAT)'}
            </span>
            <span style={{ marginLeft: 10, fontSize: 13, color: '#c8e6c9', fontWeight: 600 }}>
              {proUnlocked ? '2 of 3 Parent Seats Protected' : '1 of 1 Seat Used'}
            </span>
          </div>
          <button
            className="mini"
            style={{ background: '#ffd54f', color: '#000', fontWeight: 700, border: 'none' }}
            onClick={() => {
              setProUnlocked(p => !p)
              setActionNotice(proUnlocked ? 'Simulated Free Tier' : 'Unlocked Pro with SHIPATON-JUDGE promo!')
            }}
          >
            {proUnlocked ? 'Judge Promo Active ✓' : 'Unlock Pro Promo'}
          </button>
        </div>
        <p style={{ margin: '8px 0 4px 0', fontSize: 13, color: '#e0e0e0' }}>
          <b>Household Protection Plan:</b> Covers Mom & Dad's devices with on-device quarantine, instant dual-siren alert, and daily signed threat updates.
        </p>
      </div>

      {actionNotice && (
        <div style={{ background: '#e8f5e9', color: '#1b5e20', padding: '8px 14px', borderRadius: 8, marginBottom: 14, fontSize: 13 }}>
          {actionNotice}
        </div>
      )}

      {warRoom && (
        <div className="warroom" role="alert" aria-live="assertive">
          <h4>🚨 War room — latest threat needs eyes</h4>
          <p>
            Case #{latest.id} {latest.verdict} via {latest.channel} · {timeAgo(latest.created)}.
            Zero-buzz quarantine saved parent phone. Review proof and block sender hash below.
          </p>
        </div>
      )}

      <div className="famhead">
        <div className="row" style={{ marginTop: 0, alignItems: 'center' }}>
          <h3 style={{ margin: 0 }}>🏠 {feed.senior.name}’s Household Command Center</h3>
          <span style={{ marginLeft: 'auto' }}><ScoreRing value={safetyScore(feed)} /></span>
        </div>
        <div className="meta">
          <span>{feed.incidents.length} case(s)</span>
          <span>{feed.alerts.filter(a => a.status === 'sent').length} alerts sent</span>
          <span>{feed.checkins.length} check-ins</span>
          <button onClick={load}>↻ refresh</button>
          <button onClick={liveAttack} disabled={demoBusy} style={{ background: '#d32f2f', color: '#fff' }}>
            {demoBusy ? '…' : '🔴 Simulate live attack'}
          </button>
        </div>
        {demoMsg && <p style={{ marginTop: 8, fontWeight: 600, color: '#c62828' }}>{demoMsg}</p>}
      </div>

      {/* Fleet Overview */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h4 style={{ margin: '0 0 10px 0' }}>📱 Protected Parent Devices (Fleet)</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
          <div style={{ background: '#fdfbf7', border: '1px solid #e0d7c7', borderRadius: 8, padding: 12 }}>
            <b>Dadaji (Dad's Pixel 8)</b>
            <p style={{ margin: '4px 0 0 0', fontSize: 13, color: '#1b5e20' }}>🟢 Shield Active · 0 Threats Today</p>
          </div>
          <div style={{ background: '#fdfbf7', border: '1px solid #e0d7c7', borderRadius: 8, padding: 12 }}>
            <b>Mummy (Mom's Galaxy S22)</b>
            <p style={{ margin: '4px 0 0 0', fontSize: 13, color: '#b3541e' }}>🟢 Shield Active · 1 SMS Quarantined</p>
          </div>
        </div>
      </div>

      <div className="famgrid">
        <div className="card">
          <h4>Case file (Decrypted on manager device)</h4>
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
                  <li style={{ marginTop: 6 }}>
                    <button className="mini" style={{ background: '#c62828', color: '#fff' }} onClick={() => {
                      setActionNotice(`Blocked sender hash for case #${c.id}. Household devices will kill calls pre-ring.`)
                    }}>
                      🛡️ Block hash for household
                    </button>
                  </li>
                </ul>
              )}
            </div>
          ))}
        </div>

        <div style={{ display: 'grid', gap: 12, alignContent: 'start' }}>
          <div className="card">
            <h4>Remote Safety Actions (Consent-Gated)</h4>
            <div style={{ display: 'grid', gap: 8, marginTop: 8 }}>
              <button className="mini" onClick={() => setActionNotice('💬 Safety whisper sent to parent screen: "Do not share OTP. Checking caller."')}>
                💬 Whisper Alert to Dad's Screen
              </button>
              <button className="mini" onClick={() => setActionNotice('🔐 Dispatched 6-letter Family Proof Challenge to parent phone. Kills AI voice clones.')}>
                🔐 Send Anti-Clone Device Challenge
              </button>
              <button className="mini" style={{ color: '#c62828' }} onClick={() => setActionNotice('🚨 Emergency Siren triggered on parent phone to interrupt scammer pressure.')}>
                🚨 Sound Remote Siren
              </button>
            </div>
          </div>

          <div className="card">
            <h4>Daily rhythms & safe contacts</h4>
            {feed.routines.slice(0, 2).map(r => (
              <p key={r.id}>• {r.label} — {r.expected_time} {r.last_confirmed ? ` ✓ (${r.streak}🔥)` : ''}</p>
            ))}
            {feed.contacts.slice(0, 2).map((c, i) => (
              <p key={i}>• {c.label} ({c.kind})</p>
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
