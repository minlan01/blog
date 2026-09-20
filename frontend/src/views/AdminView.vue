<template>
  <section class="admin-page">
    <div class="admin-layout">
      <!-- 顶部 header（全宽） -->
      <header class="admin-page__header">
        <div class="admin-page__header-left">
          <button class="admin-btn" @click="$router.push('/')">&larr; 返回首页</button>
          <h1 class="admin-page__title">后台管理</h1>
        </div>
        <button class="admin-btn admin-btn--primary" @click="$router.push('/create-post')">
          + 写文章
        </button>
      </header>

      <!-- 左侧导航 + 右侧内容 -->
      <div class="admin-body">
        <aside class="admin-sidebar">
          <div class="admin-sidebar__group">
            <div class="admin-sidebar__label">内容</div>
            <button class="admin-nav-item" :class="{ active: activeTab === 'posts' }" @click="activeTab = 'posts'; onTabChange('posts')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              文章管理
            </button>
            <button class="admin-nav-item" :class="{ active: activeTab === 'media' }" @click="activeTab = 'media'; onTabChange('media')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>
              媒体库
            </button>
            <button class="admin-nav-item" :class="{ active: activeTab === 'comments' }" @click="activeTab = 'comments'; onTabChange('comments')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              评论审核
            </button>
            <button class="admin-nav-item" :class="{ active: activeTab === 'messages' }" @click="activeTab = 'messages'; onTabChange('messages')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
              留言管理
            </button>
          </div>

          <div class="admin-sidebar__group">
            <div class="admin-sidebar__label">组织</div>
            <button class="admin-nav-item" :class="{ active: activeTab === 'categories' }" @click="activeTab = 'categories'; onTabChange('categories')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
              分类管理
            </button>
            <button class="admin-nav-item" :class="{ active: activeTab === 'tags' }" @click="activeTab = 'tags'; onTabChange('tags')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
              标签管理
            </button>
            <button class="admin-nav-item" :class="{ active: activeTab === 'friend-links' }" @click="activeTab = 'friend-links'; onTabChange('friend-links')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
              友链管理
            </button>
          </div>

          <div class="admin-sidebar__group">
            <div class="admin-sidebar__label">系统</div>
            <button class="admin-nav-item" :class="{ active: activeTab === 'stats' }" @click="activeTab = 'stats'; onTabChange('stats')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
              站点统计
            </button>
            <button class="admin-nav-item" :class="{ active: activeTab === 'site' }" @click="activeTab = 'site'; onTabChange('site')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              站点设置
            </button>
            <button class="admin-nav-item" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'; onTabChange('users')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
              用户管理
            </button>
            <button class="admin-nav-item" :class="{ active: activeTab === 'tokens' }" @click="activeTab = 'tokens'; onTabChange('tokens')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>
              API 令牌
            </button>
          </div>
        </aside>

        <main class="admin-content">
          <AdminPostsTab v-if="activeTab === 'posts'" :key="'posts-' + refreshKey" @delete="openDeleteModal" />
          <AdminCategoriesTab v-if="activeTab === 'categories'" :key="'categories-' + refreshKey" @delete="openDeleteModal" />
          <AdminTagsTab v-if="activeTab === 'tags'" :key="'tags-' + refreshKey" @delete="openDeleteModal" />
          <AdminStatsTab v-if="activeTab === 'stats'" :key="'stats-' + refreshKey" />
          <AdminSiteTab v-if="activeTab === 'site'" :key="'site-' + refreshKey" />
          <AdminFriendLinksTab v-if="activeTab === 'friend-links'" :key="'friend-links-' + refreshKey" @delete="openDeleteModal" />
          <AdminUsersTab v-if="activeTab === 'users'" :key="'users-' + refreshKey" @delete="openDeleteModal" />
          <AdminCommentsTab v-if="activeTab === 'comments'" :key="'comments-' + refreshKey" />
          <AdminMessagesTab v-if="activeTab === 'messages'" :key="'messages-' + refreshKey" />
          <AdminMediaTab v-if="activeTab === 'media'" :key="'media-' + refreshKey" />
          <AdminTokensTab v-if="activeTab === 'tokens'" :key="'tokens-' + refreshKey" />
        </main>
      </div>

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
import AdminSiteTab from '@/components/admin/AdminSiteTab.vue'
import AdminFriendLinksTab from '@/components/admin/AdminFriendLinksTab.vue'
import AdminUsersTab from '@/components/admin/AdminUsersTab.vue'
import AdminCommentsTab from '@/components/admin/AdminCommentsTab.vue'
import AdminMessagesTab from '@/components/admin/AdminMessagesTab.vue'
import AdminMediaTab from '@/components/admin/AdminMediaTab.vue'
import AdminTokensTab from '@/components/admin/AdminTokensTab.vue'

const toast = useToastStore()

const activeTab = ref<'posts' | 'categories' | 'tags' | 'stats' | 'site' | 'friend-links' | 'users' | 'comments' | 'messages' | 'media' | 'tokens'>('posts')

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
  padding: var(--space-xl) 0;
  min-height: 60vh;
}

.admin-layout {
  max-width: var(--container-max, 1200px);
  margin: 0 auto;
  padding: 0 var(--space-lg);
}

.admin-body {
  display: flex;
  gap: var(--space-lg);
  align-items: flex-start;
}

/* 左侧导航 */
.admin-sidebar {
  width: 200px;
  min-width: 200px;
  position: sticky;
  top: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  padding: var(--space-md);
  background: var(--glass-card-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  box-shadow: var(--shadow-card);
}

.admin-sidebar__group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.admin-sidebar__group + .admin-sidebar__group {
  border-top: 1px solid var(--glass-border);
  padding-top: var(--space-lg);
  margin-top: var(--space-sm);
}

.admin-sidebar__label {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
  padding: 6px 10px 8px;
}

.admin-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  font-weight: 500;
  padding: 10px 12px;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-soft);
  background: none;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  text-align: left;
  width: 100%;
}

.admin-nav-item:hover {
  background: var(--glass-bg-08);
  color: var(--color-text-heading);
}

.admin-nav-item.active {
  color: #fff;
  background: var(--color-accent-gradient);
  box-shadow: 0 2px 8px rgba(129, 140, 248, 0.25);
}

[data-theme="light"] .admin-nav-item.active {
  color: #fff;
}

/* 右侧内容 */
.admin-content {
  flex: 1;
  min-width: 0;
}

/* 移动端：侧边栏变横向滚动 */
@media (max-width: 768px) {
  .admin-body {
    flex-direction: column;
  }

  .admin-sidebar {
    width: 100%;
    min-width: 0;
    position: static;
    flex-direction: row;
    overflow-x: auto;
    gap: var(--space-sm);
    padding: var(--space-sm);
  }

  .admin-sidebar__group {
    flex-direction: row;
    gap: 4px;
    flex-shrink: 0;
  }

  .admin-sidebar__group + .admin-sidebar__group {
    border-top: none;
    border-left: 1px solid var(--glass-border);
    padding-top: 0;
    padding-left: var(--space-sm);
  }

  .admin-sidebar__label {
    display: none;
  }

  .admin-nav-item {
    width: auto;
    white-space: nowrap;
    padding: 6px 12px;
  }
}

.admin-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
  max-width: var(--container-max, 1200px);
  margin-left: auto;
  margin-right: auto;
  padding: 0 var(--space-lg);
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

/* Tab 样式已统一到 base.css .admin-tabs / .admin-tab */

/* Shared styles for admin tab child components. Scoped styles do not
   automatically reach inside child components, so these use :deep(). */
.admin-page :deep(.admin-page__panel) {
  animation: adminFadeIn 0.2s ease;
}

.admin-page :deep(.admin-page__toolbar) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.admin-page :deep(.admin-page__toolbar-left),
.admin-page :deep(.admin-page__batch-bar) {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.admin-page :deep(.admin-page__batch-bar) {
  padding: 6px 10px;
  border: 1px solid var(--accent-tint-25);
  border-radius: var(--radius-sm);
  background: var(--accent-tint-06);
  color: var(--color-text-soft);
  font-size: 0.82rem;
}

.admin-page :deep(.admin-page__create-btn) {
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

.admin-page :deep(.admin-page__create-btn:hover) {
  background: var(--accent-tint-20);
  border-color: var(--color-accent);
}

.admin-page :deep(.admin-page__create-btn--sm) {
  padding: 8px 16px;
  font-size: 0.82rem;
}

.admin-page :deep(.admin-page__loading),
.admin-page :deep(.admin-page__error) {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-text-muted);
}

.admin-page :deep(.admin-page__retry) {
  margin-top: var(--space-md);
  padding: 8px 20px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  background: var(--glass-bg-02);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.admin-page :deep(.admin-page__retry:hover) {
  border-color: var(--accent-tint-40);
  color: var(--color-accent);
}

.admin-page :deep(.admin-page__inline-form) {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.admin-page :deep(.admin-page__inline-form .admin-input) {
  flex: 1 1 160px;
  min-width: 0;
}

.admin-page :deep(.admin-input) {
  min-height: 38px;
  padding: 8px 14px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  background: var(--glass-bg-12);
  color: var(--color-text);
  font-size: 0.88rem;
  font-family: inherit;
  outline: none;
  transition: border-color var(--duration-fast) ease, background var(--duration-fast) ease;
}

.admin-page :deep(.admin-input::placeholder) {
  color: var(--color-text-muted);
}

.admin-page :deep(.admin-input:focus) {
  border-color: var(--accent-tint-50);
  background: var(--glass-bg-20);
}

.admin-page :deep(.admin-input--inline) {
  width: 100%;
  min-width: 60px;
  min-height: 32px;
  padding: 4px 8px;
  font-size: 0.82rem;
}

.admin-page :deep(.admin-input--textarea) {
  width: 100%;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.admin-page :deep(.admin-table-wrap) {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  background: var(--glass-surface-bg);
  backdrop-filter: var(--glass-card-blur);
  -webkit-backdrop-filter: var(--glass-card-blur);
}

.admin-page :deep(.admin-table) {
  width: 100%;
  min-width: 760px;
  border-collapse: separate;
  border-spacing: 0;
  background: transparent;
}

.admin-page :deep(.admin-table th),
.admin-page :deep(.admin-table td) {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 0.88rem;
  vertical-align: middle;
}

.admin-page :deep(.admin-table th) {
  font-weight: 600;
  color: var(--color-text-muted);
  background: var(--glass-bg-03);
  white-space: nowrap;
}

.admin-page :deep(.admin-table td) {
  color: var(--color-text-soft);
}

.admin-page :deep(.admin-table tr:last-child td) {
  border-bottom: none;
}

.admin-page :deep(.admin-table input[type="checkbox"]) {
  width: 16px;
  height: 16px;
  accent-color: var(--color-accent);
}

.admin-page :deep(.admin-table__title) {
  max-width: 360px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-text);
  font-weight: 500;
}

.admin-page :deep(.admin-table__date),
.admin-page :deep(.admin-table__actions) {
  white-space: nowrap;
}

.admin-page :deep(.admin-table__actions .admin-btn) {
  margin-right: 6px;
}

.admin-page :deep(.admin-table__actions .admin-btn:last-child) {
  margin-right: 0;
}

.admin-page :deep(.admin-table__empty) {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--space-xl);
}

.admin-page :deep(.admin-table__reply-row) {
  padding: var(--space-md);
  background: var(--glass-bg-04);
}

.admin-page :deep(.admin-page__reply-form) {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.admin-page :deep(.admin-page__reply-label) {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-heading);
}

.admin-page :deep(.admin-page__reply-actions) {
  display: flex;
  gap: var(--space-sm);
}

.admin-page :deep(.admin-toggle) {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.admin-page :deep(.admin-toggle input) {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.admin-page :deep(.admin-toggle__track) {
  position: relative;
  width: 38px;
  height: 20px;
  background: var(--border-strong);
  border: 1px solid var(--border-default);
  border-radius: 10px;
  transition: all var(--duration-fast) ease;
}

.admin-page :deep(.admin-toggle__thumb) {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 14px;
  height: 14px;
  background: var(--color-text-muted);
  border-radius: 50%;
  transition: all var(--duration-fast) ease;
}

.admin-page :deep(.admin-toggle input:checked + .admin-toggle__track) {
  background: var(--accent-tint-25);
  border-color: var(--accent-tint-50);
}

.admin-page :deep(.admin-toggle input:checked + .admin-toggle__track .admin-toggle__thumb) {
  left: 20px;
  background: var(--color-accent);
}

.admin-page :deep(.admin-toggle:hover .admin-toggle__track) {
  border-color: var(--border-heavy-2);
}

/* 按钮样式统一使用 base.css 全局 .admin-btn */

.admin-page :deep(.admin-page__badge) {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  font-size: 0.72rem;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

.admin-page :deep(.admin-page__badge--approved) {
  background: rgba(16, 185, 129, 0.12);
  color: var(--success-main);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.admin-page :deep(.admin-page__badge--pending) {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.admin-page :deep(.admin-page__badge--draft) {
  background: rgba(139, 92, 246, 0.12);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

/* edit/delete 按钮样式统一在 base.css */

.admin-page__panel {
  animation: adminFadeIn 0.2s ease;
}

@keyframes adminFadeIn {
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

/* 按钮统一样式见 base.css */

.admin-page__badge {
  font-size: 0.72rem;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.admin-page__badge--approved {
  background: rgba(16, 185, 129, 0.12);
  color: var(--success-main);
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
  color: var(--error-main);
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
  color: var(--error-main);
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
  color: var(--error-main);
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

  .admin-page :deep(.admin-input) {
    flex: 1;
    min-width: 120px;
  }

  .admin-page :deep(.admin-page__toolbar) {
    align-items: flex-start;
    flex-direction: column;
  }

  .admin-page :deep(.admin-table-wrap) {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .admin-page :deep(.admin-table) {
    min-width: 600px;
  }

  .admin-page :deep(.admin-table th),
  .admin-page :deep(.admin-table td) {
    padding: 10px 10px;
    font-size: 0.82rem;
  }
}
</style>
