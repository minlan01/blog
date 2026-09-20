const BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export interface ModelInfo {
  name: string
  size: number | null
  modified_at: string | null
}

// ── 会话类型 ──

export interface ChatSessionSummary {
  id: number
  title: string
  model: string | null
  message_count: number
  created_at: string
  updated_at: string
}

export interface ChatMessageOut {
  id: number
  role: string
  content: string
  created_at: string
}

export interface ChatSessionDetail {
  id: number
  title: string
  model: string | null
  messages: ChatMessageOut[]
  created_at: string
  updated_at: string
}

function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  const token = sessionStorage.getItem('token')
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

// ── 模型列表 ──

export async function getModels(): Promise<ModelInfo[]> {
  const res = await fetch(`${BASE}/ai/models`, { headers: getAuthHeaders() })
  if (!res.ok) throw new Error(`Failed to fetch models: ${res.status}`)
  return res.json()
}

// ── 会话 CRUD ──

export async function getSessions(): Promise<ChatSessionSummary[]> {
  const res = await fetch(`${BASE}/ai/sessions`, { headers: getAuthHeaders() })
  if (!res.ok) throw new Error('获取会话列表失败')
  return res.json()
}

export async function createSession(title?: string, model?: string): Promise<ChatSessionDetail> {
  const res = await fetch(`${BASE}/ai/sessions`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ title: title || '新对话', model }),
  })
  if (!res.ok) throw new Error('创建会话失败')
  return res.json()
}

export async function getSession(id: number): Promise<ChatSessionDetail> {
  const res = await fetch(`${BASE}/ai/sessions/${id}`, { headers: getAuthHeaders() })
  if (!res.ok) throw new Error('获取会话详情失败')
  return res.json()
}

export async function updateSession(id: number, title: string): Promise<ChatSessionDetail> {
  const res = await fetch(`${BASE}/ai/sessions/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ title }),
  })
  if (!res.ok) throw new Error('更新会话失败')
  return res.json()
}

export async function deleteSession(id: number): Promise<void> {
  const res = await fetch(`${BASE}/ai/sessions/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  })
  if (!res.ok && res.status !== 204) throw new Error('删除会话失败')
}

// ── 记忆 ──

export async function getMemory(): Promise<string> {
  const res = await fetch(`${BASE}/ai/memory`, { headers: getAuthHeaders() })
  if (!res.ok) throw new Error('获取记忆失败')
  const data = await res.json()
  return data.memory || ''
}

export async function updateMemory(memory: string): Promise<string> {
  const res = await fetch(`${BASE}/ai/memory`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ memory }),
  })
  if (!res.ok) throw new Error('保存记忆失败')
  const data = await res.json()
  return data.memory || ''
}

// ── 流式聊天 ──

export interface StreamChatResult {
  content: string
  saved: boolean
  sessionId: number | null
}

export async function* streamChat(
  model: string,
  messages: { role: string; content: string }[],
  sessionId?: number | null,
  signal?: AbortSignal
): AsyncGenerator<{ type: 'content' | 'saved' | 'done'; value?: string; sessionId?: number }, void, undefined> {
  const res = await fetch(`${BASE}/ai/chat`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ model, messages, session_id: sessionId ?? null }),
    signal,
  })

  if (!res.ok) throw new Error(`Chat request failed: ${res.status}`)
  if (!res.body) throw new Error('No response body')

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
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
        if (payload === '[DONE]') {
          yield { type: 'done' }
          return
        }
        try {
          const data = JSON.parse(payload)
          if (data.error) throw new Error(data.error)
          if (data.content) {
            yield { type: 'content', value: data.content }
          }
          if (data.saved) {
            yield { type: 'saved', sessionId: data.session_id }
          }
        } catch (error) {
          if (error instanceof Error) throw error
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}
