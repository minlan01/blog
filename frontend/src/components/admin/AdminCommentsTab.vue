<template>
  <div class="admin-page__panel">
    <div v-if="!adminCommentsLoaded" class="admin-page__loading">加载中...</div>
    <div v-else class="admin-table-wrap">
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>作者</th>
            <th>内容</th>
            <th>状态</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="comment in adminComments" :key="comment.id">
            <td>{{ comment.id }}</td>
            <td>{{ comment.author_name || '匿名' }}</td>
            <td class="admin-table__title">{{ comment.content }}</td>
            <td>
              <span class="admin-page__badge" :class="comment.is_approved ? 'admin-page__badge--approved' : 'admin-page__badge--pending'">
                {{ comment.is_approved ? '已审核' : '待审核' }}
              </span>
            </td>
            <td class="admin-table__date">{{ formatDate(comment.created_at) }}</td>
            <td class="admin-table__actions">
              <button
                v-if="!comment.is_approved"
                class="admin-btn admin-btn--edit"
                @click="handleApproveComment(comment.id)"
              >通过</button>
              <button class="admin-btn admin-btn--delete" @click="handleAdminDeleteComment(comment.id)">删除</button>
            </td>
          </tr>
          <tr v-if="!adminComments.length">
            <td colspan="6" class="admin-table__empty">暂无评论</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getAdminComments, approveComment, adminDeleteComment } from '@/api/admin'
import { safeCall } from '@/api/http'
import { useToastStore } from '@/stores/toast'
import type { CommentRead } from '@/types/blog'

const toast = useToastStore()

const adminComments = ref<CommentRead[]>([])
const adminCommentsLoaded = ref(false)

async function loadAdminComments() {
  adminCommentsLoaded.value = false
  adminComments.value = await safeCall(() => getAdminComments(), [])
  adminCommentsLoaded.value = true
}

async function handleApproveComment(id: number) {
  try {
    await approveComment(id)
    const c = adminComments.value.find(c => c.id === id)
    if (c) c.is_approved = true
  } catch {
    toast.error('审核操作失败，请稍后重试')
  }
}

async function handleAdminDeleteComment(id: number) {
  try {
    await adminDeleteComment(id)
    adminComments.value = adminComments.value.filter(c => c.id !== id)
  } catch {
    toast.error('删除评论失败，请稍后重试')
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

loadAdminComments()
</script>
