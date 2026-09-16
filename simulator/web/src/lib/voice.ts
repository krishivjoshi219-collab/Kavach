export const SENIOR_EXAMPLES = [
  'Something strange happened — a call about my bank',
  'Checking in — good morning, all well',
  'How is my household today?'
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
      const u = new w.SpeechSynthesisUtterance(text.slice(0, 400)) as unknown as {
        rate: number; pitch: number
      }
      u.rate = 0.92
      u.pitch = 1.0
      w.speechSynthesis.speak(u)
    }
  } catch { /* audio is best-effort */ }
}
