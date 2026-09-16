import { useState } from 'react'
import type { Card } from '../lib/api'

function copyText(t: string, done: (m: string) => void) {
  const finish = () => done('copied ✓')
  try {
    const nav = navigator as Navigator & { clipboard?: { writeText(s: string): Promise<void> } }
    if (nav.clipboard) {
      nav.clipboard.writeText(t).then(finish, () => done('copy failed'));
      return
    }
  } catch { /* fallback below */ }
  const ta = document.createElement('textarea')
  ta.value = t
  document.body.appendChild(ta)
  ta.select()
  try {
    document.execCommand('copy')
    finish()
  } catch {
    done('copy failed')
  }
  document.body.removeChild(ta)
}

function CardShell({
  title, tone, onCopy, copyText: ct, children
}: {
  title: string
  tone?: 'pass' | 'fail'
  onCopy?: string
  copyText?: string
  children: React.ReactNode
}) {
  const [msg, setMsg] = useState('')
  return (
    <div className={`card${tone ? ` ${tone}` : ''}`}>
      <div className="head">
        <h4>{title}</h4>
        {onCopy && (
          <button className="mini" onClick={() => copyText(onCopy, setMsg)} title={ct || 'copy'}>
            {msg || 'copy'}
          </button>
        )}
      </div>
      {children}
    </div>
  )
}

export function StatusCard({ c }: { c: Card }) {
  const low = `${c.title} ${c.body}`.toLowerCase()
  const failed = /fail|error|❌|not ok/.test(low)
  const passed = /pass|✓|verified|ok/.test(low) && !failed
  return (
    <CardShell title={c.title} tone={failed ? 'fail' : passed ? 'pass' : undefined}>
      <pre>{c.body || '—'}</pre>
    </CardShell>
  )
}

export function DiffCard({ c }: { c: Card }) {
  return (
    <CardShell title={c.title} onCopy={c.body} copyText="copy diff">
      <pre>{c.body || 'no diff'}</pre>
    </CardShell>
  )
}

export function VerifyCard({ c }: { c: Card }) {
  const ok = !/fail|invalid|error/i.test(c.body + c.title)
  return (
    <CardShell title={c.title} tone={ok ? 'pass' : 'fail'}>
      <p style={{ margin: '0 0 8px' }}>
        <span className={`pill ${ok ? 'ok' : 'no'}`}>{ok ? '✓ VERIFIED' : '✗ NEEDS FIX'}</span>
      </p>
      <pre>{c.body || '—'}</pre>
    </CardShell>
  )
}

export function GenericCard({ c }: { c: Card }) {
  const isDiff = c.type === 'diff' || /diff|patch/.test(c.title.toLowerCase())
  if (isDiff) return <DiffCard c={c} />
  if (c.type === 'verify') return <VerifyCard c={c} />
  return <StatusCard c={c} />
}

export function ToolTimeline({ tools }: { tools: string[] }) {
  if (!tools.length) return null
  return (
    <div className="tools" aria-label="tool trace">
      {tools.map((t, i) => {
        const name = t.split('(')[0].split('->')[0].trim()
        const rest = t.slice(name.length)
        return (
          <div className="tool" key={i}>
            <b>🔧 {i + 1}. {name}</b>
            {rest}
          </div>
        )
      })}
    </div>
  )
}
