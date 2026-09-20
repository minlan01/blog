<template>
  <section class="editor">
    <div class="container narrow-container">
      <Transition name="draft-banner">
        <div v-if="showDraftPrompt" class="editor__draft-restore">
          <span>检测到未保存的草稿，是否恢复？</span>
          <button class="editor__draft-btn--restore" @click="restoreDraft">恢复</button>
          <button class="editor__draft-btn--discard" @click="discardDraft">丢弃</button>
        </div>
      </Transition>
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
              {{ uploading ? '上传中...' : '上传封面' }}
            </button>
            <input ref="fileInput" type="file" accept="image/*" class="editor__file-hidden" @change="handleFileUpload" />
            <button type="button" class="editor__upload-btn" @click="showCoverPicker = true">媒体库</button>
            <button type="button" class="editor__upload-btn" @click="($refs.mediaInput as any)?.click()" :disabled="uploading">
              {{ uploading ? '上传中...' : '插入视频/音频' }}
            </button>
            <input ref="mediaInput" type="file" accept="video/*,audio/*,.mkv,.m4a,.mp3,.wav,.aac,.ogg" class="editor__file-hidden" @change="handleMediaUpload" />
          </div>
        </div>
        <div class="editor__field editor__md-editor">
          <div class="editor__md-header">
            <label class="editor__label">正文 (Markdown)</label>
            <button type="button" class="editor__media-lib-btn" @click="showContentPicker = true" title="从媒体库插入图片">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/>
              </svg>
              媒体库图片
            </button>
          </div>
          <div class="editor__md-wrap">
            <MdEditor :key="isNarrowScreen ? 'mobile' : 'desktop'" v-model="form.content_markdown" :theme="theme" :preview="!isNarrowScreen" @onUploadImg="onUploadImg" />
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

    <!-- 媒体库选择器 - 封面 -->
    <MediaPicker
      :visible="showCoverPicker"
      confirm-text="设为封面"
      @update:visible="showCoverPicker = $event"
      @select="onPickCover"
    />
    <!-- 媒体库选择器 - 正文图片 -->
    <MediaPicker
      :visible="showContentPicker"
      confirm-text="插入正文"
      @update:visible="showContentPicker = $event"
      @select="onPickContentImage"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { setupMdEditorExtensions, isNarrowScreen } from '@/utils/mdEditorConfig'

setupMdEditorExtensions()
import { http } from '@/api/http'
import { getCategories } from '@/api/blog'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { useImageUpload } from '@/composables/useImageUpload'
import { usePasteUpload } from '@/composables/usePasteUpload'
import { useAutoSave } from '@/composables/useAutoSave'
import { useTheme } from '@/composables/useTheme'
import { calculateReadingTime } from '@/utils/readingTime'
import MediaPicker from '@/components/MediaPicker.vue'
import type { Category } from '@/types/blog'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToastStore()
const { theme } = useTheme()
const categories = ref<Category[]>([])
const submitting = ref(false)
const error = ref('')
const { uploading, uploadImage, uploadMedia } = useImageUpload()
const fileInput = ref<HTMLInputElement | null>(null)
const mediaInput = ref<HTMLInputElement | null>(null)
const showCoverPicker = ref(false)
const showContentPicker = ref(false)

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

// 自动保存草稿到 localStorage
const { loadDraft, clearDraft } = useAutoSave('create-post', form)
const hasDraftRestored = ref(false)
const showDraftPrompt = ref(false)
let draftData: any = null

onMounted(() => {
  draftData = loadDraft()
  if (draftData && (draftData.title || draftData.content_markdown)) {
    showDraftPrompt.value = true
  }
})

function restoreDraft() {
  if (draftData) {
    Object.assign(form.value, draftData)
    toast.success('已恢复未保存的草稿')
  }
  showDraftPrompt.value = false
}

function discardDraft() {
  clearDraft()
  showDraftPrompt.value = false
}

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

// Enable paste/drag image upload in the editor
const contentRef = computed({
  get: () => form.value.content_markdown,
  set: (v: string) => { form.value.content_markdown = v },
})
usePasteUpload(contentRef)

async function handleMediaUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const result = await uploadMedia(file)
  if (result) {
    if (result.mediaType === 'video') {
      form.value.content_markdown += `\n\n<video controls src="${result.url}" style="max-width:100%;border-radius:8px;"></video>\n\n`
    } else if (result.mediaType === 'audio') {
      form.value.content_markdown += `\n\n<audio controls src="${result.url}" style="width:100%;"></audio>\n\n`
    }
  }
  target.value = ''
}

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const url = await uploadImage(file)
  if (url) form.value.cover_image = url
  target.value = ''
}

function resolveMediaUrl(url: string): string {
  if (url.startsWith('http') || url.startsWith('/api/') || url.startsWith('/uploads/')) return url
  return `/api/v1${url.startsWith('/') ? url : `/${url}`}`
}

function onPickCover(item: any) {
  if (item.url) {
    form.value.cover_image = resolveMediaUrl(item.url)
  }
}

function onPickContentImage(item: any) {
  if (item.url) {
    const url = resolveMediaUrl(item.url)
    form.value.content_markdown += `\n\n![${item.filename || 'image'}](${url})\n\n`
  }
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
    clearDraft()
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
  align-items: center;
}

.editor__md-editor {
  display: flex;
  flex-direction: column;
}

.editor__md-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xs);
}

.editor__media-lib-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0.4rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur);
  -webkit-backdrop-filter: var(--glass-card-blur);
  color: var(--color-text-soft);
  font-size: 0.78rem;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.editor__media-lib-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: var(--accent-tint-08);
}

/* 草稿恢复提示条 */
.editor__draft-restore {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  margin-bottom: 0.75rem;
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur);
  -webkit-backdrop-filter: var(--glass-card-blur);
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-text);
}

.editor__draft-restore span {
  flex: 1;
}

.editor__draft-btn--restore,
.editor__draft-btn--discard {
  padding: 0.35rem 0.9rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--glass-border);
  background: transparent;
  color: var(--color-text);
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.editor__draft-btn--restore {
  background: var(--color-accent);
  color: #fff;
  border-color: var(--color-accent);
}

.editor__draft-btn--restore:hover {
  opacity: 0.9;
}

.editor__draft-btn--discard:hover {
  background: var(--glass-surface-bg);
}

.draft-banner-enter-active,
.draft-banner-leave-active {
  transition: all 0.3s ease;
}

.draft-banner-enter-from,
.draft-banner-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
