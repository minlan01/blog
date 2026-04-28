<template>
  <div class="msg-item" :class="{ 'msg-item--reply': isReply }">
    <div class="msg-item__avatar" :style="{ background: msg.color }">
      {{ msg.name.charAt(0).toUpperCase() }}
    </div>
    <div class="msg-item__body">
      <div class="msg-item__meta">
        <span class="msg-item__name">{{ msg.name }}</span>
        <span class="msg-item__time">{{ formatCreatedAt(msg.created_at) }}</span>
      </div>
      <p class="msg-item__content">{{ msg.content }}</p>
      <div class="msg-item__actions">
        <button class="msg-item__action msg-item__action--reply" @click="emit('reply', msg.id)">回复</button>
        <button v-if="isAdmin" class="msg-item__action msg-item__action--delete" @click="emit('delete', msg.id)">删除</button>
      </div>

      <!-- Reply form -->
      <form
        v-if="replyingTo === msg.id"
        class="msg-item__reply-form"
        @submit.prevent="handleSubmitReply"
      >
        <div class="msg-item__reply-fields">
          <input v-model="replyName" class="msg-item__reply-input" placeholder="你的名字" />
          <textarea
            v-model="replyContent"
            class="msg-item__reply-textarea"
            :placeholder="`回复 ${msg.name}...`"
            rows="2"
          ></textarea>
        </div>
        <div class="msg-item__reply-actions">
          <button type="submit" class="msg-item__reply-submit" :disabled="!replyName.trim() || !replyContent.trim()">回复</button>
          <button type="button" class="msg-item__reply-cancel" @click="emit('cancel-reply')">取消</button>
        </div>
      </form>

      <!-- Nested replies -->
      <div v-if="msg.replies?.length" class="msg-item__replies">
        <MessageBoardItem
          v-for="reply in msg.replies"
          :key="reply.id"
          :msg="reply"
          :is-admin="isAdmin"
          :replying-to="replyingTo"
          :is-reply="true"
          @reply="emit('reply', $event)"
          @delete="emit('delete', $event)"
          @submit-reply="(parentId, payload) => emit('submit-reply', parentId, payload)"
          @cancel-reply="emit('cancel-reply')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { MessageRead } from '@/api/messages'

const props = defineProps<{
  msg: MessageRead
  isAdmin: boolean
  replyingTo: number | null
  isReply?: boolean
}>()

const emit = defineEmits<{
  (e: 'reply', msgId: number): void
  (e: 'delete', msgId: number): void
  (e: 'submit-reply', parentId: number, payload: { name: string; email?: string; content: string }): void
  (e: 'cancel-reply'): void
}>()

const replyName = ref('')
const replyContent = ref('')

function formatCreatedAt(dateStr: string): string {
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

function handleSubmitReply() {
  if (!replyName.value.trim() || !replyContent.value.trim()) return
  emit('submit-reply', props.msg.id, {
    name: replyName.value.trim(),
    content: replyContent.value.trim(),
  })
  replyName.value = ''
  replyContent.value = ''
}
</script>

<style scoped>
.msg-item {
  display: flex;
  gap: 12px;
  padding: var(--space-md);
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-card-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  transition: border-color var(--duration-fast) ease;
}

.msg-item:hover {
  border-color: var(--accent-tint-20);
}

.msg-item--reply {
  margin-top: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--glass-bg-05);
  border-left: 3px solid var(--accent-tint-30);
}

.msg-item__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: 0.88rem;
  flex-shrink: 0;
}

.msg-item--reply .msg-item__avatar {
  width: 30px;
  height: 30px;
  font-size: 0.78rem;
}

.msg-item__body {
  flex: 1;
  min-width: 0;
}

.msg-item__meta {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: 4px;
}

.msg-item__name {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--color-text-heading);
}

.msg-item__time {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

.msg-item__content {
  font-size: 0.88rem;
  color: var(--color-text-soft);
  line-height: 1.6;
  margin-bottom: 4px;
}

.msg-item__actions {
  display: flex;
  gap: var(--space-sm);
}

.msg-item__action {
  font-size: 0.75rem;
  padding: 2px 8px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  background: none;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  color: var(--color-text-muted);
}

.msg-item__action--reply:hover {
  color: var(--color-accent);
  border-color: var(--accent-tint-30);
  background: var(--accent-tint-08);
}

.msg-item__action--delete:hover {
  color: var(--error-main);
  border-color: var(--error-border-40);
  background: var(--error-bg-12);
}

/* Reply form */
.msg-item__reply-form {
  margin-top: var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.msg-item__reply-fields {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.msg-item__reply-input {
  max-width: 200px;
  padding: 6px 10px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  font-family: inherit;
  font-size: 0.85rem;
  outline: none;
  transition: border-color var(--duration-fast) ease;
}

.msg-item__reply-input:focus {
  border-color: var(--color-accent);
}

.msg-item__reply-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  font-family: inherit;
  font-size: 0.85rem;
  outline: none;
  resize: vertical;
  min-height: 50px;
  transition: border-color var(--duration-fast) ease;
}

.msg-item__reply-textarea:focus {
  border-color: var(--color-accent);
}

.msg-item__reply-actions {
  display: flex;
  gap: var(--space-sm);
}

.msg-item__reply-submit {
  padding: 5px 14px;
  border: 1px solid var(--accent-tint-30);
  border-radius: var(--radius-sm);
  background: var(--accent-tint-10);
  color: var(--color-accent);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.msg-item__reply-submit:hover:not(:disabled) {
  background: var(--accent-tint-20);
}

.msg-item__reply-submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.msg-item__reply-cancel {
  padding: 5px 14px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  background: none;
  color: var(--color-text-muted);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.msg-item__reply-cancel:hover {
  color: var(--color-text);
  border-color: var(--border-strong);
}

/* Nested replies */
.msg-item__replies {
  margin-top: var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

@media (max-width: 640px) {
  .msg-item {
    padding: var(--space-sm);
    gap: 10px;
  }

  .msg-item__avatar {
    width: 32px;
    height: 32px;
    font-size: 0.82rem;
  }
}
</style>
