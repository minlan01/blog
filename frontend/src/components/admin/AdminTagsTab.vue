<template>
  <div class="admin-page__panel">
    <div class="admin-page__inline-form">
      <input
        v-model="newTagName"
        class="admin-input"
        placeholder="标签名称"
        @keyup.enter="handleAddTag"
      />
      <input
        v-model="newTagSlug"
        class="admin-input"
        placeholder="Slug（可选）"
        @keyup.enter="handleAddTag"
      />
      <button class="admin-page__create-btn admin-page__create-btn--sm" @click="handleAddTag">新增</button>
    </div>
    <div v-if="!tagsLoaded" class="admin-page__loading">加载中...</div>
    <div v-else class="admin-table-wrap">
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>Slug</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tag in tags" :key="tag.id">
            <td>{{ tag.id }}</td>
            <td>
              <input v-if="editingTag?.id === tag.id" v-model="editingTag.name" class="admin-input admin-input--inline" @keyup.enter="handleSaveTag(tag.id)" @keyup.escape="editingTag = null" />
              <span v-else>{{ tag.name }}</span>
            </td>
            <td>
              <input v-if="editingTag?.id === tag.id" v-model="editingTag.slug" class="admin-input admin-input--inline" @keyup.enter="handleSaveTag(tag.id)" @keyup.escape="editingTag = null" />
              <span v-else>{{ tag.slug }}</span>
            </td>
            <td class="admin-table__actions">
              <template v-if="editingTag?.id === tag.id">
                <button class="admin-btn admin-btn--edit" @click="handleSaveTag(tag.id)">保存</button>
                <button class="admin-btn" @click="editingTag = null">取消</button>
              </template>
              <template v-else>
                <button class="admin-btn admin-btn--edit" @click="startEditTag(tag)">编辑</button>
                <button class="admin-btn admin-btn--delete" @click="emit('delete', 'tag', tag.id, tag.name)">删除</button>
              </template>
            </td>
          </tr>
          <tr v-if="!tags.length">
            <td colspan="4" class="admin-table__empty">暂无标签</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createTag, updateTag } from '@/api/admin'
import { getTags } from '@/api/blog'
import { safeCall } from '@/api/http'
import { useToastStore } from '@/stores/toast'
import type { Tag } from '@/types/blog'

const toast = useToastStore()

const emit = defineEmits<{
  delete: [type: string, id: number, name: string]
}>()

const tags = ref<Tag[]>([])
const tagsLoaded = ref(false)
const newTagName = ref('')
const newTagSlug = ref('')
const editingTag = ref<{ id: number; name: string; slug: string } | null>(null)

async function loadTags() {
  tagsLoaded.value = false
  tags.value = await safeCall(() => getTags(), [])
  tagsLoaded.value = true
}

async function handleAddTag() {
  const name = newTagName.value.trim()
  if (!name) return
  const slug = newTagSlug.value.trim() || name.toLowerCase().replace(/\s+/g, '-')
  try {
    await createTag({ name, slug })
    newTagName.value = ''
    newTagSlug.value = ''
    await loadTags()
  } catch {
    toast.error('新增标签失败，请稍后重试')
  }
}

function startEditTag(tag: Tag) {
  editingTag.value = { id: tag.id, name: tag.name, slug: tag.slug }
}

async function handleSaveTag(id: number) {
  if (!editingTag.value) return
  const { name, slug } = editingTag.value
  try {
    await updateTag(id, { name, slug })
    editingTag.value = null
    await loadTags()
  } catch {
    toast.error('保存标签失败，请稍后重试')
  }
}

loadTags()
</script>
