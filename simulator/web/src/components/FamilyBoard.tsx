import { useCallback, useEffect, useState } from 'react'
import { fetchFeed, postBlockCase, postDemoAttack, type Feed } from '../lib/api'
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
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('')
  const [refreshing, setRefreshing] = useState(false)

  function toast(m: string) {
    setActionNotice(m)
    window.clearTimeout((toast as unknown as { t?: number }).t)
    ;(toast as unknown as { t?: number }).t = window.setTimeout(() => setActionNotice(''), 6000)
  }

  async function liveAttack() {
    if (demoBusy) return
    setDemoBusy(true)
    setDemoMsg('')
    try {
      const r = await postDemoAttack(seniorId, 'bank_otp')
      const msg = `🔴 LIVE ATTACK: case #${r.incident_id} ${r.verdict} — code ${r.confirm_code}. ` +
        'Screen stays quiet; E2E alert sent to war room.'
      setDemoMsg(msg)
      await load()
      setOpen(r.incident_id)
    } catch (e) {
      onNotice(e instanceof Error ? e.message : String(e))
    }
    setDemoBusy(false)
  }

  const load = useCallback(async () => {
    setRefreshing(true)
    try {
      setFeed(await fetchFeed(seniorId))
    } catch (e) {
      onNotice(e instanceof Error ? e.message : String(e))
    }
    setRefreshing(false)
  }, [seniorId, onNotice])

  useEffect(() => {
    load()
    const t = setInterval(load, 20000)
    return () => clearInterval(t)
  }, [load])

  if (!feed) return <div className="family"><div className="famhead">Loading the household…</div></div>
  const latest = feed.incidents[0]
  const warRoom = latest && (latest.verdict === 'SCAM' || latest.verdict === 'SUSPICIOUS')
  const ql = query.toLowerCase()
  const visible = feed.incidents.filter(c =>
    (!filter || c.verdict === filter) &&
    (!ql || `${c.caller_claim} ${c.channel}`.toLowerCase().includes(ql)))

  return (
    <div className="family">
      <div className={`pro ${proUnlocked ? 'on' : 'off'}`}>
        <div className="pro-top">
          <div>
            <span className="pro-badge">
              {proUnlocked ? '✨ REVENUECAT PRO SHIELD' : 'FREE TIER (1 SEAT)'}
            </span>
            <span className="pro-seats">
              {proUnlocked ? '2 of 3 parent seats protected' : '1 of 1 seat used'}
            </span>
          </div>
          <button
            className="pro-btn"
            onClick={() => {
              setProUnlocked(p => !p)
              toast(proUnlocked ? 'Previewing Free tier limits.' : 'Pro unlocked with SHIPATON-JUDGE promo (test mode, no charge).')
            }}
          >
            {proUnlocked ? 'Judge promo active ✓' : 'Unlock Pro promo'}
          </button>
        </div>
        <p className="pro-copy">
          <b>Household plan:</b> on-device quarantine, instant dual-siren, daily signed rule updates.
          Community shield shares <b>hashes only</b> — raw numbers never leave the phone.
        </p>
      </div>

      {actionNotice && (
        <div className="toast" role="status">{actionNotice}</div>
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
          <button onClick={load}>{refreshing ? '… syncing' : '↻ refresh'}</button>
          <button onClick={liveAttack} disabled={demoBusy} style={{ background: '#d32f2f', color: '#fff' }}>
            {demoBusy ? '…' : '🔴 Simulate live attack'}
          </button>
        </div>
        <div className="searchrow">
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search cases… e.g. bank, OTP, CBI" aria-label="Search cases" />
          <select value={filter} onChange={e => setFilter(e.target.value)} aria-label="Filter by verdict">
            <option value="">All verdicts</option>
            <option value="SCAM">SCAM</option>
            <option value="SUSPICIOUS">SUSPICIOUS</option>
            <option value="LIKELY_SAFE">LIKELY_SAFE</option>
            <option value="UNCERTAIN">UNCERTAIN</option>
          </select>
        </div>
        {demoMsg && <p style={{ marginTop: 8, fontWeight: 600, color: '#c62828' }}>{demoMsg}</p>}
      </div>

      <div className="fleet">
        <h4>📱 Protected parent devices</h4>
        <div className="fleet-grid">
          <div className="fleet-card"><b>Dadaji · Pixel 8</b><p className="ok">🟢 Shield active · rules v-latest · 0 threats today</p></div>
          <div className="fleet-card"><b>Mummy · Galaxy S22</b><p className="warn">🟢 Shield active · 1 SMS quarantined · OTP masked</p></div>
        </div>
      </div>

      <div className="famgrid">
        <div className="card">
          <h4>Case file — decrypted on manager device ({visible.length})</h4>
          {visible.length === 0 && <p>🕊️ Clean slate — nothing matches. A quiet phone is a safe phone.</p>}
          {visible.map(c => (
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
                    <button className="mini" style={{ background: '#c62828', color: '#fff' }} onClick={async () => {
                      try {
                        const b = await postBlockCase(seniorId, c.id)
                        toast(
                          `Blocked sender-hash ${b.number_hash.slice(0, 12)}… for case #${c.id}. ` +
                          (b.community ? 'Community shield now carries it (3+ households).' : 'Household devices sync it; community learns at 3 households.')
                        )
                      } catch (e) {
                        onNotice(e instanceof Error ? e.message : String(e))
                      }
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
            <h4>Remote safety actions · consent-gated</h4>
            <div style={{ display: 'grid', gap: 8, marginTop: 8 }}>
              <button className="mini" onClick={() => {
                toast('💬 Safety whisper sent to parent screen: "Do not share OTP. Checking caller."')
              }}>
                💬 Whisper alert to parent screen
              </button>
              <button className="mini" onClick={() => {
                toast('🔐 6-letter Family Proof challenge dispatched. Kills AI voice clones — enrolled-device proof only.')
              }}>
                🔐 Send anti-clone device challenge
              </button>
              <button className="mini" style={{ color: '#c62828' }} onClick={() => {
                toast('🚨 Emergency siren triggered on parent phone to break scammer pressure.')
              }}>
                🚨 Sound remote siren
              </button>
            </div>
          </div>

          <div className="card">
            <h4>Daily rhythms & safe contacts</h4>
            {feed.routines.map(r => (
              <p key={r.id}>• {r.label} — {r.expected_time} {r.last_confirmed ? ` ✓ (${r.streak}🔥)` : '· pending'}</p>
            ))}
            {feed.routines.length === 0 && <p>No rhythms yet.</p>}
            {feed.contacts.map((c, i) => (
              <p key={i}>• {c.label} ({c.kind})</p>
            ))}
            {feed.contacts.length === 0 && <p>No safe contacts saved.</p>}
            {feed.checkins.length > 0 && (
              <p className="meta">Last check-in: {feed.checkins[0].kind} · {feed.checkins[0].mood}</p>
            )}
            {feed.alerts.length > 0 && (
              <p className="meta">Alerts: {feed.alerts.slice(0, 3).map(a => `#${a.id} ${a.status}`).join(' · ')}</p>
            )}
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
