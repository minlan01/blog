<template>
  <div class="admin-page__panel">
    <div v-if="!adminMessagesLoaded" class="admin-page__loading">加载中...</div>
    <div v-else class="admin-table-wrap">
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>昵称</th>
            <th>内容</th>
            <th>回复状态</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="msg in adminMessages" :key="msg.id">
            <td>{{ msg.id }}</td>
            <td>{{ msg.name }}</td>
            <td class="admin-table__title">{{ msg.content }}</td>
            <td>
              <span class="admin-page__badge" :class="msg.admin_reply ? 'admin-page__badge--approved' : 'admin-page__badge--pending'">
                {{ msg.admin_reply ? '已回复' : '未回复' }}
              </span>
            </td>
            <td class="admin-table__date">{{ formatDate(msg.created_at) }}</td>
            <td class="admin-table__actions">
              <button
                class="admin-btn admin-btn--edit"
                @click="startReplyMessage(msg)"
              >{{ msg.admin_reply ? '修改回复' : '回复' }}</button>
              <button class="admin-btn admin-btn--delete" @click="handleAdminDeleteMessage(msg.id)">删除</button>
            </td>
          </tr>
          <tr v-if="replyingMessage">
            <td colspan="6" class="admin-table__reply-row">
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
          <tr v-if="!adminMessages.length">
            <td colspan="6" class="admin-table__empty">暂无留言</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getAdminMessages, replyMessage, adminDeleteMessage, type AdminMessageRead } from '@/api/admin'
import { safeCall } from '@/api/http'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()

const adminMessages = ref<AdminMessageRead[]>([])
const adminMessagesLoaded = ref(false)
const replyingMessage = ref<AdminMessageRead | null>(null)
const replyContent = ref('')

async function loadAdminMessages() {
  adminMessagesLoaded.value = false
  adminMessages.value = await safeCall(() => getAdminMessages(), [])
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
  } catch {
    toast.error('回复留言失败，请稍后重试')
  }
}

async function handleAdminDeleteMessage(id: number) {
  try {
    await adminDeleteMessage(id)
    adminMessages.value = adminMessages.value.filter(m => m.id !== id)
  } catch {
    toast.error('删除留言失败，请稍后重试')
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

loadAdminMessages()
</script>
