<template>
  <div class="admin-page__panel">
    <div class="admin-page__inline-form">
      <input
        v-model="newCatName"
        class="admin-input"
        placeholder="分类名称"
        @keyup.enter="handleAddCategory"
      />
      <input
        v-model="newCatSlug"
        class="admin-input"
        placeholder="Slug（可选）"
        @keyup.enter="handleAddCategory"
      />
      <button class="admin-page__create-btn admin-page__create-btn--sm" @click="handleAddCategory">新增</button>
    </div>
    <div v-if="!catsLoaded" class="admin-page__loading">加载中...</div>
    <div v-else class="admin-table-wrap">
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>Slug</th>
            <th>描述</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cat in categories" :key="cat.id">
            <td>{{ cat.id }}</td>
            <td>
              <input v-if="editingCat?.id === cat.id" v-model="editingCat.name" class="admin-input admin-input--inline" @keyup.enter="handleSaveCategory(cat.id)" @keyup.escape="editingCat = null" />
              <span v-else>{{ cat.name }}</span>
            </td>
            <td>
              <input v-if="editingCat?.id === cat.id" v-model="editingCat.slug" class="admin-input admin-input--inline" @keyup.enter="handleSaveCategory(cat.id)" @keyup.escape="editingCat = null" />
              <span v-else>{{ cat.slug }}</span>
            </td>
            <td>
              <input v-if="editingCat?.id === cat.id" v-model="editingCat.description" class="admin-input admin-input--inline" placeholder="描述（可选）" @keyup.enter="handleSaveCategory(cat.id)" @keyup.escape="editingCat = null" />
              <span v-else>{{ cat.description ?? '-' }}</span>
            </td>
            <td class="admin-table__actions">
              <template v-if="editingCat?.id === cat.id">
                <button class="admin-btn admin-btn--edit" @click="handleSaveCategory(cat.id)">保存</button>
                <button class="admin-btn" @click="editingCat = null">取消</button>
              </template>
              <template v-else>
                <button class="admin-btn admin-btn--edit" @click="startEditCategory(cat)">编辑</button>
                <button class="admin-btn admin-btn--delete" @click="emit('delete', 'category', cat.id, cat.name)">删除</button>
              </template>
            </td>
          </tr>
          <tr v-if="!categories.length">
            <td colspan="5" class="admin-table__empty">暂无分类</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createCategory, updateCategory } from '@/api/admin'
import { getCategories } from '@/api/blog'
import { safeCall } from '@/api/http'
import { useToastStore } from '@/stores/toast'
import type { Category } from '@/types/blog'

const toast = useToastStore()

const emit = defineEmits<{
  delete: [type: string, id: number, name: string]
}>()

const categories = ref<Category[]>([])
const catsLoaded = ref(false)
const newCatName = ref('')
const newCatSlug = ref('')
const editingCat = ref<{ id: number; name: string; slug: string; description: string } | null>(null)

async function loadCategories() {
  catsLoaded.value = false
  categories.value = await safeCall(() => getCategories(), [])
  catsLoaded.value = true
}

async function handleAddCategory() {
  const name = newCatName.value.trim()
  if (!name) return
  const slug = newCatSlug.value.trim() || name.toLowerCase().replace(/\s+/g, '-')
  try {
    await createCategory({ name, slug })
    newCatName.value = ''
    newCatSlug.value = ''
    await loadCategories()
  } catch {
    toast.error('新增分类失败，请稍后重试')
  }
}

function startEditCategory(cat: Category) {
  editingCat.value = { id: cat.id, name: cat.name, slug: cat.slug, description: cat.description ?? '' }
}

async function handleSaveCategory(id: number) {
  if (!editingCat.value) return
  const { name, slug, description } = editingCat.value
  try {
    await updateCategory(id, { name, slug, description: description || undefined })
    editingCat.value = null
    await loadCategories()
  } catch {
    toast.error('保存分类失败，请稍后重试')
  }
}

loadCategories()
</script>
