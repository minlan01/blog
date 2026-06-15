<template>
  <div class="admin-page__panel">
    <div class="admin-page__inline-form">
      <input v-model="newLinkName" class="admin-input" placeholder="名称" />
      <input v-model="newLinkUrl" class="admin-input" placeholder="URL" />
      <input v-model="newLinkDesc" class="admin-input" placeholder="描述" />
      <input v-model="newLinkCategory" class="admin-input" placeholder="分类" style="max-width:100px" />
      <button class="admin-page__create-btn admin-page__create-btn--sm" @click="handleAddLink">新增</button>
    </div>
    <div v-if="!linksLoaded" class="admin-page__loading">加载中...</div>
    <div v-else class="admin-table-wrap">
      <table class="admin-table">
        <thead>
          <tr>
            <th>名称</th>
            <th>URL</th>
            <th>分类</th>
            <th>排序</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="link in friendLinks" :key="link.id">
            <td>
              <input v-if="editingLink?.id === link.id" v-model="editingLink.name" class="admin-input admin-input--inline" @keyup.enter="handleSaveLink(link.id)" @keyup.escape="editingLink = null" />
              <span v-else>{{ link.name }}</span>
            </td>
            <td>
              <input v-if="editingLink?.id === link.id" v-model="editingLink.url" class="admin-input admin-input--inline" style="font-family:var(--font-mono);font-size:0.82rem;" @keyup.enter="handleSaveLink(link.id)" @keyup.escape="editingLink = null" />
              <span v-else style="font-family:var(--font-mono);font-size:0.82rem;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block;">{{ link.url }}</span>
            </td>
            <td>
              <input v-if="editingLink?.id === link.id" v-model="editingLink.category" class="admin-input admin-input--inline" style="max-width:100px" @keyup.enter="handleSaveLink(link.id)" @keyup.escape="editingLink = null" />
              <span v-else>{{ link.category }}</span>
            </td>
            <td>
              <input v-if="editingLink?.id === link.id" v-model.number="editingLink.sort_order" type="number" class="admin-input admin-input--inline" style="max-width:60px" @keyup.enter="handleSaveLink(link.id)" @keyup.escape="editingLink = null" />
              <span v-else>{{ link.sort_order }}</span>
            </td>
            <td class="admin-table__actions">
              <template v-if="editingLink?.id === link.id">
                <button class="admin-btn admin-btn--edit" @click="handleSaveLink(link.id)">保存</button>
                <button class="admin-btn" @click="editingLink = null">取消</button>
              </template>
              <template v-else>
                <button class="admin-btn admin-btn--edit" @click="startEditLink(link)">编辑</button>
                <button class="admin-btn admin-btn--delete" @click="emit('delete', 'friend-link', link.id, link.name)">删除</button>
              </template>
            </td>
          </tr>
          <tr v-if="!friendLinks.length">
            <td colspan="5" class="admin-table__empty">暂无友链</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createFriendLink, updateFriendLink } from '@/api/admin'
import { getFriendLinks } from '@/api/blog'
import { safeCall } from '@/api/http'
import { useToastStore } from '@/stores/toast'
import type { FriendLink } from '@/types/blog'

const toast = useToastStore()

const emit = defineEmits<{
  delete: [type: string, id: number, name: string]
}>()

const friendLinks = ref<FriendLink[]>([])
const linksLoaded = ref(false)
const newLinkName = ref('')
const newLinkUrl = ref('')
const newLinkDesc = ref('')
const newLinkCategory = ref('default')
const editingLink = ref<{ id: number; name: string; url: string; category: string; sort_order: number } | null>(null)

async function loadFriendLinks() {
  linksLoaded.value = false
  friendLinks.value = await safeCall(() => getFriendLinks(), [])
  linksLoaded.value = true
}

async function handleAddLink() {
  const name = newLinkName.value.trim()
  const url = newLinkUrl.value.trim()
  if (!name || !url) return
  try {
    await createFriendLink({
      name,
      url,
      description: newLinkDesc.value.trim() || undefined,
      category: newLinkCategory.value.trim() || 'default',
    })
    newLinkName.value = ''
    newLinkUrl.value = ''
    newLinkDesc.value = ''
    newLinkCategory.value = 'default'
    await loadFriendLinks()
  } catch {
    toast.error('新增友链失败，请稍后重试')
  }
}

function startEditLink(link: FriendLink) {
  editingLink.value = { id: link.id, name: link.name, url: link.url, category: link.category ?? 'default', sort_order: link.sort_order ?? 0 }
}

async function handleSaveLink(id: number) {
  if (!editingLink.value) return
  const { name, url, category, sort_order } = editingLink.value
  try {
    await updateFriendLink(id, { name, url, category, sort_order })
    editingLink.value = null
    await loadFriendLinks()
  } catch {
    toast.error('保存友链失败，请稍后重试')
  }
}

loadFriendLinks()
</script>
