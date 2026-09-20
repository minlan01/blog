import { nextTick, onUnmounted, ref } from 'vue'
import {
  createSession as apiCreateSession,
  deleteSession as apiDeleteSession,
  getMemory,
  getSession,
  getSessions,
  getModels,
  streamChat,
  updateMemory,
  updateSession,
} from '@/api/chat'
import type { ChatMessageOut, ChatSessionDetail, ChatSessionSummary, ModelInfo } from '@/api/chat'

export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
}

export function useChat() {
  let _msgId = 0
  const messages = ref<Message[]>([])
  const models = ref<ModelInfo[]>([])
  const selectedModel = ref('')
  const streaming = ref(false)
  const error = ref('')
  const messagesContainer = ref<HTMLElement | null>(null)

  // ── 会话状态 ──
  const sessions = ref<ChatSessionSummary[]>([])
  const currentSessionId = ref<number | null>(null)
  const sessionsLoaded = ref(false)

  // ── 记忆状态 ──
  const memory = ref('')
  const memoryOpen = ref(false)
  const memoryDraft = ref('')
  const memorySaving = ref(false)

  let _abortController: AbortController | null = null

  // ════════════ 模型 ════════════

  async function loadModels() {
    try {
      models.value = await getModels()
      if (models.value.length > 0 && !selectedModel.value) {
        selectedModel.value = models.value[0].name
      }
    } catch {
      error.value = '无法获取 DeepSeek 模型列表，请确认后端已配置 DeepSeek API Key'
    }
  }

  // ════════════ 会话管理 ════════════

  async function loadSessions() {
    try {
      sessions.value = await getSessions()
      sessionsLoaded.value = true
    } catch {
      error.value = '获取会话列表失败'
    }
  }

  async function startNewSession() {
    if (streaming.value) abort()
    // 始终重置到新对话状态
    currentSessionId.value = null
    messages.value = []
    error.value = ''
  }

  async function switchSession(id: number) {
    if (streaming.value) abort()
    try {
      const detail: ChatSessionDetail = await getSession(id)
      currentSessionId.value = id
      messages.value = detail.messages.map((m: ChatMessageOut) => ({
        id: ++_msgId,
        role: m.role as 'user' | 'assistant',
        content: m.content,
      }))
      error.value = ''
    } catch {
      error.value = '加载会话失败'
    }
  }

  async function removeSession(id: number) {
    try {
      await apiDeleteSession(id)
      sessions.value = sessions.value.filter((s) => s.id !== id)
      if (currentSessionId.value === id) {
        currentSessionId.value = null
        messages.value = []
      }
    } catch {
      error.value = '删除会话失败'
    }
  }

  async function renameSession(id: number, title: string) {
    try {
      await updateSession(id, title)
      const s = sessions.value.find((x) => x.id === id)
      if (s) s.title = title
    } catch {
      error.value = '重命名失败'
    }
  }

  // ════════════ 记忆 ════════════

  async function loadMemory() {
    try {
      memory.value = await getMemory()
      memoryDraft.value = memory.value
    } catch {
      // 静默失败
    }
  }

  async function saveMemory() {
    memorySaving.value = true
    try {
      memory.value = await updateMemory(memoryDraft.value)
    } catch {
      error.value = '保存记忆失败'
    } finally {
      memorySaving.value = false
    }
  }

  // ════════════ 发送消息 ════════════

  async function send(content: string) {
    if (!content.trim() || streaming.value) return
    if (!selectedModel.value) {
      error.value = '请先选择模型'
      return
    }

    error.value = ''
    _abortController = new AbortController()
    messages.value.push({ id: ++_msgId, role: 'user', content: content.trim() })
    messages.value.push({ id: ++_msgId, role: 'assistant', content: '' })
    streaming.value = true

    const assistantMsg = messages.value[messages.value.length - 1]
    const history = messages.value.slice(0, -1).map((m) => ({
      role: m.role,
      content: m.content,
    }))

    try {
      for await (const chunk of streamChat(
        selectedModel.value,
        history,
        currentSessionId.value,
        _abortController.signal
      )) {
        if (chunk.type === 'content' && chunk.value) {
          assistantMsg.content += chunk.value
          await scrollToBottom()
        } else if (chunk.type === 'saved' && chunk.sessionId) {
          // 后端总是返回 session_id（新建或已有）
          currentSessionId.value = chunk.sessionId
        }
      }
      // 刷新会话列表（更新 updated_at）
      loadSessions()
    } catch (e: any) {
      if (e.name === 'AbortError') return
      if (!assistantMsg.content) {
        assistantMsg.content = e.message || '请求失败'
      }
      error.value = e.message || '流式响应出错'
    } finally {
      streaming.value = false
      _abortController = null
    }
  }

  function abort() {
    _abortController?.abort()
    _abortController = null
    streaming.value = false
    if (messages.value.length > 0) {
      const last = messages.value[messages.value.length - 1]
      if (last.role === 'assistant' && !last.content) {
        messages.value.pop()
      }
    }
  }

  function clearMessages() {
    abort()
    messages.value = []
    currentSessionId.value = null
    error.value = ''
  }

  async function scrollToBottom() {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }

  onUnmounted(() => {
    abort()
  })

  return {
    messages,
    models,
    selectedModel,
    streaming,
    error,
    messagesContainer,
    sessions,
    currentSessionId,
    sessionsLoaded,
    memory,
    memoryOpen,
    memoryDraft,
    memorySaving,
    loadModels,
    loadSessions,
    startNewSession,
    switchSession,
    removeSession,
    renameSession,
    loadMemory,
    saveMemory,
    send,
    abort,
    clearMessages,
  }
}
