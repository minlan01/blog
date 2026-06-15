<template>
  <section class="editor">
    <div class="container narrow-container">
      <header class="editor__header">
        <div class="editor__header-left">
          <button class="editor__back" @click="router.push('/admin')">&larr; 返回管理</button>
          <h1 class="editor__title">写文章</h1>
        </div>
        <div class="editor__header-actions">
          <button class="editor__draft-btn" @click="handleSubmit('draft')" :disabled="submitting">
            {{ submitting ? '保存中...' : '存草稿' }}
          </button>
          <button class="editor__publish" @click="handleSubmit('published')" :disabled="submitting">
            {{ submitting ? '发布中...' : '发布' }}
          </button>
        </div>
      </header>

      <div v-if="error" class="editor__error">{{ error }}</div>

      <form class="editor__form" @submit.prevent="handleSubmit('published')">
        <div class="editor__field">
          <input v-model="form.title" type="text" class="editor__title-input" placeholder="文章标题" required />
        </div>
        <div class="editor__row">
          <div class="editor__field editor__field--half">
            <label class="editor__label">链接别名 (slug)</label>
            <input v-model="form.slug" type="text" class="editor__input" placeholder="url-friendly-slug" required />
          </div>
          <div class="editor__field editor__field--half">
            <label class="editor__label">分类</label>
            <select v-model="form.category_id" class="editor__input">
              <option :value="null">无分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
        </div>
        <div class="editor__field">
          <label class="editor__label">摘要</label>
          <textarea v-model="form.summary" class="editor__textarea editor__textarea--short" placeholder="简要描述..." required rows="2"></textarea>
        </div>
        <div class="editor__field">
          <label class="editor__label">封面图片</label>
          <div class="editor__cover-row">
            <input v-model="form.cover_image" type="text" class="editor__input" placeholder="https://..." />
            <button type="button" class="editor__upload-btn" @click="($refs.fileInput as any)?.click()" :disabled="uploading">
              {{ uploading ? '上传中...' : '上传图片' }}
            </button>
            <input ref="fileInput" type="file" accept="image/*" class="editor__file-hidden" @change="handleFileUpload" />
          </div>
        </div>
        <div class="editor__field">
          <label class="editor__label">正文 (Markdown)</label>
          <div class="editor__md-editor">
            <MdEditor v-model="form.content_markdown" :theme="theme" @onUploadImg="onUploadImg" />
          </div>
        </div>
        <div class="editor__field">
          <label class="editor__inline-label">
            <input type="checkbox" v-model="form.is_featured" />
            <span>设为精选</span>
          </label>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { http } from '@/api/http'
import { getCategories } from '@/api/blog'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { useImageUpload } from '@/composables/useImageUpload'
import { useTheme } from '@/composables/useTheme'
import { calculateReadingTime } from '@/utils/readingTime'
import type { Category } from '@/types/blog'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToastStore()
const { theme } = useTheme()
const categories = ref<Category[]>([])
const submitting = ref(false)
const error = ref('')
const { uploading, uploadImage } = useImageUpload()
const fileInput = ref<HTMLInputElement | null>(null)

const form = ref({
  title: '',
  slug: '',
  summary: '',
  content_markdown: '',
  cover_image: '',
  is_featured: false,
  category_id: null as number | null,
  tag_ids: [] as number[],
})

watch(() => form.value.title, (title) => {
  const generated = title
    .toLowerCase()
    .replace(/[^\w\s\u4e00-\u9fff-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .slice(0, 200)
    .replace(/^-|-$/g, '')
  form.value.slug = generated || `post-${Date.now()}`
})

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const url = await uploadImage(file)
  if (url) form.value.cover_image = url
  target.value = ''
}

async function onUploadImg(files: File[], callback: (urls: string[]) => void) {
  const urls = await Promise.all(files.map(async (file) => {
    const url = await uploadImage(file)
    return url || ''
  }))
  callback(urls.filter(Boolean))
}

async function handleSubmit(status: 'published' | 'draft') {
  if (!form.value.title || !form.value.content_markdown) return
  error.value = ''
  submitting.value = true
  try {
    const payload = {
      title: form.value.title,
      slug: form.value.slug || `post-${Date.now()}`,
      summary: form.value.summary,
      content_markdown: form.value.content_markdown,
      cover_image: form.value.cover_image || null,
      is_featured: form.value.is_featured,
      category_id: form.value.category_id,
      tag_ids: form.value.tag_ids,
      status,
      reading_time: calculateReadingTime(form.value.content_markdown),
    }
    const { data } = await http.post('/admin/posts', payload)
    router.push(`/posts/${data.slug}`)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Publish failed.'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  if (!authStore.isAdmin) {
    router.push('/')
    return
  }
  try {
    categories.value = await getCategories()
  } catch {
    toast.error('加载分类失败，请刷新页面重试')
  }
})
</script>

<style scoped>
@import '@/assets/styles/editor.css';

.editor__header-actions {
  display: flex;
  gap: 12px;
}

.editor__draft-btn {
  padding: 8px 16px;
  border: 1px solid var(--color-accent);
  background: transparent;
  color: var(--color-accent);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.editor__draft-btn:hover:not(:disabled) {
  background: var(--color-accent);
  color: var(--color-bg-deep);
}

.editor__draft-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.editor__md-editor {
  border-radius: var(--radius-md);
  overflow: hidden;
}
</style>
