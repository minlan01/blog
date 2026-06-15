<template>
  <section class="comments" v-if="postId">
    <h3 class="comments__title">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      评论 ({{ totalCount }})
    </h3>

    <!-- Comment list (nested) -->
    <div class="comments__list" v-if="comments.length">
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        :user-id="userId"
        :is-admin="isAdmin"
        :is-logged-in="isLoggedIn"
        :replying-to="replyingTo"
        @reply="startReply"
        @delete="handleDelete"
        @submit-reply="submitReply"
        @cancel-reply="cancelReply"
      />
    </div>
    <p v-else-if="loadError" class="comments__error">{{ loadError }}</p>
    <p v-else class="comments__empty">暂无评论，来发表第一条吧。</p>

    <!-- Action error (submit/reply/delete) -->
    <div v-if="actionError" class="comments__action-error">{{ actionError }}</div>

    <!-- Main comment form -->
    <form class="comments__form" @submit.prevent="submitComment" v-if="isLoggedIn">
      <textarea
        v-model="newComment"
        class="comments__textarea"
        placeholder="写下你的评论..."
        rows="3"
        required
      ></textarea>
      <button type="submit" class="comments__submit" :disabled="submitting">
        {{ submitting ? '发表中...' : '发表评论' }}
      </button>
    </form>
    <div v-else class="comments__login-prompt">
      <p class="comments__login-text">需要注册/登录后才能发表评论</p>
      <div class="comments__login-actions">
        <button class="comments__login-btn" @click="showLoginModal = true">登录 / 注册</button>
      </div>
    </div>

    <!-- Login prompt modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showLoginModal" class="modal-overlay" @click.self="showLoginModal = false">
          <div class="modal">
            <h3 class="modal__title">需要登录</h3>
            <p class="modal__text">发表评论前请先登录或注册账号。</p>
            <div class="modal__actions">
              <RouterLink to="/login" class="modal__btn modal__btn--confirm" @click="showLoginModal = false">去登录</RouterLink>
              <RouterLink to="/register" class="modal__btn modal__btn--register" @click="showLoginModal = false">去注册</RouterLink>
              <button class="modal__btn modal__btn--cancel" @click="showLoginModal = false">取消</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getComments, createComment, deleteComment } from '@/api/comments'
import { useAuthStore } from '@/stores/auth'
import type { CommentRead } from '@/types/blog'
import CommentItem from './CommentItem.vue'

const props = defineProps<{
  postId: number
  isLoggedIn?: boolean
  userId?: number
}>()

const emit = defineEmits<{
  (e: 'comment-added'): void
}>()

const authStore = useAuthStore()
const comments = ref<CommentRead[]>([])
const newComment = ref('')
const submitting = ref(false)
const replyingTo = ref<number | null>(null)
const showLoginModal = ref(false)
const loadError = ref('')
const actionError = ref('')

const isAdmin = computed(() => authStore.isAdmin)

const totalCount = computed(() => {
  function countAll(list: CommentRead[]): number {
    return list.reduce((sum, c) => sum + 1 + countAll(c.replies || []), 0)
  }
  return countAll(comments.value)
})

async function loadComments() {
  try {
    comments.value = await getComments(props.postId)
  } catch {
    loadError.value = '评论加载失败，请刷新页面重试'
  }
}

async function submitComment() {
  if (!newComment.value.trim()) return
  submitting.value = true
  actionError.value = ''
  try {
    const comment = await createComment({
      content: newComment.value,
      post_id: props.postId,
    })
    comments.value.push(comment)
    newComment.value = ''
    emit('comment-added')
  } catch {
    actionError.value = '评论发表失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

function startReply(commentId: number) {
  if (!props.isLoggedIn) {
    showLoginModal.value = true
    return
  }
  replyingTo.value = commentId
}

function cancelReply() {
  replyingTo.value = null
}

async function submitReply(parentId: number, content: string) {
  actionError.value = ''
  try {
    const reply = await createComment({
      content,
      post_id: props.postId,
      parent_id: parentId,
    })
    insertReply(comments.value, parentId, reply)
    replyingTo.value = null
    emit('comment-added')
  } catch {
    actionError.value = '回复发表失败，请稍后重试'
  }
}

function insertReply(list: CommentRead[], parentId: number, reply: CommentRead): boolean {
  for (const c of list) {
    if (c.id === parentId) {
      if (!c.replies) c.replies = []
      c.replies.push(reply)
      return true
    }
    if (c.replies && insertReply(c.replies, parentId, reply)) return true
  }
  return false
}

async function handleDelete(commentId: number) {
  actionError.value = ''
  try {
    await deleteComment(commentId)
    removeComment(comments.value, commentId)
  } catch {
    actionError.value = '删除评论失败，请稍后重试'
  }
}

function removeComment(list: CommentRead[], id: number): boolean {
  const idx = list.findIndex(c => c.id === id)
  if (idx !== -1) {
    list.splice(idx, 1)
    return true
  }
  for (const c of list) {
    if (c.replies && removeComment(c.replies, id)) return true
  }
  return false
}

onMounted(loadComments)
</script>

<style scoped>
.comments {
  margin-top: var(--space-2xl);
  padding-top: var(--space-xl);
  border-top: 1px solid var(--color-border);
}

.comments__title {
  font-size: 1rem;
  margin: 0 0 var(--space-lg);
  font-weight: 600;
  color: var(--color-text-heading);
  display: flex;
  align-items: center;
  gap: 8px;
}

.comments__title svg {
  color: var(--color-accent);
  opacity: 0.6;
}

.comments__list {
  display: grid;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.comments__empty {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin: 0 0 var(--space-lg);
}

.comments__loading {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.comments__skeleton {
  height: 64px;
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
}

.comments__error {
  color: #ef4444;
  font-size: 0.85rem;
  margin: 0 0 var(--space-lg);
  text-align: center;
  padding: var(--space-md);
}

.comments__action-error {
  color: #ef4444;
  font-size: 0.82rem;
  padding: var(--space-sm) var(--space-md);
  margin-bottom: var(--space-md);
  border: 1px solid var(--error-border-30);
  border-radius: var(--radius-sm);
  background: var(--error-bg-06);
}

.comments__form {
  display: grid;
  gap: var(--space-md);
}

.comments__textarea {
  width: 100%;
  padding: var(--space-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg-deep);
  color: var(--color-text);
  font-size: 0.85rem;
  line-height: 1.7;
  resize: vertical;
  transition: all var(--duration-fast) ease;
}

.comments__textarea::placeholder {
  color: var(--color-text-muted);
  opacity: 0.5;
}

.comments__textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 8px var(--accent-tint-08);
}

.comments__submit {
  justify-self: start;
  padding: 8px 20px;
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm);
  color: var(--color-accent);
  font-weight: 500;
  font-size: 0.82rem;
  background: transparent;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.comments__submit:hover:not(:disabled) {
  background: var(--accent-tint-10);
  box-shadow: 0 0 8px var(--accent-tint-15);
}

.comments__submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.comments__login-prompt {
  text-align: center;
  padding: var(--space-xl);
  border: 1px dashed var(--glass-border);
  border-radius: var(--radius-md);
  background: var(--glass-bg-03);
}

.comments__login-text {
  font-size: 0.88rem;
  color: var(--color-text-muted);
  margin: 0 0 var(--space-md);
}

.comments__login-btn {
  padding: 8px 24px;
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm);
  background: var(--accent-tint-10);
  color: var(--color-accent);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.comments__login-btn:hover {
  background: var(--accent-tint-20);
}

/* Modal styles (reusing global modal) */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 150;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(6px);
}

.modal {
  background: var(--modal-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  max-width: 400px;
  width: calc(100% - 48px);
  backdrop-filter: var(--glass-panel-blur);
}

.modal__title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin: 0 0 var(--space-md);
}

.modal__text {
  font-size: 0.9rem;
  color: var(--color-text-soft);
  margin: 0 0 var(--space-lg);
  line-height: 1.6;
}

.modal__actions {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.modal__btn {
  padding: 8px 18px;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: all var(--duration-fast) ease;
  text-align: center;
}

.modal__btn--confirm {
  border: 1px solid var(--color-accent);
  background: var(--accent-tint-10);
  color: var(--color-accent);
}

.modal__btn--confirm:hover {
  background: var(--accent-tint-20);
}

.modal__btn--register {
  border: 1px solid var(--glass-border);
  background: var(--glass-bg-06);
  color: var(--color-text-soft);
}

.modal__btn--register:hover {
  border-color: var(--border-strong);
  color: var(--color-text);
}

.modal__btn--cancel {
  border: 1px solid var(--glass-border);
  background: none;
  color: var(--color-text-muted);
}

.modal__btn--cancel:hover {
  color: var(--color-text);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
