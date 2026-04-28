<template>
  <div class="comment-item">
    <div class="comment-item__main">
      <div class="comment-item__header">
        <span class="comment-item__author">{{ comment.author_name || '匿名' }}</span>
        <span class="comment-item__date">{{ formatDate(comment.created_at) }}</span>
      </div>
      <p class="comment-item__content">{{ comment.content }}</p>
      <div class="comment-item__actions">
        <button
          v-if="isLoggedIn"
          class="comment-item__action comment-item__action--reply"
          @click="emit('reply', comment.id)"
        >回复</button>
        <button
          v-if="canDelete"
          class="comment-item__action comment-item__action--delete"
          @click="emit('delete', comment.id)"
        >删除</button>
      </div>
    </div>

    <!-- Reply form -->
    <form
      v-if="replyingTo === comment.id"
      class="comment-item__reply-form"
      @submit.prevent="handleSubmitReply"
    >
      <textarea
        v-model="replyContent"
        class="comment-item__reply-textarea"
        :placeholder="`回复 ${comment.author_name || '匿名'}...`"
        rows="2"
        required
      ></textarea>
      <div class="comment-item__reply-actions">
        <button type="submit" class="comment-item__reply-submit" :disabled="!replyContent.trim()">回复</button>
        <button type="button" class="comment-item__reply-cancel" @click="emit('cancel-reply')">取消</button>
      </div>
    </form>

    <!-- Nested replies -->
    <div v-if="comment.replies?.length" class="comment-item__replies">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :user-id="userId"
        :is-admin="isAdmin"
        :is-logged-in="isLoggedIn"
        :replying-to="replyingTo"
        :is-reply="true"
        @reply="emit('reply', $event)"
        @delete="emit('delete', $event)"
        @submit-reply="(id: number, content: string) => emit('submit-reply', id, content)"
        @cancel-reply="emit('cancel-reply')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { CommentRead } from '@/types/blog'

const props = defineProps<{
  comment: CommentRead
  userId?: number
  isAdmin?: boolean
  replyingTo: number | null
  isLoggedIn?: boolean
  isReply?: boolean
}>()

const emit = defineEmits<{
  (e: 'reply', commentId: number): void
  (e: 'delete', commentId: number): void
  (e: 'submit-reply', parentId: number, content: string): void
  (e: 'cancel-reply'): void
}>()

const replyContent = ref('')

const canDelete = computed(() =>
  props.isAdmin || (props.userId && props.comment.user_id === props.userId)
)

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function handleSubmitReply() {
  if (!replyContent.value.trim()) return
  emit('submit-reply', props.comment.id, replyContent.value.trim())
  replyContent.value = ''
}
</script>

<style scoped>
.comment-item {
  display: flex;
  flex-direction: column;
}

.comment-item__main {
  padding: var(--space-md);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--glass-surface-bg);
  backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
  -webkit-backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
}

.comment-item__header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.comment-item__author {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-accent);
}

.comment-item__date {
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

.comment-item__content {
  font-size: 0.88rem;
  color: var(--color-text-soft);
  line-height: 1.75;
  margin: 0;
}

.comment-item__actions {
  display: flex;
  gap: var(--space-sm);
  margin-top: var(--space-sm);
}

.comment-item__action {
  font-size: 0.75rem;
  padding: 3px 10px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background: none;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.comment-item__action--reply {
  color: var(--color-text-muted);
}

.comment-item__action--reply:hover {
  color: var(--color-accent);
  border-color: var(--accent-tint-30);
}

.comment-item__action--delete {
  color: var(--color-text-muted);
}

.comment-item__action--delete:hover {
  color: var(--error-main);
  border-color: var(--error-border-30);
}

/* Reply form */
.comment-item__reply-form {
  margin-top: var(--space-sm);
  margin-left: var(--space-lg);
  padding: var(--space-sm);
  border: 1px solid var(--accent-tint-20);
  border-radius: var(--radius-sm);
  background: var(--accent-tint-04);
}

.comment-item__reply-textarea {
  width: 100%;
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg-deep);
  color: var(--color-text);
  font-size: 0.82rem;
  line-height: 1.6;
  resize: vertical;
}

.comment-item__reply-textarea::placeholder {
  color: var(--color-text-muted);
  opacity: 0.5;
}

.comment-item__reply-textarea:focus {
  outline: none;
  border-color: var(--color-accent);
}

.comment-item__reply-actions {
  display: flex;
  gap: var(--space-sm);
  margin-top: var(--space-sm);
}

.comment-item__reply-submit {
  padding: 5px 14px;
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm);
  color: var(--color-accent);
  font-size: 0.78rem;
  font-weight: 500;
  background: var(--accent-tint-10);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.comment-item__reply-submit:hover:not(:disabled) {
  background: var(--accent-tint-20);
}

.comment-item__reply-submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.comment-item__reply-cancel {
  padding: 5px 14px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  font-size: 0.78rem;
  background: none;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.comment-item__reply-cancel:hover {
  color: var(--color-text);
  border-color: var(--border-heavy);
}

/* Nested replies */
.comment-item__replies {
  margin-top: var(--space-sm);
  margin-left: var(--space-lg);
  padding-left: var(--space-md);
  border-left: 2px solid var(--accent-tint-15);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

@media (max-width: 640px) {
  .comment-item__replies {
    margin-left: var(--space-sm);
    padding-left: var(--space-sm);
  }

  .comment-item__reply-form {
    margin-left: var(--space-sm);
  }
}
</style>
