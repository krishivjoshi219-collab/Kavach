import { useEffect, useState } from 'react'
import { fetchHealth, fetchVersion } from '../lib/api'

export default function HealthPill({ llmMode }: { llmMode: string }) {
  const [state, setState] = useState<'wait' | 'on' | 'off'>('wait')
  const [ms, setMs] = useState<number | null>(null)
  const [ver, setVer] = useState<string>('')

  useEffect(() => {
    let dead = false
    async function poll() {
      try {
        const h = await fetchHealth()
        if (dead) return
        setState('on')
        setMs(h.ms)
      } catch {
        if (dead) return
        setState('off')
        setMs(null)
      }
    }
    fetchVersion().then(v => {
      if (!dead && v) setVer(`v${v.version} · ${v.mcp_spec}`)
    })
    poll()
    const t = setInterval(poll, 30000)
    return () => {
      dead = true
      clearInterval(t)
    }
  }, [])

  const label =
    state === 'on' ? `online${ms != null ? ` · ${ms}ms` : ''}` : state === 'off' ? 'offline' : 'checking…'
  return (
    <span className="health" title={ver || 'backend health'}>
      <span className={`dot ${state}`} aria-hidden />
      {label}
      {llmMode && <span className="badge">{llmMode}</span>}
    </span>
  )
}
