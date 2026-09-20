<template>
  <div class="admin-page__panel">
    <div v-if="!usersLoaded" class="admin-page__loading">加载中...</div>
    <div v-else class="admin-table-wrap">
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>头像</th>
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
              <img
                v-if="user.avatar"
                :src="user.avatar"
                :alt="user.username"
                class="user-avatar"
              />
              <div v-else class="user-avatar user-avatar--placeholder">
                {{ user.username.charAt(0).toUpperCase() }}
              </div>
            </td>
            <td>
              <select
                v-if="user.role !== 'super_admin'"
                class="admin-input"
                :value="user.role"
                @change="handleUpdateUserRole(user, ($event.target as HTMLSelectElement).value)"
              >
                <option value="user">user</option>
              </select>
              <span v-else class="admin-table__locked-role" title="超级管理员角色锁死，不可修改">
                🔒 super_admin
              </span>
            </td>
            <td class="admin-table__date">{{ formatDate(user.created_at) }}</td>
            <td class="admin-table__actions">
              <button
                class="admin-btn admin-btn--edit"
                @click="openEditModal(user)"
              >编辑</button>
              <button
                class="admin-btn admin-btn--reset"
                @click="openResetModal(user)"
              >重置密码</button>
              <button
                class="admin-btn admin-btn--delete"
                :disabled="user.id === currentAdminId"
                :title="user.id === currentAdminId ? '不能删除自己' : ''"
                @click="emit('delete', 'user', user.id, user.username)"
              >删除</button>
            </td>
          </tr>
          <tr v-if="!users.length">
            <td colspan="6" class="admin-table__empty">暂无用户</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 编辑用户资料 Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="editModal.show" class="modal-overlay" @click.self="closeEditModal">
          <div class="modal">
            <h3 class="modal__title">编辑用户「{{ editModal.username }}」</h3>
            <div class="modal__body">
              <div class="modal__field">
                <label class="modal__label">头像链接</label>
                <input
                  v-model="editModal.avatar"
                  type="url"
                  class="modal__input"
                  placeholder="https://..."
                />
              </div>
              <div class="modal__field">
                <label class="modal__label">个性签名</label>
                <textarea
                  v-model="editModal.bio"
                  class="modal__input modal__textarea"
                  placeholder="一句话介绍"
                ></textarea>
              </div>
            </div>
            <div class="modal__actions">
              <button class="modal__btn modal__btn--cancel" @click="closeEditModal">取消</button>
              <button class="modal__btn modal__btn--confirm" :disabled="editModal.saving" @click="confirmEdit">
                {{ editModal.saving ? '保存中...' : '保存' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 重置密码 Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="resetModal.show" class="modal-overlay" @click.self="closeResetModal">
          <div class="modal">
            <h3 class="modal__title">重置「{{ resetModal.username }}」的密码</h3>
            <div class="modal__body">
              <p class="modal__hint">管理员重置不需要旧密码。新密码需至少 8 位，含大小写字母和数字。</p>
              <div class="modal__field">
                <label class="modal__label">新密码</label>
                <input
                  v-model="resetModal.newPassword"
                  type="password"
                  class="modal__input"
                  placeholder="至少 8 位"
                  autocomplete="new-password"
                />
              </div>
              <div class="modal__field">
                <label class="modal__label">确认新密码</label>
                <input
                  v-model="resetModal.confirmPassword"
                  type="password"
                  class="modal__input"
                  placeholder="再次输入"
                  autocomplete="new-password"
                />
              </div>
              <p v-if="resetModal.error" class="modal__error">{{ resetModal.error }}</p>
            </div>
            <div class="modal__actions">
              <button class="modal__btn modal__btn--cancel" @click="closeResetModal">取消</button>
              <button class="modal__btn modal__btn--confirm" :disabled="resetModal.saving" @click="confirmReset">
                {{ resetModal.saving ? '重置中...' : '确认重置' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { getUsers, updateUser } from '@/api/admin'
import { safeCall } from '@/api/http'
import { useToastStore } from '@/stores/toast'
import { useAuthStore } from '@/stores/auth'
import type { User } from '@/types/blog'

const toast = useToastStore()
const authStore = useAuthStore()
const currentAdminId = computed(() => (authStore.user as any)?.id)

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

// ── Edit profile modal ──
const editModal = reactive({
  show: false,
  id: 0,
  username: '',
  avatar: '',
  bio: '',
  saving: false,
})

function openEditModal(user: User) {
  editModal.show = true
  editModal.id = user.id
  editModal.username = user.username
  editModal.avatar = user.avatar ?? ''
  editModal.bio = user.bio ?? ''
  editModal.saving = false
}

function closeEditModal() {
  editModal.show = false
}

async function confirmEdit() {
  editModal.saving = true
  try {
    const updated = await updateUser(editModal.id, {
      avatar: editModal.avatar || undefined,
      bio: editModal.bio || undefined,
    })
    const idx = users.value.findIndex(u => u.id === editModal.id)
    if (idx >= 0) users.value[idx] = updated
    toast.success('用户资料已更新')
    closeEditModal()
  } catch {
    toast.error('更新失败，请稍后重试')
  } finally {
    editModal.saving = false
  }
}

// ── Reset password modal ──
const resetModal = reactive({
  show: false,
  id: 0,
  username: '',
  newPassword: '',
  confirmPassword: '',
  error: '',
  saving: false,
})

function openResetModal(user: User) {
  resetModal.show = true
  resetModal.id = user.id
  resetModal.username = user.username
  resetModal.newPassword = ''
  resetModal.confirmPassword = ''
  resetModal.error = ''
  resetModal.saving = false
}

function closeResetModal() {
  resetModal.show = false
}

async function confirmReset() {
  resetModal.error = ''
  if (resetModal.newPassword !== resetModal.confirmPassword) {
    resetModal.error = '两次输入的密码不一致'
    return
  }
  if (resetModal.newPassword.length < 8) {
    resetModal.error = '密码至少 8 位'
    return
  }
  resetModal.saving = true
  try {
    await updateUser(resetModal.id, { new_password: resetModal.newPassword })
    toast.success(`已重置「${resetModal.username}」的密码`)
    closeResetModal()
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    if (Array.isArray(detail)) {
      resetModal.error = detail.map((d: any) => d.msg || String(d)).join('；')
    } else {
      resetModal.error = typeof detail === 'string' ? detail : '重置失败，请稍后重试'
    }
  } finally {
    resetModal.saving = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

loadUsers()
</script>

<style scoped>
.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--color-border);
}

.admin-table__locked-role {
  font-weight: 600;
  color: var(--color-accent);
  cursor: default;
}

.user-avatar--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  font-weight: 600;
  background: var(--accent-tint-10);
  color: var(--color-accent);
}

.admin-btn--reset {
  color: var(--color-text-soft);
  background: var(--glass-bg-02);
  border-color: var(--border-strong);
}

.admin-btn--reset:hover:not(:disabled) {
  color: var(--color-accent);
  border-color: var(--color-accent);
  background: var(--accent-tint-06);
}

/* Modal styles — these match AdminView.vue's modal styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(20px);
}

.modal {
  width: 90%;
  max-width: 460px;
  padding: var(--space-xl);
  background: var(--modal-bg);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(20px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.modal__title {
  margin: 0 0 var(--space-md);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-heading);
}

.modal__body {
  display: grid;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.modal__field {
  display: grid;
  gap: 6px;
}

.modal__label {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.modal__input {
  padding: 9px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.88rem;
  font-family: inherit;
  outline: none;
  transition: border-color var(--duration-fast) ease;
}

.modal__input:focus {
  border-color: var(--color-accent);
}

.modal__textarea {
  resize: vertical;
  min-height: 60px;
}

.modal__hint {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  background: var(--accent-tint-06);
  border: 1px solid var(--accent-tint-20);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  margin: 0;
}

.modal__error {
  font-size: 0.82rem;
  color: #f87171;
  background: rgba(248, 113, 113, 0.08);
  border: 1px solid rgba(248, 113, 113, 0.2);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  margin: 0;
}

.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
}

.modal__btn {
  padding: 8px 20px;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.modal__btn--cancel {
  border: 1px solid var(--border-strong);
  background: var(--glass-bg-12);
  color: var(--color-text-soft);
}

.modal__btn--cancel:hover {
  border-color: var(--border-strong);
  color: var(--color-text);
}

.modal__btn--confirm {
  border: 1px solid var(--color-accent);
  background: var(--color-accent);
  color: var(--color-bg);
}

.modal__btn--confirm:hover:not(:disabled) {
  opacity: 0.9;
}

.modal__btn--confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

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
  transform: scale(0.95) translateY(8px);
}
</style>
