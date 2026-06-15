<template>
  <div class="admin-page__panel">
    <div class="admin-page__toolbar">
      <div class="admin-page__toolbar-left">
        <button class="admin-btn admin-btn--edit" @click="handleExportPosts">导出全部</button>
        <label class="admin-btn admin-btn--edit" style="cursor:pointer;">
          导入
          <input type="file" accept=".zip" @change="handleImportPosts" style="display:none" />
        </label>
      </div>
      <div v-if="selectedPostIds.size" class="admin-page__batch-bar">
        <span>已选 {{ selectedPostIds.size }} 篇</span>
        <button class="admin-btn admin-btn--delete" @click="handleBatchDeletePosts">批量删除</button>
      </div>
    </div>
    <div v-if="!postsLoaded" class="admin-page__loading">加载中...</div>
    <div v-else-if="postsError" class="admin-page__error">
      <p>加载失败</p>
      <button class="admin-page__retry" @click="loadPosts">重试</button>
    </div>
    <template v-else>
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th><input type="checkbox" :checked="selectedPostIds.size === posts.length && posts.length > 0" @change="toggleAllPosts" /></th>
              <th>标题</th>
              <th>分类</th>
              <th>状态</th>
              <th>精选</th>
              <th>发布日期</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="post in posts" :key="post.id">
              <td><input type="checkbox" :checked="selectedPostIds.has(post.id)" @change="togglePostSelect(post.id)" /></td>
              <td class="admin-table__title">{{ post.title }}</td>
              <td>{{ post.category?.name ?? '-' }}</td>
              <td>
                <span class="admin-page__badge" :class="post.status === 'published' ? 'admin-page__badge--approved' : 'admin-page__badge--draft'">
                  {{ post.status === 'published' ? '已发布' : '草稿' }}
                </span>
              </td>
              <td>
                <label class="admin-toggle" :title="post.is_featured ? '取消精选' : '设为精选'">
                  <input type="checkbox" :checked="post.is_featured" @change="toggleFeatured(post)" />
                  <span class="admin-toggle__track"><span class="admin-toggle__thumb"></span></span>
                </label>
              </td>
              <td class="admin-table__date">{{ formatDate(post.published_at) }}</td>
              <td class="admin-table__actions">
                <button class="admin-btn admin-btn--edit" @click="$router.push(`/edit-post/${post.slug}`)">编辑</button>
                <button class="admin-btn admin-btn--delete" @click="emit('delete', 'post', post.id, post.title)">删除</button>
              </td>
            </tr>
            <tr v-if="!posts.length">
              <td colspan="6" class="admin-table__empty">暂无文章</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getAdminPosts, updatePost, batchDeletePosts, exportPosts, importPosts } from '@/api/admin'
import { safeCall } from '@/api/http'
import { useToastStore } from '@/stores/toast'
import type { PostSummary } from '@/types/blog'

const toast = useToastStore()

const emit = defineEmits<{
  delete: [type: string, id: number, name: string]
}>()

const posts = ref<PostSummary[]>([])
const postsLoaded = ref(false)
const postsError = ref(false)

async function loadPosts() {
  postsLoaded.value = false
  postsError.value = false
  const result = await safeCall(() => getAdminPosts(), [] as PostSummary[])
  posts.value = result
  postsLoaded.value = true
}

async function toggleFeatured(post: PostSummary) {
  try {
    await updatePost(post.id, { is_featured: !post.is_featured })
    post.is_featured = !post.is_featured
  } catch {
    toast.error('切换精选状态失败，请稍后重试')
  }
}

const selectedPostIds = ref<Set<number>>(new Set())

function togglePostSelect(id: number) {
  if (selectedPostIds.value.has(id)) {
    selectedPostIds.value.delete(id)
  } else {
    selectedPostIds.value.add(id)
  }
  selectedPostIds.value = new Set(selectedPostIds.value)
}

function toggleAllPosts() {
  if (selectedPostIds.value.size === posts.value.length) {
    selectedPostIds.value = new Set()
  } else {
    selectedPostIds.value = new Set(posts.value.map(p => p.id))
  }
}

async function handleBatchDeletePosts() {
  const ids = [...selectedPostIds.value]
  if (!ids.length) return
  try {
    await batchDeletePosts(ids)
    selectedPostIds.value = new Set()
    await loadPosts()
  } catch {
    toast.error('批量删除失败，请稍后重试')
  }
}

async function handleExportPosts() {
  try {
    const blob = await exportPosts()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'blog_posts.zip'
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.error('导出失败，请稍后重试')
  }
}

async function handleImportPosts(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  try {
    await importPosts(file)
    await loadPosts()
  } catch {
    toast.error('导入失败，请检查文件格式是否正确')
  } finally {
    target.value = ''
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

loadPosts()
</script>
