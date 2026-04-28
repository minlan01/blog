const BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export interface ModelInfo {
  name: string
  size: number | null
  modified_at: string | null
}

export async function getModels(): Promise<ModelInfo[]> {
  const res = await fetch(`${BASE}/ai/models`)
  if (!res.ok) throw new Error(`Failed to fetch models: ${res.status}`)
  return res.json()
}

export async function* streamChat(
  model: string,
  messages: { role: string; content: string }[]
): AsyncGenerator<string, void, undefined> {
  const res = await fetch(`${BASE}/ai/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, messages })
  })

  if (!res.ok) throw new Error(`Chat request failed: ${res.status}`)
  if (!res.body) throw new Error('No response body')

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed.startsWith('data: ')) continue
      const payload = trimmed.slice(6)
      if (payload === '[DONE]') return
      try {
        const data = JSON.parse(payload)
        if (data.error) throw new Error(data.error)
        if (data.content) yield data.content
      } catch {
        // skip malformed lines
      }
    }
  }
}
