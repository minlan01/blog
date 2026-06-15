<template>
  <div class="admin-page__panel">
    <div v-if="!usersLoaded" class="admin-page__loading">加载中...</div>
    <div v-else class="admin-table-wrap">
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>角色</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td class="admin-table__title">{{ user.username }}</td>
            <td>
              <select
                class="admin-input"
                :value="user.role"
                @change="handleUpdateUserRole(user, ($event.target as HTMLSelectElement).value)"
              >
                <option value="user">user</option>
                <option value="super_admin">super_admin</option>
              </select>
            </td>
            <td class="admin-table__date">{{ formatDate(user.created_at) }}</td>
            <td class="admin-table__actions">
              <button class="admin-btn admin-btn--delete" @click="emit('delete', 'user', user.id, user.username)">删除</button>
            </td>
          </tr>
          <tr v-if="!users.length">
            <td colspan="5" class="admin-table__empty">暂无用户</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getUsers, updateUser } from '@/api/admin'
import { safeCall } from '@/api/http'
import { useToastStore } from '@/stores/toast'
import type { User } from '@/types/blog'

const toast = useToastStore()

const emit = defineEmits<{
  delete: [type: string, id: number, name: string]
}>()

const users = ref<User[]>([])
const usersLoaded = ref(false)

async function loadUsers() {
  usersLoaded.value = false
  users.value = await safeCall(() => getUsers(), [])
  usersLoaded.value = true
}

async function handleUpdateUserRole(user: User, newRole: string) {
  try {
    await updateUser(user.id, { role: newRole })
    user.role = newRole
  } catch {
    toast.error('更新用户角色失败，请稍后重试')
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

loadUsers()
</script>
