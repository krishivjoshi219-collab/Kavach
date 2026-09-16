import { useCallback, useEffect, useState } from 'react'
import { fetchFeed, type Feed } from '../lib/api'
import AppEmbed from './AppEmbed'

function timeAgo(ts: number): string {
  const s = Math.max(1, Math.floor(Date.now() / 1000 - ts))
  if (s < 60) return `${s}s ago`
  if (s < 3600) return `${Math.floor(s / 60)}m ago`
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`
  return `${Math.floor(s / 86400)}d ago`
}

export default function FamilyBoard({
  seniorId, onNotice
}: {
  seniorId: string
  onNotice: (m: string) => void
}) {
  const [feed, setFeed] = useState<Feed | null>(null)
  const [open, setOpen] = useState<number | null>(null)

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
  return (
    <div className="family">
      <div className="famhead">
        <h3>🏠 {feed.senior.name}’s household</h3>
        <div className="meta">
          <span>{feed.incidents.length} case(s)</span>
          <span>{feed.alerts.filter(a => a.status === 'sent').length} alerts sent</span>
          <span>{feed.checkins.length} check-ins</span>
          <button onClick={load}>↻ refresh</button>
        </div>
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
            {feed.contacts.map((c, i) => <p key={i}>• {c.label} <span style={{ color: '#7a6a55' }}>({c.kind})</span></p>)}
          </div>
        </div>
      </div>
      <AppEmbed seniorId={seniorId} />
    </div>
  )
}
