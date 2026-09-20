<template>
  <div class="admin-page__panel">
    <!-- 筛选栏 -->
    <div class="msg-filter-bar">
      <button
        v-for="f in filters"
        :key="f.value"
        class="msg-filter-btn"
        :class="{ active: currentFilter === f.value }"
        @click="currentFilter = f.value"
      >{{ f.label }} ({{ countByStatus(f.value) }})</button>
    </div>

    <div v-if="!adminMessagesLoaded" class="admin-page__loading">加载中...</div>
    <div v-else-if="filteredMessages.length === 0" class="admin-table__empty">暂无留言</div>
    <div v-else class="admin-table-wrap" style="overflow-x: auto; -webkit-overflow-scrolling: touch;">
      <table class="admin-table" style="min-width: 800px;">
        <thead>
          <tr>
            <th>ID</th>
            <th>昵称</th>
            <th>邮箱</th>
            <th>内容</th>
            <th>状态</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="msg in filteredMessages" :key="msg.id">
            <tr>
              <td>{{ msg.id }}</td>
              <td>{{ msg.name }}</td>
              <td class="admin-table__date">{{ msg.email || '-' }}</td>
              <td class="admin-table__title">{{ msg.content }}</td>
              <td>
                <span class="msg-status" :class="`msg-status--${msg.status || 'pending'}`">
                  {{ statusLabel(msg.status) }}
                </span>
              </td>
              <td class="admin-table__date">{{ formatDate(msg.created_at) }}</td>
              <td class="admin-table__actions">
                <button
                  v-if="msg.status !== 'approved'"
                  class="admin-btn admin-btn--approve"
                  @click="handleApprove(msg.id)"
                >通过</button>
                <button
                  v-if="msg.status !== 'rejected'"
                  class="admin-btn admin-btn--reject"
                  @click="handleReject(msg.id)"
                >拒绝</button>
                <button
                  class="admin-btn admin-btn--edit"
                  @click="startReplyMessage(msg)"
                >{{ msg.admin_reply ? '改回复' : '回复' }}</button>
                <button class="admin-btn admin-btn--delete" @click="handleAdminDeleteMessage(msg.id)">删除</button>
              </td>
            </tr>
            <tr v-if="replyingMessage?.id === msg.id">
              <td colspan="7" class="admin-table__reply-row">
                <div class="admin-page__reply-form">
                  <span class="admin-page__reply-label">回复 {{ replyingMessage.name }}：</span>
                  <textarea v-model="replyContent" class="admin-input admin-input--textarea" rows="3" placeholder="输入回复内容..."></textarea>
                  <div class="admin-page__reply-actions">
                    <button class="admin-btn admin-btn--edit" :disabled="!replyContent.trim()" @click="handleReplyMessage(replyingMessage.id)">提交回复</button>
                    <button class="admin-btn" @click="replyingMessage = null">取消</button>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { getAdminMessages, replyMessage, adminDeleteMessage, updateMessageStatus, type AdminMessageRead } from '@/api/admin'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()

const adminMessages = ref<AdminMessageRead[]>([])
const adminMessagesLoaded = ref(false)
const replyingMessage = ref<AdminMessageRead | null>(null)
const replyContent = ref('')
const currentFilter = ref<string>('all')

const filters = [
  { label: '全部', value: 'all' },
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
]

const filteredMessages = computed(() => {
  if (currentFilter.value === 'all') return adminMessages.value
  return adminMessages.value.filter(m => (m.status || 'pending') === currentFilter.value)
})

function countByStatus(status: string): number {
  if (status === 'all') return adminMessages.value.length
  return adminMessages.value.filter(m => (m.status || 'pending') === status).length
}

function statusLabel(status?: string): string {
  if (status === 'approved') return '已通过'
  if (status === 'rejected') return '已拒绝'
  return '待审核'
}

async function loadAdminMessages() {
  adminMessagesLoaded.value = false
  try {
    adminMessages.value = await getAdminMessages()
  } catch {
    toast.error('加载留言失败')
  }
  adminMessagesLoaded.value = true
}

function startReplyMessage(msg: AdminMessageRead) {
  replyingMessage.value = msg
  replyContent.value = msg.admin_reply || ''
}

async function handleReplyMessage(id: number) {
  if (!replyContent.value.trim()) return
  try {
    const updated = await replyMessage(id, replyContent.value.trim())
    const idx = adminMessages.value.findIndex(m => m.id === id)
    if (idx !== -1) adminMessages.value[idx] = updated
    replyingMessage.value = null
    replyContent.value = ''
    toast.success('回复成功')
  } catch {
    toast.error('回复失败')
  }
}

async function handleApprove(id: number) {
  try {
    const updated = await updateMessageStatus(id, 'approved')
    const idx = adminMessages.value.findIndex(m => m.id === id)
    if (idx !== -1) adminMessages.value[idx] = updated
    toast.success('已通过')
  } catch {
    toast.error('操作失败')
  }
}

async function handleReject(id: number) {
  try {
    const updated = await updateMessageStatus(id, 'rejected')
    const idx = adminMessages.value.findIndex(m => m.id === id)
    if (idx !== -1) adminMessages.value[idx] = updated
    toast.success('已拒绝')
  } catch {
    toast.error('操作失败')
  }
}

async function handleAdminDeleteMessage(id: number) {
  if (!confirm('确定删除这条留言？')) return
  try {
    await adminDeleteMessage(id)
    adminMessages.value = adminMessages.value.filter(m => m.id !== id)
    toast.success('已删除')
  } catch {
    toast.error('删除失败')
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

loadAdminMessages()
</script>

<style scoped>
.msg-filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: var(--space-md);
  flex-wrap: wrap;
}

.msg-filter-btn {
  padding: 6px 16px;
  background: transparent;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  color: var(--color-text-soft);
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.msg-filter-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-text);
}

.msg-filter-btn.active {
  background: var(--accent-tint-12);
  border-color: var(--accent-tint-25);
  color: var(--color-accent);
  font-weight: 500;
}

.msg-status {
  font-size: 0.75rem;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-weight: 500;
}

.msg-status--pending {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
}

.msg-status--approved {
  background: var(--success-bg-12);
  color: var(--success-main);
}

.msg-status--rejected {
  background: var(--error-bg-12);
  color: var(--error-main);
}

.admin-btn--approve {
  color: var(--success-main);
  border-color: var(--success-bg-12);
}

.admin-btn--approve:hover {
  background: rgba(16, 185, 129, 0.1);
}

.admin-btn--reject {
  color: #f59e0b;
  border-color: rgba(245, 158, 11, 0.3);
}

.admin-btn--reject:hover {
  background: rgba(245, 158, 11, 0.1);
}
</style>
