<template>
  <section class="admin-page">
    <div class="container">
      <header class="admin-page__header">
        <div class="admin-page__header-left">
          <button class="admin-page__back" @click="$router.push('/')">&larr; 返回首页</button>
          <h1 class="admin-page__title">后台管理</h1>
        </div>
        <button class="admin-page__create-btn" @click="$router.push('/create-post')">
          + 写文章
        </button>
      </header>

      <div class="admin-page__tabs">
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'posts' }"
          @click="activeTab = 'posts'; onTabChange('posts')"
        >文章管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'categories' }"
          @click="activeTab = 'categories'; onTabChange('categories')"
        >分类管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'tags' }"
          @click="activeTab = 'tags'; onTabChange('tags')"
        >标签管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'stats' }"
          @click="activeTab = 'stats'; onTabChange('stats')"
        >站点统计</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'friend-links' }"
          @click="activeTab = 'friend-links'; onTabChange('friend-links')"
        >友链管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'users' }"
          @click="activeTab = 'users'; onTabChange('users')"
        >用户管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'comments' }"
          @click="activeTab = 'comments'; onTabChange('comments')"
        >评论审核</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'messages' }"
          @click="activeTab = 'messages'; onTabChange('messages')"
        >留言管理</button>
        <button
          class="admin-page__tab"
          :class="{ active: activeTab === 'media' }"
          @click="activeTab = 'media'; onTabChange('media')"
        >媒体库</button>
      </div>

      <AdminPostsTab v-if="activeTab === 'posts'" :key="'posts-' + refreshKey" @delete="openDeleteModal" />
      <AdminCategoriesTab v-if="activeTab === 'categories'" :key="'categories-' + refreshKey" @delete="openDeleteModal" />
      <AdminTagsTab v-if="activeTab === 'tags'" :key="'tags-' + refreshKey" @delete="openDeleteModal" />
      <AdminStatsTab v-if="activeTab === 'stats'" :key="'stats-' + refreshKey" />
      <AdminFriendLinksTab v-if="activeTab === 'friend-links'" :key="'friend-links-' + refreshKey" @delete="openDeleteModal" />
      <AdminUsersTab v-if="activeTab === 'users'" :key="'users-' + refreshKey" @delete="openDeleteModal" />
      <AdminCommentsTab v-if="activeTab === 'comments'" :key="'comments-' + refreshKey" />
      <AdminMessagesTab v-if="activeTab === 'messages'" :key="'messages-' + refreshKey" />
      <AdminMediaTab v-if="activeTab === 'media'" :key="'media-' + refreshKey" />

      <Teleport to="body">
        <Transition name="modal">
          <div v-if="deleteModal.show" class="modal-overlay" @click.self="closeDeleteModal">
            <div class="modal">
              <h3 class="modal__title">确认删除</h3>
              <p class="modal__text">
                确定要删除{{ deleteModal.type === 'post' ? '文章' : deleteModal.type === 'category' ? '分类' : deleteModal.type === 'tag' ? '标签' : deleteModal.type === 'user' ? '用户' : '友链' }}
                <strong>「{{ deleteModal.name }}」</strong>吗？此操作不可撤销。
              </p>
              <div class="modal__actions">
                <button class="modal__btn modal__btn--cancel" @click="closeDeleteModal">取消</button>
                <button class="modal__btn modal__btn--confirm" @click="confirmDelete">删除</button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { deletePost, deleteCategory, deleteTag, deleteFriendLink, deleteUser } from '@/api/admin'
import { useToastStore } from '@/stores/toast'
import AdminPostsTab from '@/components/admin/AdminPostsTab.vue'
import AdminCategoriesTab from '@/components/admin/AdminCategoriesTab.vue'
import AdminTagsTab from '@/components/admin/AdminTagsTab.vue'
import AdminStatsTab from '@/components/admin/AdminStatsTab.vue'
import AdminFriendLinksTab from '@/components/admin/AdminFriendLinksTab.vue'
import AdminUsersTab from '@/components/admin/AdminUsersTab.vue'
import AdminCommentsTab from '@/components/admin/AdminCommentsTab.vue'
import AdminMessagesTab from '@/components/admin/AdminMessagesTab.vue'
import AdminMediaTab from '@/components/admin/AdminMediaTab.vue'

const toast = useToastStore()

const activeTab = ref<'posts' | 'categories' | 'tags' | 'stats' | 'friend-links' | 'users' | 'comments' | 'messages' | 'media'>('posts')

const loadedTabs = new Set<string>(['posts'])

function onTabChange(tab: string) {
  if (loadedTabs.has(tab)) return
  loadedTabs.add(tab)
}

const refreshKey = ref(0)
type DeleteType = 'post' | 'category' | 'tag' | 'friend-link' | 'user'

const deleteModal = reactive({
  show: false,
  type: '' as DeleteType | '',
  id: 0,
  name: '',
})

function isDeleteType(type: string): type is DeleteType {
  return ['post', 'category', 'tag', 'friend-link', 'user'].includes(type)
}

function openDeleteModal(type: string, id: number, name: string) {
  if (!isDeleteType(type)) return
  deleteModal.show = true
  deleteModal.type = type
  deleteModal.id = id
  deleteModal.name = name
}

function closeDeleteModal() {
  deleteModal.show = false
}

async function confirmDelete() {
  const { type, id } = deleteModal
  closeDeleteModal()
  try {
    if (type === 'post') {
      await deletePost(id)
    } else if (type === 'category') {
      await deleteCategory(id)
    } else if (type === 'tag') {
      await deleteTag(id)
    } else if (type === 'friend-link') {
      await deleteFriendLink(id)
    } else if (type === 'user') {
      await deleteUser(id)
    }
    refreshKey.value++
    toast.success('删除成功')
  } catch {
    toast.error('删除失败，请稍后重试')
  }
}
</script>

<style scoped>
.admin-page {
  padding: var(--space-3xl) 0;
  min-height: 60vh;
}

.admin-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
}

.admin-page__header-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.admin-page__back {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-muted);
  background: none;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 6px 14px;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.admin-page__back:hover {
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.admin-page__title {
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.admin-page__create-btn {
  font-size: 0.88rem;
  font-weight: 500;
  padding: 10px 22px;
  border: 1px solid var(--accent-tint-40);
  border-radius: var(--radius-sm);
  color: var(--color-accent);
  background: var(--accent-tint-10);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.admin-page__create-btn:hover {
  background: var(--accent-tint-20);
  border-color: var(--color-accent);
}

.admin-page__create-btn--sm {
  padding: 8px 16px;
  font-size: 0.82rem;
}

.admin-page__tabs {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-xl);
  padding: var(--space-sm);
  background: var(--glass-surface-bg);
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  backdrop-filter: var(--glass-card-blur);
}

.admin-page__tab {
  font-size: 0.9rem;
  font-weight: 500;
  padding: 8px 18px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  background: var(--glass-bg-02);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.admin-page__tab:hover {
  border-color: var(--border-strong);
  color: var(--color-text);
}

.admin-page__tab.active {
  border-color: var(--accent-tint-40);
  background: var(--accent-tint-15);
  color: var(--color-accent);
}

.admin-page__panel {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.admin-page__loading {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-text-muted);
}

.admin-page__error {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-text-muted);
}

.admin-page__retry {
  margin-top: var(--space-md);
  padding: 8px 20px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  background: var(--glass-bg-02);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.admin-page__retry:hover {
  border-color: var(--accent-tint-40);
  color: var(--color-accent);
}

.admin-page__inline-form {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.admin-input {
  padding: 8px 14px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  background: var(--glass-bg-12);
  color: var(--color-text);
  font-size: 0.88rem;
  outline: none;
  transition: border-color var(--duration-fast) ease;
}

.admin-input::placeholder {
  color: var(--color-text-muted);
}

.admin-input:focus {
  border-color: var(--accent-tint-50);
}

.admin-input--inline {
  width: 100%;
  min-width: 60px;
  padding: 4px 8px;
  font-size: 0.82rem;
}

.admin-input--textarea {
  width: 100%;
  resize: vertical;
  min-height: 60px;
  font-family: inherit;
}

.admin-table-wrap {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--glass-surface-bg);
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  backdrop-filter: var(--glass-card-blur);
}

.admin-table th,
.admin-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 0.88rem;
}

.admin-table th {
  font-weight: 600;
  color: var(--color-text-muted);
  background: var(--glass-bg-03);
  white-space: nowrap;
}

.admin-table td {
  color: var(--color-text-soft);
}

.admin-table tr:last-child td {
  border-bottom: none;
}

.admin-table__title {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-text);
  font-weight: 500;
}

.admin-table__date {
  white-space: nowrap;
}

.admin-table__actions {
  white-space: nowrap;
}

.admin-table__empty {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--space-xl);
}

.admin-table__reply-row {
  padding: var(--space-md);
  background: var(--glass-bg-05);
}

.admin-page__reply-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.admin-page__reply-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-heading);
}

.admin-page__reply-actions {
  display: flex;
  gap: var(--space-sm);
}

.admin-toggle {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.admin-toggle input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.admin-toggle__track {
  position: relative;
  width: 38px;
  height: 20px;
  background: var(--border-strong);
  border: 1px solid var(--border-default);
  border-radius: 10px;
  transition: all var(--duration-fast) ease;
}

.admin-toggle__thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 14px;
  height: 14px;
  background: var(--color-text-muted);
  border-radius: 50%;
  transition: all var(--duration-fast) ease;
}

.admin-toggle input:checked + .admin-toggle__track {
  background: var(--accent-tint-25);
  border-color: var(--accent-tint-50);
}

.admin-toggle input:checked + .admin-toggle__track .admin-toggle__thumb {
  left: 20px;
  background: var(--color-accent);
}

.admin-toggle:hover .admin-toggle__track {
  border-color: var(--border-heavy-2);
}

.admin-btn {
  font-size: 0.78rem;
  font-weight: 500;
  padding: 5px 12px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  margin-right: 6px;
}

.admin-page__badge {
  font-size: 0.72rem;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.admin-page__badge--approved {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.admin-page__badge--pending {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.admin-page__badge--draft {
  background: rgba(139, 92, 246, 0.12);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.admin-btn--edit {
  color: var(--color-accent);
  background: var(--accent-tint-06);
  border-color: var(--accent-tint-30);
}

.admin-btn--edit:hover {
  background: var(--accent-tint-15);
}

.admin-btn--delete {
  color: var(--color-text-muted);
  background: var(--glass-bg-02);
}

.admin-btn--delete:hover {
  color: #f87171;
  border-color: var(--error-border-30);
}

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
  max-width: 420px;
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

.modal__text {
  margin: 0 0 var(--space-lg);
  font-size: 0.9rem;
  color: var(--color-text-soft);
  line-height: 1.6;
}

.modal__text strong {
  color: #f87171;
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
  border: 1px solid var(--error-border-40);
  background: var(--error-bg-12);
  color: #f87171;
}

.modal__btn--confirm:hover {
  background: var(--error-bg-25);
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

@media (max-width: 768px) {
  .admin-page__header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-md);
  }

  .admin-page__inline-form {
    flex-wrap: wrap;
  }

  .admin-input {
    flex: 1;
    min-width: 120px;
  }

  .admin-table th,
  .admin-table td {
    padding: 10px 10px;
    font-size: 0.82rem;
  }
}
</style>
