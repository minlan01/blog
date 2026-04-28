<template>
  <section class="chat">
    <div class="container chat-container">
      <!-- Header -->
      <header class="chat__header">
        <p class="chat__kicker">AI ASSISTANT</p>
        <h1 class="chat__title">AI 对话</h1>
      </header>

      <!-- Controls -->
      <div class="chat__controls">
        <select v-model="selectedModel" class="chat__model-select" :disabled="streaming">
          <option value="" disabled>选择模型</option>
          <option v-for="m in models" :key="m.name" :value="m.name">{{ m.name }}</option>
        </select>
        <button class="chat__clear-btn" @click="clearMessages" :disabled="streaming || messages.length === 0">
          清空对话
        </button>
      </div>

      <!-- Error -->
      <div v-if="error" class="chat__error">{{ error }}</div>

      <!-- Messages -->
      <div class="chat__messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="chat__empty">
          <p>选择一个模型，开始与 AI 对话</p>
        </div>
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="chat__bubble"
          :class="[`chat__bubble--${msg.role}`]"
        >
          <div class="chat__bubble-role">{{ msg.role === 'user' ? '你' : 'AI' }}</div>
          <div class="chat__bubble-content">
            <span>{{ msg.content }}</span>
            <span v-if="msg.role === 'assistant' && streaming && i === messages.length - 1" class="chat__cursor"></span>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="chat__input-area">
        <textarea
          v-model="input"
          class="chat__input"
          placeholder="输入消息… (Enter 发送, Shift+Enter 换行)"
          rows="1"
          :disabled="streaming"
          @keydown="onKeydown"
        ></textarea>
        <button class="chat__send-btn" @click="handleSend" :disabled="streaming || !input.trim()">
          发送
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useChat } from '@/composables/useChat'

const {
  messages,
  models,
  selectedModel,
  streaming,
  error,
  messagesContainer,
  loadModels,
  send,
  clearMessages
} = useChat()

const input = ref('')

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

async function handleSend() {
  const text = input.value
  if (!text.trim() || streaming.value) return
  input.value = ''
  await send(text)
}

onMounted(() => {
  loadModels()
})
</script>

<style scoped>
.chat {
  padding: var(--space-3xl) 0;
  min-height: calc(100vh - var(--header-height));
  display: flex;
  flex-direction: column;
}

.chat-container {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - var(--header-height) - var(--space-3xl) * 2);
}

.chat__header {
  margin-bottom: var(--space-xl);
}

.chat__kicker {
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.22em;
  color: var(--color-accent);
  margin: 0 0 var(--space-sm);
}

.chat__title {
  font-size: clamp(2rem, 5vw, 3rem);
  margin: 0;
}

/* ====== Controls ====== */
.chat__controls {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
  align-items: center;
}

.chat__model-select {
  flex: 1;
  max-width: 280px;
  padding: 8px 12px;
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: 0.88rem;
  outline: none;
  cursor: pointer;
  transition: border-color var(--duration-fast) ease;
}

.chat__model-select:focus {
  border-color: var(--color-accent);
}

.chat__model-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat__clear-btn {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  color: var(--color-text-soft);
  font-size: 0.82rem;
  cursor: pointer;
  transition: border-color var(--duration-fast) ease, color var(--duration-fast) ease;
}

.chat__clear-btn:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-text);
}

.chat__clear-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ====== Error ====== */
.chat__error {
  background: var(--error-bg-12);
  border: 1px solid var(--error-border-30);
  color: var(--error-main);
  border-radius: var(--radius-md);
  padding: 10px 16px;
  font-size: 0.85rem;
  margin-bottom: var(--space-md);
}

/* ====== Messages ====== */
.chat__messages {
  flex: 1;
  min-height: 400px;
  max-height: 72vh;
  overflow-y: auto;
  padding: var(--space-lg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  box-shadow:
    0 4px 24px rgba(0, 0, 0, 0.25),
    var(--glass-highlight);
  margin-bottom: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  position: relative;
}

.chat__messages::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--glass-noise);
  background-size: 128px 128px;
  pointer-events: none;
  z-index: 0;
}

.chat__empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  position: relative;
  z-index: 1;
}

.chat__bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

.chat__bubble--user {
  align-self: flex-end;
  background: var(--accent-tint-12);
  border: 1px solid var(--accent-tint-25);
}

.chat__bubble--assistant {
  align-self: flex-start;
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
}

.chat__bubble-role {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
  margin-bottom: 4px;
  text-transform: uppercase;
}

.chat__bubble--user .chat__bubble-role {
  color: var(--accent-tint-60);
}

.chat__bubble-content {
  font-size: 0.9rem;
  color: var(--color-text);
  white-space: pre-wrap;
  word-break: break-word;
}

/* ====== Cursor ====== */
.chat__cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: var(--color-accent);
  margin-left: 2px;
  vertical-align: text-bottom;
  animation: blink 0.8s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

/* ====== Input Area ====== */
.chat__input-area {
  display: flex;
  gap: var(--space-md);
  align-items: flex-end;
}

.chat__input {
  flex: 1;
  padding: 10px 14px;
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: 0.88rem;
  font-family: inherit;
  resize: none;
  outline: none;
  min-height: 42px;
  max-height: 120px;
  line-height: 1.5;
  transition: border-color var(--duration-fast) ease;
}

.chat__input:focus {
  border-color: var(--color-accent);
}

.chat__input:disabled {
  opacity: 0.5;
}

.chat__input::placeholder {
  color: var(--color-text-muted);
}

.chat__send-btn {
  padding: 10px 20px;
  background: var(--color-accent);
  border: none;
  border-radius: var(--radius-md);
  color: #0a0a12;
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  transition: opacity var(--duration-fast) ease;
  white-space: nowrap;
}

.chat__send-btn:hover:not(:disabled) {
  opacity: 0.85;
}

.chat__send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ====== Responsive ====== */
@media (max-width: 640px) {
  .chat__controls {
    flex-direction: column;
  }

  .chat__model-select {
    max-width: 100%;
  }

  .chat__bubble {
    max-width: 92%;
  }

  .chat__messages {
    max-height: 55vh;
    min-height: 280px;
    padding: var(--space-md);
  }
}
</style>
