<template>
  <section class="editor">
    <div class="container narrow-container">
      <header class="editor__header">
        <div class="editor__header-left">
          <button class="editor__back" @click="router.push('/admin')">&larr; 返回管理</button>
          <h1 class="editor__title">编辑文章</h1>
        </div>
        <div class="editor__header-actions">
          <button class="editor__draft-btn" @click="handleSaveDraft" :disabled="submitting">
            {{ submitting ? '保存中...' : '保存草稿' }}
          </button>
          <button class="editor__publish" @click="handlePublish" :disabled="submitting">
            {{ submitting ? '保存中...' : (form.status === 'published' ? '更新' : '发布') }}
          </button>
        </div>
      </header>

      <div v-if="loading" class="editor__loading">加载中...</div>
      <div v-else-if="error && !form.title" class="editor__error">{{ error }}</div>

      <form v-else class="editor__form" @submit.prevent>
        <div class="editor__field">
          <input v-model="form.title" type="text" class="editor__title-input" placeholder="文章标题" required />
        </div>
        <div class="editor__row">
          <div class="editor__field editor__field--half">
            <label class="editor__label">链接别名 (slug)</label>
            <input v-model="form.slug" type="text" class="editor__input" required />
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
          <textarea v-model="form.summary" class="editor__textarea editor__textarea--short" required rows="2"></textarea>
        </div>
        <div class="editor__field">
          <label class="editor__label">封面图片</label>
          <div class="editor__cover-row">
            <input v-model="form.cover_image" type="text" class="editor__input" />
            <button type="button" class="editor__upload-btn" @click="($refs.fileInput as any)?.click()" :disabled="uploading">
              {{ uploading ? '上传中...' : '上传图片' }}
            </button>
            <input ref="fileInput" type="file" accept="image/*" class="editor__file-hidden" @change="handleFileUpload" />
          </div>
        </div>
        <div class="editor__field editor__md-editor">
          <label class="editor__label">正文 (Markdown)</label>
          <MdEditor v-model="form.content_markdown" :theme="theme" @onUploadImg="onUploadImg" />
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
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { http } from '@/api/http'
import { getAdminPosts } from '@/api/admin'
import { getCategories } from '@/api/blog'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { useImageUpload } from '@/composables/useImageUpload'
import { useTheme } from '@/composables/useTheme'
import { calculateReadingTime } from '@/utils/readingTime'
import type { Category } from '@/types/blog'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const toast = useToastStore()
const { theme } = useTheme()
const categories = ref<Category[]>([])
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const postIdNum = ref<number | null>(null)
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
  status: 'draft',
})

async function loadPost() {
  const slug = route.params.id as string
  try {
    const { data: listData } = await http.get<any>(`/admin/posts`, { params: { slug } })
    const postSummary = listData?.[0]
    if (!postSummary) {
      error.value = 'Post not found.'
      return
    }
    postIdNum.value = postSummary.id
    const { data: post } = await http.get<any>(`/admin/posts/${postSummary.id}`)
    form.value = {
      title: post.title,
      slug: post.slug,
      summary: post.summary,
      content_markdown: post.content_markdown || '',
      cover_image: post.cover_image || '',
      is_featured: post.is_featured,
      category_id: post.category?.id || null,
      tag_ids: post.tags?.map((t: any) => t.id) || [],
      status: post.status || 'draft',
    }
  } catch (e: any) {
    error.value = 'Failed to load post.'
  } finally {
    loading.value = false
  }
}

async function onUploadImg(files: File[], callback: (urls: string[]) => void) {
  const urls: string[] = []
  for (const file of files) {
    const url = await uploadImage(file)
    if (url) urls.push(url)
  }
  callback(urls)
}

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const url = await uploadImage(file)
  if (url) form.value.cover_image = url
  target.value = ''
}

async function handleSubmit(status: 'draft' | 'published') {
  error.value = ''
  submitting.value = true
  try {
    const reading_time = calculateReadingTime(form.value.content_markdown)
    const payload: Record<string, any> = {
      title: form.value.title,
      slug: form.value.slug,
      summary: form.value.summary,
      content_markdown: form.value.content_markdown,
      reading_time,
      is_featured: form.value.is_featured,
      category_id: form.value.category_id,
      tag_ids: form.value.tag_ids,
      status,
    }
    if (form.value.cover_image) {
      payload.cover_image = form.value.cover_image
    }
    await http.put(`/admin/posts/${postIdNum.value}`, payload)
    form.value.status = status
    if (status === 'published') {
      router.push(`/posts/${form.value.slug}`)
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Save failed.'
  } finally {
    submitting.value = false
  }
}

async function handleSaveDraft() {
  await handleSubmit('draft')
}

async function handlePublish() {
  await handleSubmit('published')
}

onMounted(async () => {
  if (!authStore.isAdmin) {
    router.push('/')
    return
  }
  await Promise.all([
    loadPost(),
    getCategories().then(cats => { categories.value = cats }).catch(() => { toast.error('加载分类失败，请刷新页面重试') }),
  ])
})
</script>

<style scoped>
@import '@/assets/styles/editor.css';

.editor__md-editor {
  display: flex;
  flex-direction: column;
}

.editor__draft-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-bg-secondary);
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.2s;
}

.editor__draft-btn:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.editor__draft-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.editor__header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}
</style>
