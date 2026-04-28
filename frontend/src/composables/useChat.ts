import { nextTick, ref } from 'vue'
import { getModels, streamChat } from '@/api/chat'
import type { ModelInfo } from '@/api/chat'

export interface Message {
  role: 'user' | 'assistant'
  content: string
}

export function useChat() {
  const messages = ref<Message[]>([])
  const models = ref<ModelInfo[]>([])
  const selectedModel = ref('')
  const streaming = ref(false)
  const error = ref('')
  const messagesContainer = ref<HTMLElement | null>(null)

  async function loadModels() {
    try {
      models.value = await getModels()
      if (models.value.length > 0 && !selectedModel.value) {
        selectedModel.value = models.value[0].name
      }
    } catch {
      error.value = '无法获取模型列表，请确认 llama.cpp server 正在运行'
    }
  }

  async function send(content: string) {
    if (!content.trim() || streaming.value) return
    if (!selectedModel.value) {
      error.value = '请先选择模型'
      return
    }

    error.value = ''
    messages.value.push({ role: 'user', content: content.trim() })
    messages.value.push({ role: 'assistant', content: '' })
    streaming.value = true

    const assistantMsg = messages.value[messages.value.length - 1]
    const history = messages.value.slice(0, -1).map((m) => ({
      role: m.role,
      content: m.content
    }))

    try {
      for await (const token of streamChat(selectedModel.value, history)) {
        assistantMsg.content += token
        await scrollToBottom()
      }
    } catch (e: any) {
      if (!assistantMsg.content) {
        assistantMsg.content = e.message || '请求失败'
      }
      error.value = e.message || '流式响应出错'
    } finally {
      streaming.value = false
    }
  }

  function clearMessages() {
    messages.value = []
    error.value = ''
  }

  async function scrollToBottom() {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }

  return {
    messages,
    models,
    selectedModel,
    streaming,
    error,
    messagesContainer,
    loadModels,
    send,
    clearMessages
  }
}
