<template>
  <section class="chat">
    <div class="chat__body">
      <!-- ── 侧边栏 ── -->
      <aside class="chat__sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="chat__sidebar-header">
          <span class="chat__sidebar-title">对话历史</span>
          <button class="chat__sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed" title="收起/展开">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path v-if="sidebarCollapsed" d="m9 18 6-6-6-6" />
              <path v-else d="m15 18-6-6 6-6" />
            </svg>
          </button>
        </div>

        <button class="chat__new-btn" @click="startNewSession" :disabled="streaming">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>
          新对话
        </button>

        <div class="chat__session-list">
          <div v-if="!sessionsLoaded" class="chat__sidebar-loading">加载中...</div>
          <div v-else-if="sessions.length === 0" class="chat__sidebar-empty">
            暂无历史对话
          </div>
          <div
            v-for="s in sessions"
            :key="s.id"
            class="chat__session-item"
            :class="{ active: s.id === currentSessionId }"
            @click="switchSession(s.id)"
          >
            <div class="chat__session-info">
              <div class="chat__session-title">{{ s.title }}</div>
              <div class="chat__session-meta">{{ s.message_count }} 条</div>
            </div>
            <button
              class="chat__session-delete"
              title="删除"
              @click.stop="confirmDelete(s.id, s.title)"
              :disabled="streaming"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/></svg>
            </button>
          </div>
        </div>

        <button class="chat__memory-btn" @click="memoryOpen = true">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          AI 记忆
          <span v-if="memory" class="chat__memory-dot"></span>
        </button>
      </aside>

      <!-- ── 主对话区 ── -->
      <div class="chat__main">
        <!-- 顶栏 -->
        <div class="chat__topbar">
          <button v-if="sidebarCollapsed" class="chat__expand-btn" @click="sidebarCollapsed = false">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
          </button>
          <select v-model="selectedModel" class="chat__model-select" :disabled="streaming">
            <option value="" disabled>选择模型</option>
            <option v-for="m in models" :key="m.name" :value="m.name">{{ m.name }}</option>
          </select>
          <div class="chat__topbar-right">
            <button v-if="memory" class="chat__memory-badge" @click="memoryOpen = true" title="点击编辑记忆">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
              记忆已启用
            </button>
            <button v-if="messages.length > 0" class="chat__clear-btn" @click="clearMessages" :disabled="streaming">
              清空
            </button>
          </div>
        </div>

        <div v-if="error" class="chat__error">{{ error }}</div>

        <!-- 消息区 -->
        <div class="chat__messages" ref="messagesContainer">
          <!-- 空状态 -->
          <div v-if="messages.length === 0" class="chat__welcome">
            <div class="chat__welcome-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 8V4H8M4 4h16v16H4z"/><path d="M2 14h20M9 14v4M15 14v4"/>
              </svg>
            </div>
            <h2 class="chat__welcome-title">开始一段新对话</h2>
            <p class="chat__welcome-desc">
              {{ memory ? 'AI 已记住你的偏好，直接开始提问' : '选择模型，输入你的问题' }}
            </p>
            <div class="chat__welcome-hints">
              <button class="chat__hint-chip" @click="useHint('解释一下 Vue 3 的 Composition API')">解释 Vue 3 Composition API</button>
              <button class="chat__hint-chip" @click="useHint('写一个 Python 快速排序')">写一个 Python 快排</button>
              <button class="chat__hint-chip" @click="useHint('FastAPI 和 Django 有什么区别？')">FastAPI vs Django</button>
            </div>
          </div>

          <!-- 消息列表（全宽线性流式） -->
          <div
            v-for="(msg, i) in messages"
            :key="msg.id"
            class="msg-row"
            :class="`msg-row--${msg.role}`"
          >
            <!-- 头像 -->
            <div class="msg-row__avatar" :class="`msg-row__avatar--${msg.role}`">
              <svg v-if="msg.role === 'user'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M2 14h20M9 14v4M15 14v4"/></svg>
            </div>
            <!-- 内容 -->
            <div class="msg-row__content">
              <div class="msg-row__role">{{ msg.role === 'user' ? '你' : 'AI 助手' }}</div>
              <div class="msg-row__text">
                <span>{{ msg.content }}</span>
                <span v-if="msg.role === 'assistant' && streaming && i === messages.length - 1" class="msg-row__typing"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="chat__input-area">
          <textarea
            v-model="input"
            class="chat__input"
            placeholder="输入消息… (Enter 发送, Shift+Enter 换行)"
            rows="1"
            ref="inputEl"
            :disabled="streaming"
            @keydown="onKeydown"
            @input="autoResize"
          ></textarea>
          <button class="chat__send-btn" @click="handleSend" :disabled="streaming || !input.trim()">
            <svg v-if="!streaming" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="chat__send-spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- ── 记忆编辑弹窗 ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="memoryOpen" class="modal-overlay" @click.self="memoryOpen = false">
          <div class="modal">
            <h3 class="modal__title">AI 记忆</h3>
            <p class="modal__desc">
              这段文字会作为系统提示词注入每一次对话。写入你的身份偏好、技术栈、代码风格等，AI 会跨会话记住。
            </p>
            <div class="modal__body">
              <textarea
                v-model="memoryDraft"
                class="modal__textarea"
                placeholder="例：我是 Python 后端开发者，偏好简洁代码，用中文回答，代码注释也用中文..."
                rows="8"
              ></textarea>
              <div class="modal__char-count">{{ memoryDraft.length }} / 5000</div>
            </div>
            <div class="modal__actions">
              <button class="modal__btn modal__btn--cancel" @click="memoryOpen = false">取消</button>
              <button class="modal__btn modal__btn--save" @click="saveAndCloseMemory" :disabled="memorySaving">
                {{ memorySaving ? '保存中...' : '保存' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useChat } from '@/composables/useChat'

const {
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
  loadMemory,
  saveMemory,
  send,
  clearMessages,
} = useChat()

const input = ref('')
const inputEl = ref<HTMLTextAreaElement | null>(null)
// 移动端默认收起侧栏，避免 240px 面板遮住对话区
const sidebarCollapsed = ref(window.innerWidth < 768)

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
  await nextTick()
  autoResize()
  await send(text)
}

function useHint(text: string) {
  input.value = text
  inputEl.value?.focus()
}

function autoResize() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

async function confirmDelete(id: number, title: string) {
  if (confirm(`确定删除对话「${title}」？`)) {
    await removeSession(id)
  }
}

async function saveAndCloseMemory() {
  await saveMemory()
  memoryOpen.value = false
}

onMounted(() => {
  loadModels()
  loadSessions()
  loadMemory()
  // 锁定 body 滚动，防止 AI 页面滑动导致输入框被挡
  document.body.style.overflow = 'hidden'
})

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* ═══════════════════════════════════════════════
   全局容器 — 全屏布局（覆盖标准 container/footer）
   ═══════════════════════════════════════════════ */
.chat {
  position: fixed;
  top: var(--header-height);
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10;
  overflow: hidden;
  background: rgba(10, 10, 18, 0.55);
}

[data-theme="light"] .chat {
  background: rgba(250, 247, 242, 0.6);
}

.chat__body {
  display: flex;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

/* ═══════════════════════════════════════════════
   侧边栏
   ═══════════════════════════════════════════════ */
.chat__sidebar {
  width: 240px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-sm);
  border-right: 1px solid var(--glass-border);
  transition: width 0.2s ease, padding 0.2s ease;
  overflow: hidden;
}

.chat__sidebar.collapsed {
  width: 0;
  padding: 0;
  border-right: none;
}

.chat__sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xs);
}

.chat__sidebar-title {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.chat__sidebar-toggle {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  display: flex;
  transition: background var(--duration-fast) ease, color var(--duration-fast) ease;
}

.chat__sidebar-toggle:hover {
  background: var(--glass-card-bg);
  color: var(--color-text);
}

.chat__new-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 9px 14px;
  background: var(--color-accent);
  border: none;
  border-radius: var(--radius-md);
  color: #0a0a12;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: opacity var(--duration-fast) ease;
  white-space: nowrap;
}

.chat__new-btn:hover:not(:disabled) {
  opacity: 0.85;
}

.chat__new-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.chat__session-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-height: 0;
}

.chat__sidebar-loading,
.chat__sidebar-empty {
  padding: var(--space-lg) var(--space-sm);
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.8rem;
}

.chat__session-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 10px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast) ease;
}

.chat__session-item:hover {
  background: var(--glass-card-bg);
}

.chat__session-item.active {
  background: var(--accent-tint-12);
}

.chat__session-info {
  flex: 1;
  min-width: 0;
}

.chat__session-title {
  font-size: 0.82rem;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat__session-meta {
  font-size: 0.68rem;
  color: var(--color-text-muted);
  margin-top: 1px;
}

.chat__session-delete {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast) ease;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
}

.chat__session-item:hover .chat__session-delete {
  opacity: 1;
}

.chat__session-delete:hover:not(:disabled) {
  background: var(--error-bg-12);
  color: var(--error-main);
}

.chat__memory-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  color: var(--color-text-soft);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  white-space: nowrap;
}

.chat__memory-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-text);
}

.chat__memory-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent);
  margin-left: auto;
}

/* ═══════════════════════════════════════════════
   主对话区
   ═══════════════════════════════════════════════ */
.chat__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
}

/* ── 顶栏 ── */
.chat__topbar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  border-bottom: 1px solid var(--glass-border);
  min-height: 48px;
}

.chat__expand-btn {
  background: transparent;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 4px;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  transition: all var(--duration-fast) ease;
}

.chat__expand-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-text);
}

.chat__model-select {
  padding: 6px 12px;
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: 0.85rem;
  outline: none;
  cursor: pointer;
  transition: border-color var(--duration-fast) ease;
}

.chat__model-select:focus {
  border-color: var(--color-accent);
}

.chat__model-select:disabled {
  opacity: 0.5;
}

.chat__topbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.chat__memory-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--accent-tint-12);
  border: 1px solid var(--accent-tint-25);
  border-radius: 999px;
  color: var(--accent-tint-60);
  font-size: 0.72rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity var(--duration-fast) ease;
}

.chat__memory-badge:hover {
  opacity: 0.8;
}

.chat__clear-btn {
  padding: 6px 14px;
  background: transparent;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  color: var(--color-text-soft);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.chat__clear-btn:hover:not(:disabled) {
  border-color: var(--error-main);
  color: var(--error-main);
}

/* ── 错误 ── */
.chat__error {
  margin: var(--space-sm) var(--space-lg);
  background: var(--error-bg-12);
  border: 1px solid var(--error-border-30);
  color: var(--error-main);
  border-radius: var(--radius-md);
  padding: 8px 14px;
  font-size: 0.82rem;
}

/* ═══════════════════════════════════════════════
   消息区 — 全宽线性流式
   ═══════════════════════════════════════════════ */
.chat__messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-lg) 0;
}

/* ── 空状态欢迎 ── */
.chat__welcome {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-xl);
}

.chat__welcome-icon {
  color: var(--color-text-muted);
  opacity: 0.5;
  margin-bottom: var(--space-sm);
}

.chat__welcome-title {
  font-size: 1.4rem;
  margin: 0;
  color: var(--color-text);
}

.chat__welcome-desc {
  font-size: 0.88rem;
  color: var(--color-text-muted);
  margin: 0;
}

.chat__welcome-hints {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin-top: var(--space-lg);
  max-width: 500px;
  justify-content: center;
}

.chat__hint-chip {
  padding: 7px 16px;
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  color: var(--color-text-soft);
  font-size: 0.82rem;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.chat__hint-chip:hover {
  border-color: var(--color-accent);
  color: var(--color-text);
  background: var(--accent-tint-12);
}

/* ── 单条消息行 ── */
.msg-row {
  display: flex;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  max-width: 820px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  animation: msg-fade-in 0.3s ease;
}

@keyframes msg-fade-in {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.msg-row--user {
  background: var(--accent-tint-08, rgba(99, 102, 241, 0.04));
}

[data-theme="light"] .msg-row--user {
  background: rgba(217, 119, 6, 0.05);
}

.msg-row__avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
}

.msg-row__avatar--user {
  background: var(--accent-tint-15, rgba(99, 102, 241, 0.15));
  color: var(--color-accent);
}

[data-theme="light"] .msg-row__avatar--user {
  background: rgba(217, 119, 6, 0.15);
  color: #d97706;
}

.msg-row__avatar--assistant {
  background: var(--glass-card-bg);
  color: var(--color-text-soft);
  border: 1px solid var(--glass-border);
}

.msg-row__content {
  flex: 1;
  min-width: 0;
}

.msg-row__role {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
  margin-bottom: 4px;
}

.msg-row__text {
  font-size: 0.9rem;
  line-height: 1.7;
  color: var(--color-text);
  white-space: pre-wrap;
  word-break: break-word;
}

/* ── 流式打字指示器 ── */
.msg-row__typing {
  display: inline-block;
  width: 6px;
  height: 16px;
  background: var(--color-accent);
  margin-left: 3px;
  vertical-align: text-bottom;
  border-radius: 1px;
  animation: typing-pulse 1s ease-in-out infinite;
}

@keyframes typing-pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* ═══════════════════════════════════════════════
   输入区
   ═══════════════════════════════════════════════ */
.chat__input-area {
  display: flex;
  gap: var(--space-sm);
  align-items: flex-end;
  padding: var(--space-sm) var(--space-lg) var(--space-md);
  border-top: 1px solid var(--glass-border);
  max-width: 820px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.chat__input {
  flex: 1;
  padding: 10px 14px;
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
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
  box-shadow: 0 0 0 3px var(--accent-tint-12, rgba(99, 102, 241, 0.1));
}

[data-theme="light"] .chat__input:focus {
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.1);
}

.chat__input:disabled {
  opacity: 0.5;
}

.chat__input::placeholder {
  color: var(--color-text-muted);
}

.chat__send-btn {
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  background: var(--color-accent);
  border: none;
  border-radius: var(--radius-lg);
  color: #0a0a12;
  cursor: pointer;
  transition: opacity var(--duration-fast) ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat__send-btn:hover:not(:disabled) {
  opacity: 0.85;
}

.chat__send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.chat__send-spin {
  animation: spin 0.8s linear infinite;
}

/* ═══════════════════════════════════════════════
   记忆弹窗
   ═══════════════════════════════════════════════ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  width: 90%;
  max-width: 540px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.modal__title {
  margin: 0 0 var(--space-sm);
  font-size: 1.2rem;
}

.modal__desc {
  margin: 0 0 var(--space-lg);
  font-size: 0.82rem;
  color: var(--color-text-muted);
  line-height: 1.6;
}

.modal__body {
  margin-bottom: var(--space-lg);
}

.modal__textarea {
  width: 100%;
  padding: 12px;
  background: var(--color-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: 0.88rem;
  font-family: inherit;
  resize: vertical;
  outline: none;
  line-height: 1.6;
  transition: border-color var(--duration-fast) ease;
  box-sizing: border-box;
}

.modal__textarea:focus {
  border-color: var(--color-accent);
}

.modal__char-count {
  text-align: right;
  font-size: 0.72rem;
  color: var(--color-text-muted);
  margin-top: 4px;
}

.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
}

.modal__btn {
  padding: 8px 20px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity var(--duration-fast) ease;
}

.modal__btn--cancel {
  background: transparent;
  color: var(--color-text-soft);
  border: 1px solid var(--color-border-strong);
}

.modal__btn--save {
  background: var(--color-accent);
  color: #0a0a12;
  font-weight: 600;
}

.modal__btn:hover:not(:disabled) {
  opacity: 0.85;
}

.modal__btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ═══════════════════════════════════════════════
   弹窗动画
   ═══════════════════════════════════════════════ */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .modal,
.modal-leave-active .modal {
  transition: transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal,
.modal-leave-to .modal {
  transform: scale(0.95);
}

/* ��══════════════════════════════════════════════
   响应式
   ═══════════════════════════════════════════════ */
@media (max-width: 768px) {
  .chat {
    height: calc(100vh - var(--header-height));
  }

  .chat__sidebar {
    position: absolute;
    z-index: 100;
    height: 100%;
    background: rgba(10, 10, 18, 0.92);
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
  }

  [data-theme="light"] .chat__sidebar {
    background: rgba(250, 247, 242, 0.95);
  }

  .chat__sidebar.collapsed {
    width: 0;
    border-right: none;
  }

  .msg-row {
    padding: var(--space-sm) var(--space-md);
  }

  .chat__input-area {
    padding: var(--space-sm) var(--space-md);
  }

  .chat__topbar {
    padding: var(--space-sm) var(--space-md);
  }

  .chat__welcome-hints {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (max-width: 480px) {
  .chat__model-select {
    font-size: 0.78rem;
    max-width: 140px;
  }

  .msg-row {
    gap: var(--space-sm);
  }

  .msg-row__avatar {
    width: 28px;
    height: 28px;
  }
}
</style>
