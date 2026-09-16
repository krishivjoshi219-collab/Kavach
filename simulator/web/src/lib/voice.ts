export const EXAMPLES = [
  'why did my deploy fail?',
  'is the demo-api pipeline passing?',
  'verify this code:\n```python\ndef f():\n    return 1\n```'
]

type Rec = {
  lang: string
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null
  onend: (() => void) | null
  onerror: (() => void) | null
  start(): void
  stop(): void
}

export function supportedRec(): (new () => Rec) | null {
  const w = window as unknown as Record<string, unknown>
  return (w.SpeechRecognition as new () => Rec) ||
    (w.webkitSpeechRecognition as new () => Rec) || null
}

export function speak(text: string) {
  try {
    const w = window as unknown as {
      speechSynthesis?: { cancel(): void; speak(u: unknown): void }
      SpeechSynthesisUtterance?: new (t: string) => unknown
    }
    if (w.speechSynthesis && w.SpeechSynthesisUtterance && text) {
      w.speechSynthesis.cancel()
      w.speechSynthesis.speak(new w.SpeechSynthesisUtterance(text.slice(0, 280)))
    }
  } catch { /* audio is best-effort */ }
}
