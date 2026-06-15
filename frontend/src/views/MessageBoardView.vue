<template>
  <section class="message-board">
    <div class="container">
      <header class="message-board__header">
        <span class="message-board__label">MESSAGE</span>
        <h1 class="message-board__title">留言板</h1>
      </header>

      <!-- Envelope decoration -->
      <div class="message-board__envelope" :class="{ 'message-board__envelope--open': envelopeOpen }"
        @mouseenter="envelopeOpen = true" @mouseleave="envelopeOpen = false">
        <div class="message-board__envelope-body">
          <div class="message-board__envelope-flap"></div>
          <div class="message-board__envelope-content">
            <div class="message-board__envelope-letter">
              <p class="message-board__envelope-text">给我留言吧~</p>
              <p class="message-board__envelope-sub">欢迎交流，留下你的足迹</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Message form -->
      <div class="message-board__form-card">
        <div class="message-board__form-inner">
          <div class="message-board__form-row">
            <div class="message-board__field">
              <label class="message-board__label-text">昵称</label>
              <input v-model="form.name" class="message-board__input" placeholder="你的名字" />
            </div>
            <div class="message-board__field">
              <label class="message-board__label-text">邮箱 <span class="message-board__optional">(选填)</span></label>
              <input v-model="form.email" type="email" class="message-board__input" placeholder="your@email.com" />
            </div>
          </div>
          <div class="message-board__field">
            <label class="message-board__label-text">留言内容</label>
            <textarea v-model="form.content" class="message-board__textarea" rows="4" placeholder="写下你想说的..."></textarea>
          </div>
          <div class="message-board__captcha-row">
            <div class="message-board__field message-board__captcha-field">
              <label class="message-board__label-text">{{ captchaQuestion }}</label>
              <input v-model="form.captchaAnswer" class="message-board__input" type="number" placeholder="?" />
            </div>
            <button type="button" class="message-board__captcha-refresh" @click="loadCaptcha" title="换一个">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
            </button>
          </div>
          <p v-if="captchaError" class="message-board__captcha-error">{{ captchaError }}</p>
          <button class="message-board__submit" @click="submitMessage" :disabled="!canSubmit">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            {{ submitLoading ? '发送中...' : '发送留言' }}
          </button>
        </div>
      </div>

      <!-- Messages list -->
      <div class="message-board__list">
        <h2 class="message-board__list-title">
          留言 ({{ totalCount }})
        </h2>

        <!-- Loading state -->
        <div v-if="loading" class="message-board__loading">
          <div class="message-board__skeleton" v-for="n in 3" :key="n"></div>
        </div>

        <p v-else-if="loadError" class="message-board__load-error">{{ loadError }}</p>
        <div v-else-if="!messages.length" class="message-board__empty">
          <p>还没有留言，来做第一个留言的人吧！</p>
        </div>
        <TransitionGroup v-else name="msg-list" tag="div" class="message-board__messages">
          <div v-for="msg in messages" :key="msg.id">
            <MessageItem
              :msg="msg"
              :is-admin="isAdmin"
              :replying-to="replyingTo"
              :captcha-question="captchaQuestion"
              :captcha-token="captchaToken"
              :captcha-ts="captchaTs"
              @reply="startReply"
              @delete="handleDelete"
              @submit-reply="submitReply"
              @cancel-reply="cancelReply"
            />
          </div>
        </TransitionGroup>

        <!-- Delete error -->
        <div v-if="deleteError" class="message-board__delete-error">{{ deleteError }}</div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { createMessage, deleteMessage, getMessages, getCaptcha, type MessageRead } from '@/api/messages'
import { useAuthStore } from '@/stores/auth'
import MessageItem from './MessageBoardItem.vue'

const envelopeOpen = ref(false)

const authStore = useAuthStore()

const isAdmin = computed(() => authStore.isAdmin)

const form = reactive({
  name: '',
  email: '',
  content: '',
  captchaAnswer: '',
})

const captchaQuestion = ref('')
const captchaToken = ref('')
const captchaTs = ref(0)
const captchaError = ref('')

const messages = ref<MessageRead[]>([])
const loading = ref(false)
const loadError = ref('')
const deleteError = ref('')
const submitLoading = ref(false)
const replyingTo = ref<number | null>(null)

const canSubmit = computed(() => form.name.trim() && form.content.trim() && form.captchaAnswer.trim() && !submitLoading.value)

const totalCount = computed(() => {
  function countAll(list: MessageRead[]): number {
    return list.reduce((sum, m) => sum + 1 + countAll(m.replies || []), 0)
  }
  return countAll(messages.value)
})

function formatCreatedAt(dateStr: string): string {
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

async function loadCaptcha() {
  try {
    const data = await getCaptcha()
    captchaQuestion.value = data.question
    captchaToken.value = data.token
    captchaTs.value = data.ts
    form.captchaAnswer = ''
    captchaError.value = ''
  } catch {
    captchaError.value = '验证码加载失败，请刷新页面重试'
  }
}

async function loadMessages() {
  loading.value = true
  loadError.value = ''
  try {
    messages.value = await getMessages()
  } catch {
    loadError.value = '留言加载失败，请刷新页面重试'
  } finally {
    loading.value = false
  }
}

async function submitMessage() {
  if (!canSubmit.value) return

  submitLoading.value = true
  captchaError.value = ''
  try {
    const newMessage = await createMessage({
      name: form.name.trim(),
      email: form.email.trim() || undefined,
      content: form.content.trim(),
      captcha_answer: parseInt(form.captchaAnswer, 10),
      captcha_token: captchaToken.value,
      captcha_ts: captchaTs.value,
    })
    messages.value.unshift(newMessage)

    form.name = ''
    form.email = ''
    form.content = ''
    await loadCaptcha()
  } catch (error: any) {
    captchaError.value = error?.response?.data?.detail || '发送失败'
    await loadCaptcha()
  } finally {
    submitLoading.value = false
  }
}

function startReply(msgId: number) {
  replyingTo.value = msgId
}

function cancelReply() {
  replyingTo.value = null
}

async function submitReply(parentId: number, payload: { name: string; email?: string; content: string }) {
  captchaError.value = ''
  try {
    const reply = await createMessage({
      name: payload.name.trim(),
      email: payload.email?.trim() || undefined,
      content: payload.content.trim(),
      parent_id: parentId,
      captcha_answer: parseInt(form.captchaAnswer, 10),
      captcha_token: captchaToken.value,
      captcha_ts: captchaTs.value,
    })
    insertReply(messages.value, parentId, reply)
    replyingTo.value = null
    await loadCaptcha()
  } catch (error: any) {
    captchaError.value = error?.response?.data?.detail || '回复失败，请重试验证码'
    await loadCaptcha()
  }
}

function insertReply(list: MessageRead[], parentId: number, reply: MessageRead): boolean {
  for (const m of list) {
    if (m.id === parentId) {
      if (!m.replies) m.replies = []
      m.replies.push(reply)
      return true
    }
    if (m.replies && insertReply(m.replies, parentId, reply)) return true
  }
  return false
}

async function handleDelete(msgId: number) {
  deleteError.value = ''
  try {
    await deleteMessage(msgId)
    removeMessage(messages.value, msgId)
  } catch {
    deleteError.value = '删除留言失败，请稍后重试'
  }
}

function removeMessage(list: MessageRead[], id: number): boolean {
  const idx = list.findIndex(m => m.id === id)
  if (idx !== -1) {
    list.splice(idx, 1)
    return true
  }
  for (const m of list) {
    if (m.replies && removeMessage(m.replies, id)) return true
  }
  return false
}

onMounted(() => {
  loadMessages()
  loadCaptcha()
})
</script>

<style scoped>
.message-board {
  padding: var(--space-3xl) 0;
}

.message-board__header {
  margin-bottom: var(--space-xl);
}

.message-board__label {
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.message-board__title {
  font-size: clamp(1.6rem, 3.5vw, 2.2rem);
  margin: var(--space-xs) 0;
}

/* Envelope */
.message-board__envelope {
  max-width: 320px;
  margin: 0 auto var(--space-xl);
  perspective: 800px;
}

.message-board__envelope-body {
  position: relative;
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-card-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.message-board__envelope-flap {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: var(--color-surface-strong);
  clip-path: polygon(0 0, 50% 100%, 100% 0);
  transform-origin: top center;
  transition: transform 0.5s var(--ease-spring);
  z-index: 2;
}

.message-board__envelope--open .message-board__envelope-flap {
  transform: rotateX(180deg);
}

.message-board__envelope-content {
  padding: var(--space-2xl) var(--space-lg) var(--space-lg);
}

.message-board__envelope-letter {
  text-align: center;
}

.message-board__envelope-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin-bottom: 4px;
}

.message-board__envelope-sub {
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

/* Form */
.message-board__form-card {
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  margin-bottom: var(--space-xl);
  position: relative;
  overflow: hidden;
}

.message-board__form-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--glass-noise);
  background-size: 128px 128px;
  pointer-events: none;
}

.message-board__form-inner {
  padding: var(--space-lg);
  position: relative;
  z-index: 1;
}

.message-board__form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.message-board__field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: var(--space-md);
}

.message-board__label-text {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-soft);
}

.message-board__optional {
  color: var(--color-text-muted);
  font-weight: 400;
}

.message-board__input,
.message-board__textarea {
  padding: 10px 14px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  font-family: inherit;
  font-size: 0.9rem;
  outline: none;
  transition: border-color var(--duration-fast) ease;
}

.message-board__input:focus,
.message-board__textarea:focus {
  border-color: var(--color-accent);
}

.message-board__textarea {
  resize: vertical;
  min-height: 80px;
}

.message-board__submit {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-full);
  background: var(--accent-tint-10);
  color: var(--color-accent);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.message-board__submit:hover:not(:disabled) {
  background: var(--accent-tint-20);
  transform: translateY(-1px);
}

.message-board__submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.message-board__captcha-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.message-board__captcha-field {
  flex: 1;
}

.message-board__captcha-refresh {
  background: none;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s;
  margin-bottom: 0;
}

.message-board__captcha-refresh:hover {
  color: var(--primary);
}

.message-board__captcha-error {
  color: #ef4444;
  font-size: 0.85rem;
  margin: 4px 0 0;
}

.message-board__load-error {
  color: #ef4444;
  font-size: 0.88rem;
  text-align: center;
  padding: var(--space-lg);
}

.message-board__delete-error {
  color: #ef4444;
  font-size: 0.82rem;
  padding: var(--space-sm) var(--space-md);
  margin-top: var(--space-md);
  border: 1px solid var(--error-border-30);
  border-radius: var(--radius-sm);
  background: var(--error-bg-06);
}

.message-board__loading {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.message-board__skeleton {
  height: 80px;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
}

.message-board__empty {
  text-align: center;
  padding: var(--space-2xl);
  color: var(--color-text-muted);
  font-size: 0.9rem;
  border: 1px dashed var(--glass-border);
  border-radius: var(--radius-md);
  background: var(--glass-bg-03);
}

/* Messages list */
.message-board__list-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin-bottom: var(--space-md);
}

.message-board__messages {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

/* List transitions */
.msg-list-enter-active {
  transition: all 0.4s var(--ease-spring);
}
.msg-list-enter-from {
  opacity: 0;
  transform: translateY(-12px);
}

@media (max-width: 640px) {
  .message-board {
    padding: var(--space-xl) 0;
  }

  .message-board__form-row {
    grid-template-columns: 1fr;
  }

  .message-board__envelope {
    max-width: 100%;
  }

  .message-board__form-inner {
    padding: var(--space-md);
  }
}
</style>
