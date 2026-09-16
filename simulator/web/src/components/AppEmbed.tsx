import { useEffect, useRef } from 'react'
import { getApiBase } from '../lib/api'

/**
 * Embeds the ui://kavach-family-board MCP App in an iframe and implements
 * the host side of the MCP Apps bridge: answers ui/initialize and proxies
 * tools/call(incident_history) to /api/family-feed.
 */
export default function AppEmbed({ seniorId }: { seniorId: string }) {
  const ref = useRef<HTMLIFrameElement>(null)
  const base = getApiBase()
  const src = `${base}/apps/family-board.html?senior_id=${encodeURIComponent(seniorId)}`

  useEffect(() => {
    async function onMsg(ev: MessageEvent) {
      const d = (ev.data || {}) as Record<string, unknown>
      const frame = ref.current?.contentWindow
      if (!frame || ev.source !== frame) return
      if (d.method === 'ui/initialize') {
        frame.postMessage({ jsonrpc: '2.0', id: d.id ?? 0,
          result: { app: 'kavach-family-board', version: '0.1.0' } }, '*')
        return
      }
      if (d.method === 'tools/call') {
        const params = d.params as { name?: string } | undefined
        if (params?.name === 'incident_history') {
          try {
            const r = await fetch(`${base}/api/family-feed?senior_id=${encodeURIComponent(seniorId)}`)
            const feed = await r.json()
            frame.postMessage({ jsonrpc: '2.0', id: d.id ?? 1,
              result: { content: [{ type: 'text', text: JSON.stringify({
                incidents: (feed.incidents || []).map((c: Record<string, unknown>) => ({
                  id: c.id, verdict: c.verdict, channel: c.channel,
                  caller_claim: c.caller_claim })) }) }] } }, '*')
          } catch {
            frame.postMessage({ jsonrpc: '2.0', id: d.id ?? 1,
              result: { content: [{ type: 'text', text: '{"incidents":[]}' }] } }, '*')
          }
        }
      }
    }
    window.addEventListener('message', onMsg)
    return () => window.removeEventListener('message', onMsg)
  }, [base, seniorId])

  return (
    <div className="appframe">
      <div className="bar">
        <b>MCP App</b>
        <span><code>ui://kavach-family-board</code> · live bridge: postMessage ↔ family-feed</span>
      </div>
      <iframe ref={ref} src={src} title="Kavach family board (MCP App)" sandbox="allow-scripts" />
    </div>
  )
}
