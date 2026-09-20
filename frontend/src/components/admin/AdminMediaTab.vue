<template>
  <div class="admin-page__panel">
    <div class="admin-page__media-toolbar">
      <div class="admin-page__media-toolbar__left">
        <button class="admin-page__media-btn admin-page__media-btn--primary" :disabled="mediaUploading" @click="triggerMediaUpload">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <path d="m17 8-5-5-5 5" />
            <path d="M12 3v12" />
          </svg>
          {{ mediaUploading ? '上传中...' : '选择媒体' }}
        </button>
        <input
          ref="mediaFileInput"
          type="file"
          accept="image/*,video/*,audio/*,.mkv,.m4a,.mp3,.wav,.aac,.ogg"
          multiple
          class="admin-page__media-file-input"
          @change="handleMediaUpload"
        />
        <span v-if="mediaUploading" class="admin-page__media-status">
          正在上传 {{ mediaUploadProgress.done }}/{{ mediaUploadProgress.total }}
        </span>
        <span v-else-if="mediaUploadSuccess" class="admin-page__media-status admin-page__media-status--success">
          {{ mediaUploadSuccess }}
        </span>
        <span v-if="mediaUploadError" class="admin-page__media-status admin-page__media-status--error">
          {{ mediaUploadError }}
        </span>
      </div>

      <!-- 上传队列面板 -->
      <div v-if="uploadQueue.length" class="upload-queue">
        <div
          v-for="item in uploadQueue"
          :key="item.id"
          class="upload-queue__item"
          :class="`upload-queue__item--${item.status}`"
        >
          <span class="upload-queue__icon">
            <svg v-if="item.status === 'success'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="m20 6-11 11-5-5"/></svg>
            <svg v-else-if="item.status === 'error'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M18 6 6 18M6 6l12 12"/></svg>
            <svg v-else-if="item.status === 'uploading'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin-icon"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
            <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>
          </span>
          <span class="upload-queue__name">{{ item.name }}</span>
          <span class="upload-queue__size">{{ (item.size / 1024 / 1024).toFixed(1) }}MB</span>
          <span class="upload-queue__status">{{ item.status === 'pending' ? '等待中' : item.status === 'uploading' ? '上传中...' : item.status === 'success' ? '完成' : item.error }}</span>
        </div>
      </div>

      <div class="admin-page__media-toolbar__right">
        <template v-if="mediaSelectedIds.size > 0">
          <span class="admin-page__media-badge">已选 {{ mediaSelectedIds.size }} 项</span>
          <button
            class="admin-page__media-btn"
            :disabled="mediaSelectedIds.size !== 1"
            :title="mediaSelectedIds.size > 1 ? '只能选择一个媒体文件进行编辑' : '编辑'"
            @click="handleEditSelectedImage"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.1 2.1 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
            编辑
          </button>
          <button class="admin-page__media-btn admin-page__media-btn--danger" @click="handleDeleteSelectedImages">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
              <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
            删除
          </button>
          <button class="admin-page__media-btn" @click="mediaSelectAll">全选</button>
          <button class="admin-page__media-btn" @click="mediaSelectedIds = new Set()">取消</button>
        </template>
      </div>
    </div>

    <div v-if="!mediaLoaded" class="admin-page__loading">加载中...</div>
    <div v-else-if="!mediaItems.length" class="admin-page__loading">暂无媒体文件</div>
    <div v-else class="media-explorer">
      <!-- 左侧文件夹树 -->
      <aside class="media-sidebar">
        <div class="media-sidebar__header">文件夹</div>
        <button
          class="media-folder"
          :class="{ active: currentTypeFilter === 'all' }"
          @click="currentTypeFilter = 'all'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
          <span class="media-folder__name">全部文件</span>
          <span class="media-folder__count">{{ mediaItems.length }}</span>
        </button>
        <button
          v-if="typeCount('image') > 0"
          class="media-folder"
          :class="{ active: currentTypeFilter === 'image' }"
          @click="currentTypeFilter = 'image'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>
          <span class="media-folder__name">图片</span>
          <span class="media-folder__count">{{ typeCount('image') }}</span>
        </button>
        <button
          v-if="typeCount('video') > 0"
          class="media-folder"
          :class="{ active: currentTypeFilter === 'video' }"
          @click="currentTypeFilter = 'video'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>
          <span class="media-folder__name">视频</span>
          <span class="media-folder__count">{{ typeCount('video') }}</span>
        </button>
        <button
          v-if="typeCount('audio') > 0"
          class="media-folder"
          :class="{ active: currentTypeFilter === 'audio' }"
          @click="currentTypeFilter = 'audio'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
          <span class="media-folder__name">音乐</span>
          <span class="media-folder__count">{{ typeCount('audio') }}</span>
        </button>
      </aside>

      <!-- 右侧文件列表 -->
      <div class="media-content">
        <!-- 面包屑 -->
        <div class="media-breadcrumb">
          <span class="media-breadcrumb__root" @click="currentTypeFilter = 'all'">媒体库</span>
          <template v-if="currentTypeFilter !== 'all'">
            <span class="media-breadcrumb__sep">/</span>
            <span class="media-breadcrumb__current">{{ folderLabel }}</span>
          </template>
          <span class="media-breadcrumb__count">{{ filteredMediaItems.length }} 个文件</span>
        </div>

        <!-- 文件网格 -->
        <div class="admin-page__media-grid">
        <div
          v-for="item in filteredMediaItems"
          :key="item.id"
          class="admin-page__media-card"
          :class="{ 'admin-page__media-card--selected': mediaSelectedIds.has(item.id), 'admin-page__media-card--editing': editingImgName?.id === item.id }"
        >
        <div class="admin-page__media-img-wrap">
          <button
            type="button"
            class="admin-page__media-select"
            :class="{ 'admin-page__media-select--active': mediaSelectedIds.has(item.id) }"
            :title="mediaSelectedIds.has(item.id) ? '取消选择' : '选择媒体'"
            @click.stop="toggleMediaSelect(item.id)"
          >
            <svg v-if="mediaSelectedIds.has(item.id)" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <path d="m20 6-11 11-5-5" />
            </svg>
          </button>

          <button type="button" class="admin-page__media-img-button" :title="`查看 ${item.filename}`" @click="openPreview(item)">
            <img
              v-if="isImage(item)"
              v-show="!mediaBrokenIds.has(item.id)"
              :src="mediaUrl(item.url)"
              :alt="item.filename"
              class="admin-page__media-img"
              loading="lazy"
              @load="clearMediaBroken(item.id)"
              @error="markMediaBroken(item.id)"
            />
            <video
              v-else-if="isVideo(item)"
              v-show="!mediaBrokenIds.has(item.id)"
              :src="mediaUrl(item.url)"
              class="admin-page__media-img"
              muted
              preload="metadata"
              @loadedmetadata="clearMediaBroken(item.id)"
              @error="markMediaBroken(item.id)"
            />
            <div v-else-if="isAudio(item)" class="admin-page__media-audio-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 18V5l12-2v13" />
                <circle cx="6" cy="18" r="3" />
                <circle cx="18" cy="16" r="3" />
              </svg>
              <span class="admin-page__media-audio-ext">{{ item.filename.split('.').pop()?.toUpperCase() }}</span>
            </div>
            <span v-else class="admin-page__media-img-error">不支持预览</span>
            <span v-if="mediaBrokenIds.has(item.id)" class="admin-page__media-img-error">媒体加载失败</span>
            <span class="admin-page__media-type">{{ mediaLabel(item) }}</span>
            <span class="admin-page__media-preview-hint">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            </span>
          </button>
        </div>

        <div class="admin-page__media-info">
          <template v-if="editingImgName?.id === item.id">
            <input
              v-model="editingImgName.filename"
              class="admin-input admin-input--inline"
              @keyup.enter="handleSaveImageName(item.id)"
              @keyup.escape="editingImgName = null"
            />
            <div class="admin-page__media-edit-actions">
              <button class="admin-btn admin-btn--edit" @click="handleSaveImageName(item.id)">保存</button>
              <button class="admin-btn" @click="editingImgName = null">取消</button>
            </div>
          </template>
          <template v-else>
            <span class="admin-page__media-name" :title="item.filename">{{ item.filename }}</span>
            <span class="admin-page__media-meta">
              <span class="admin-page__media-size">{{ formatSize(item.size) }}</span>
              <span v-if="item.uploaded_by" class="admin-page__media-uploader">{{ item.uploaded_by }}</span>
            </span>
          </template>
        </div>
        </div>
      </div>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="previewImage" class="admin-page__media-modal-overlay" @click.self="previewImage = null">
          <div class="admin-page__preview-modal">
            <img
              v-if="isImage(previewImage)"
              :src="mediaUrl(previewImage.url)"
              :alt="previewImage.filename"
              class="admin-page__preview-img"
            />
            <video
              v-else-if="isVideo(previewImage)"
              :src="mediaUrl(previewImage.url)"
              class="admin-page__preview-video"
              controls
              autoplay
            />
            <div v-else-if="isAudio(previewImage)" class="admin-page__preview-audio">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                <path d="M9 18V5l12-2v13" />
                <circle cx="6" cy="18" r="3" />
                <circle cx="18" cy="16" r="3" />
              </svg>
              <audio :src="mediaUrl(previewImage.url)" controls autoplay />
            </div>
            <div class="admin-page__preview-info">
              <span>{{ previewImage.filename }}</span>
              <span class="admin-page__preview-meta">{{ formatSize(previewImage.size) }}</span>
              <a :href="mediaUrl(previewImage.url)" target="_blank" rel="noopener" class="admin-page__preview-link">打开原文件</a>
            </div>
            <button class="admin-page__preview-close" @click="previewImage = null">&times;</button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { getImages, deleteImage, updateImage, uploadImage, type ImageItem } from '@/api/admin'
import { safeCall } from '@/api/http'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()

const mediaItems = ref<ImageItem[]>([])
const currentTypeFilter = ref<string>('all')

function typeCount(type: string): number {
  return mediaItems.value.filter(i => {
    if (type === 'image') return isImage(i)
    if (type === 'video') return isVideo(i)
    if (type === 'audio') return isAudio(i)
    return false
  }).length
}

const folderLabel = computed(() => {
  if (currentTypeFilter.value === 'image') return '图片'
  if (currentTypeFilter.value === 'video') return '视频'
  if (currentTypeFilter.value === 'audio') return '音乐'
  return ''
})
const mediaLoaded = ref(false)
const currentUploaderFilter = ref('all')

const mediaByUploader = computed(() => {
  const groups: Record<string, ImageItem[]> = {}
  for (const item of mediaItems.value) {
    const uploader = item.uploaded_by || 'unknown'
    if (!groups[uploader]) groups[uploader] = []
    groups[uploader].push(item)
  }
  return groups
})

const filteredMediaItems = computed(() => {
  let items = mediaItems.value
  // 类型筛选
  if (currentTypeFilter.value !== 'all') {
    items = items.filter(i => {
      if (currentTypeFilter.value === 'image') return isImage(i)
      if (currentTypeFilter.value === 'video') return isVideo(i)
      if (currentTypeFilter.value === 'audio') return isAudio(i)
      return true
    })
  }
  // 上传者筛选
  if (currentUploaderFilter.value !== 'all') {
    return mediaByUploader.value[currentUploaderFilter.value] || []
  }
  return items
})
const mediaUploading = ref(false)
const mediaUploadError = ref('')
const mediaUploadSuccess = ref('')
const mediaUploadProgress = ref({ done: 0, total: 0 })
const uploadQueue = ref<{ id: number; name: string; size: number; status: 'pending' | 'uploading' | 'success' | 'error'; error: string }[]>([])
const mediaFileInput = ref<HTMLInputElement | null>(null)
const mediaSelectedIds = ref<Set<number>>(new Set())
const mediaBrokenIds = ref<Set<number>>(new Set())
const previewImage = ref<ImageItem | null>(null)
const editingImgName = ref<{ id: number; filename: string } | null>(null)

function isImage(item: ImageItem) {
  return item.media_type === 'image' || item.mime_type?.startsWith('image/')
}

function isVideo(item: ImageItem) {
  return item.media_type === 'video' || item.mime_type?.startsWith('video/')
}

function isAudio(item: ImageItem) {
  return item.media_type === 'music' || item.media_type === 'audio' || item.mime_type?.startsWith('audio/')
}

function mediaLabel(item: ImageItem) {
  if (isVideo(item)) return 'VIDEO'
  if (isAudio(item)) return 'AUDIO'
  return 'IMAGE'
}

function isAllowedMedia(file: File) {
  return file.type.startsWith('image/') || file.type.startsWith('video/') || file.type.startsWith('audio/') ||
    file.name.toLowerCase().endsWith('.mkv') || file.name.toLowerCase().endsWith('.m4a') ||
    file.name.toLowerCase().endsWith('.mp3') || file.name.toLowerCase().endsWith('.wav') ||
    file.name.toLowerCase().endsWith('.aac') || file.name.toLowerCase().endsWith('.ogg')
}

function handleEditSelectedImage() {
  if (mediaSelectedIds.value.size !== 1) return
  const id = [...mediaSelectedIds.value][0]
  const item = mediaItems.value.find(i => i.id === id)
  if (item) editingImgName.value = { id: item.id, filename: item.filename }
}

async function loadMedia() {
  mediaLoaded.value = false
  mediaItems.value = await safeCall(() => getImages(), [])
  mediaBrokenIds.value = new Set()
  mediaLoaded.value = true
}

function triggerMediaUpload() {
  mediaFileInput.value?.click()
}

async function handleMediaUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const selectedFiles = Array.from(target.files || [])
  if (!selectedFiles.length) return

  const mediaFiles = selectedFiles.filter(isAllowedMedia)
  if (!mediaFiles.length) {
    mediaUploadError.value = '请选择图片或视频文件'
    target.value = ''
    return
  }

  mediaUploading.value = true
  mediaUploadError.value = ''
  mediaUploadSuccess.value = ''

  // 构建上传队列
  uploadQueue.value = mediaFiles.map((f, i) => ({
    id: i,
    name: f.name,
    size: f.size,
    status: 'pending' as 'pending' | 'uploading' | 'success' | 'error',
    error: '',
  }))

  const failures: string[] = []
  try {
    for (let i = 0; i < mediaFiles.length; i++) {
      const file = mediaFiles[i]
      // 标记当前文件为上传中
      uploadQueue.value[i].status = 'uploading'

      try {
        await uploadImage(file)
        uploadQueue.value[i].status = 'success'
      } catch (e: any) {
        const status = e?.response?.status
        let reason: string
        if (status === 401) reason = '登录已过期'
        else if (status === 413) reason = '文件过大'
        else if (status === 415) reason = '格式不支持'
        else reason = e?.response?.data?.detail || e?.message || '上传失败'
        uploadQueue.value[i].status = 'error'
        uploadQueue.value[i].error = reason
        failures.push(`${file.name}: ${reason}`)
      }
    }

    await loadMedia()

    const successCount = mediaFiles.length - failures.length
    const skipped = selectedFiles.length - mediaFiles.length
    if (failures.length) {
      mediaUploadError.value = `${successCount} 个上传成功，${failures.length} 个失败${skipped ? `，${skipped} 个不支持的文件已跳过` : ''}`
    } else {
      mediaUploadSuccess.value = mediaFiles.length === 1 ? '上传成功' : `已上传 ${mediaFiles.length} 个媒体文件`
      if (skipped) mediaUploadError.value = `${skipped} 个不支持的文件已跳过`
    }
  } finally {
    mediaUploading.value = false
    mediaUploadProgress.value = { done: mediaFiles.length, total: mediaFiles.length }
    target.value = ''
    // 3 秒后清空队列显示
    setTimeout(() => { uploadQueue.value = [] }, 3000)
  }
}

function toggleMediaSelect(id: number) {
  if (mediaSelectedIds.value.has(id)) {
    mediaSelectedIds.value.delete(id)
  } else {
    mediaSelectedIds.value.add(id)
  }
  mediaSelectedIds.value = new Set(mediaSelectedIds.value)
}

function mediaSelectAll() {
  mediaSelectedIds.value = new Set(mediaItems.value.map(item => item.id))
}

function openPreview(item: ImageItem) {
  previewImage.value = item
}

function markMediaBroken(id: number) {
  const next = new Set(mediaBrokenIds.value)
  next.add(id)
  mediaBrokenIds.value = next
}

function clearMediaBroken(id: number) {
  if (!mediaBrokenIds.value.has(id)) return
  const next = new Set(mediaBrokenIds.value)
  next.delete(id)
  mediaBrokenIds.value = next
}

async function handleDeleteSelectedImages() {
  const ids = [...mediaSelectedIds.value]
  if (!ids.length) return
  await Promise.allSettled(ids.map(id => deleteImage(id)))
  mediaItems.value = mediaItems.value.filter(item => !mediaSelectedIds.value.has(item.id))
  mediaSelectedIds.value = new Set()
}

async function handleSaveImageName(id: number) {
  if (!editingImgName.value) return
  const filename = editingImgName.value.filename.trim()
  if (!filename) return
  try {
    await updateImage(id, { filename })
    editingImgName.value = null
    mediaSelectedIds.value = new Set()
    await loadMedia()
  } catch {
    toast.error('保存媒体名称失败，请稍后重试')
  }
}

function mediaUrl(url: string) {
  if (url.startsWith('http') || url.startsWith('data:') || url.startsWith('blob:')) return url
  if (url.startsWith('/api/') || url.startsWith('/uploads/')) return url
  const base = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
  return `${base}${url.startsWith('/') ? url : `/${url}`}`
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

loadMedia()
</script>

<style scoped>
.admin-page__media-toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
  padding: var(--space-sm) var(--space-md);
  background: var(--glass-surface-bg);
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  backdrop-filter: var(--glass-card-blur);
}

.admin-page__media-toolbar__left {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.admin-page__media-toolbar__right {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-left: auto;
  flex-wrap: wrap;
}

.admin-page__media-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  font-weight: 500;
  padding: 7px 14px;
  border: 1px solid var(--glass-bg-12);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  background: transparent;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  white-space: nowrap;
}

.admin-page__media-btn:hover {
  color: var(--color-text);
  border-color: var(--border-heavy);
  background: var(--glass-bg-04);
}

.admin-page__media-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  pointer-events: none;
}

.admin-page__media-btn--primary {
  color: var(--color-accent);
  border-color: var(--accent-tint-35);
  background: var(--accent-tint-08);
}

.admin-page__media-btn--primary:hover {
  background: var(--accent-tint-18);
  border-color: var(--accent-tint-50);
}

.admin-page__media-btn--danger {
  color: #f87171;
  border-color: var(--error-border-30);
  background: var(--error-bg-06);
}

.admin-page__media-btn--danger:hover {
  background: var(--error-bg-15);
  border-color: var(--error-border-40);
}

.admin-page__media-file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

.admin-page__media-status {
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.admin-page__media-status--success {
  color: #10b981;
}

.admin-page__media-status--error {
  color: #f87171;
}

.admin-page__media-badge {
  font-size: 0.72rem;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  background: var(--accent-tint-12);
  color: var(--color-accent);
  border: 1px solid var(--accent-tint-25);
}

.admin-page__media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: var(--space-md);
}

.admin-page__media-card {
  background: var(--glass-surface-bg);
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: all var(--duration-fast) ease;
}

.admin-page__media-card:hover {
  border-color: var(--accent-tint-30);
}

.admin-page__media-card--selected {
  border-color: var(--accent-tint-60);
  box-shadow: 0 0 0 2px var(--accent-tint-20);
}

.admin-page__media-card--editing {
  border-color: var(--accent-tint-40);
}

.admin-page__media-img-wrap {
  position: relative;
}

.admin-page__media-img-button {
  position: relative;
  display: block;
  width: 100%;
  height: 126px;
  padding: 0;
  border: 0;
  background: var(--glass-bg-04);
  color: inherit;
  cursor: zoom-in;
  overflow: hidden;
  text-align: left;
}

.admin-page__media-img {
  width: 100%;
  height: 126px;
  object-fit: cover;
  display: block;
}

.admin-page__media-img-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 126px;
  padding: var(--space-sm);
  color: var(--color-text-muted);
  font-size: 0.78rem;
  background: var(--glass-bg-06);
}

.admin-page__media-select {
  position: absolute;
  top: 6px;
  left: 6px;
  z-index: 2;
  width: 24px;
  height: 24px;
  padding: 0;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(4px);
  border: 1.5px solid var(--border-heavy);
  color: var(--text-overlay-30);
  transition: all var(--duration-fast) ease;
  cursor: pointer;
}

.admin-page__media-select:hover {
  border-color: var(--text-overlay-45);
  color: var(--text-overlay-50);
  background: rgba(0, 0, 0, 0.5);
}

.admin-page__media-select--active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #fff;
}

.admin-page__media-type {
  position: absolute;
  left: 8px;
  bottom: 8px;
  padding: 3px 7px;
  border-radius: var(--radius-sm);
  background: rgba(0, 0, 0, 0.55);
  color: var(--text-overlay-60);
  font-family: var(--font-mono);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.admin-page__media-preview-hint {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  color: var(--text-overlay-60);
  opacity: 0;
  transition: all var(--duration-fast) ease;
}

.admin-page__media-card:hover .admin-page__media-preview-hint,
.admin-page__media-img-button:focus-visible .admin-page__media-preview-hint {
  background: var(--accent-tint-50);
  color: #fff;
  opacity: 1;
}

.admin-page__media-info {
  padding: var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.admin-page__media-name {
  font-size: 0.72rem;
  color: var(--color-text-soft);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.admin-page__media-size {
  font-size: 0.68rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

.admin-page__media-edit-actions {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.admin-page__media-edit-actions .admin-btn {
  color: var(--color-text-soft);
}

.admin-page__media-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 120;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
  background: rgba(0, 0, 0, 0.68);
  backdrop-filter: blur(18px);
}

.admin-page__preview-modal {
  position: relative;
  max-width: 92vw;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.admin-page__preview-img,
.admin-page__preview-video {
  max-width: 90vw;
  max-height: 80vh;
  object-fit: contain;
  border-radius: var(--radius-md);
}

.admin-page__preview-video {
  background: #000;
}

.admin-page__preview-info {
  margin-top: var(--space-sm);
  font-size: 0.85rem;
  color: var(--color-text-soft);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
  justify-content: center;
}

.admin-page__preview-meta {
  color: var(--color-text-muted);
  font-size: 0.78rem;
}

.admin-page__preview-link {
  color: var(--color-accent);
  font-size: 0.78rem;
  text-decoration: none;
}

.admin-page__preview-link:hover {
  text-decoration: underline;
}

.admin-page__preview-close {
  position: absolute;
  top: -12px;
  right: -12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid var(--border-strong);
  background: var(--modal-bg);
  color: var(--color-text);
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) ease;
}

.admin-page__preview-close:hover {
  background: var(--error-bg-20);
  border-color: var(--error-border-40);
  color: #f87171;
}

@media (max-width: 760px) {
  .admin-page__media-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .admin-page__media-toolbar__right {
    margin-left: 0;
  }
}

.media-filter-bar {
  display: flex;
  gap: 6px;
  margin-bottom: var(--space-md);
  flex-wrap: wrap;
}

.media-filter-btn {
  padding: 4px 14px;
  background: transparent;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  color: var(--color-text-soft);
  font-size: 0.78rem;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.media-filter-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-text);
}

.media-filter-btn.active {
  background: var(--accent-tint-12);
  border-color: var(--accent-tint-25);
  color: var(--color-accent);
  font-weight: 500;
}

.admin-page__media-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.admin-page__media-uploader {
  font-size: 0.62rem;
  color: var(--color-text-muted);
  padding: 1px 6px;
  border-radius: var(--radius-full);
  background: var(--glass-bg-08);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 120px;
}

/* 类型筛选 Tab — 旧样式已废弃 */

/* 上传队列 */
.upload-queue {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 260px;
  overflow-y: auto;
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--glass-surface-bg);
}

.upload-queue__item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.6rem;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  background: var(--glass-card-bg);
  transition: all var(--duration-fast) ease;
}

.upload-queue__item--uploading {
  border-left: 3px solid var(--color-accent);
}

.upload-queue__item--success {
  opacity: 0.7;
  border-left: 3px solid var(--success-main);
}

.upload-queue__item--error {
  border-left: 3px solid var(--error-main);
}

.upload-queue__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.upload-queue__item--success .upload-queue__icon { color: var(--success-main); }
.upload-queue__item--error .upload-queue__icon { color: var(--error-main); }
.upload-queue__item--uploading .upload-queue__icon { color: var(--color-accent); }
.upload-queue__item--pending .upload-queue__icon { color: var(--color-text-muted); }

.spin-icon {
  animation: spin 1s linear infinite;
}

.upload-queue__name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-text);
}

.upload-queue__size {
  color: var(--color-text-muted);
  font-size: 0.7rem;
  white-space: nowrap;
}

.upload-queue__status {
  font-size: 0.7rem;
  white-space: nowrap;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.upload-queue__item--uploading .upload-queue__status { color: var(--color-accent); }
.upload-queue__item--success .upload-queue__status { color: var(--success-main); }
.upload-queue__item--error .upload-queue__status { color: var(--error-main); }
.upload-queue__item--pending .upload-queue__status { color: var(--color-text-muted); }

/* 文件管理器布局 */
.media-explorer {
  display: flex;
  gap: 0;
  min-height: 400px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.media-sidebar {
  width: 200px;
  min-width: 200px;
  border-right: 1px solid var(--border-default);
  padding: 0.5rem 0;
  background: var(--glass-surface-bg);
}

.media-sidebar__header {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  padding: 0.5rem 1rem;
}

.media-folder {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  color: var(--color-text-soft);
  background: none;
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  text-align: left;
}

.media-folder:hover {
  background: var(--glass-bg-08);
  color: var(--color-text);
}

.media-folder.active {
  background: var(--accent-tint-06);
  color: var(--color-accent);
  border-left: 3px solid var(--color-accent);
  padding-left: calc(1rem - 3px);
}

.media-folder__name {
  flex: 1;
}

.media-folder__count {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  background: var(--glass-bg-12);
  padding: 1px 7px;
  border-radius: var(--radius-full);
}

.media-folder.active .media-folder__count {
  background: var(--accent-tint-15);
  color: var(--color-accent);
}

.media-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.media-breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  border-bottom: 1px solid var(--border-default);
  font-size: 0.8rem;
  background: var(--glass-card-bg);
}

.media-breadcrumb__root {
  cursor: pointer;
  color: var(--color-text-muted);
  transition: color var(--duration-fast) ease;
}

.media-breadcrumb__root:hover {
  color: var(--color-accent);
}

.media-breadcrumb__sep {
  color: var(--color-text-muted);
  opacity: 0.5;
}

.media-breadcrumb__current {
  color: var(--color-text-heading);
  font-weight: 500;
}

.media-breadcrumb__count {
  margin-left: auto;
  font-size: 0.7rem;
  color: var(--color-text-muted);
}

.admin-page__media-grid {
  padding: 1rem;
}

@media (max-width: 768px) {
  .media-explorer {
    flex-direction: column;
  }
  .media-sidebar {
    width: 100%;
    min-width: 0;
    border-right: none;
    border-bottom: 1px solid var(--border-default);
    display: flex;
    flex-wrap: wrap;
    padding: 0.5rem;
  }
  .media-sidebar__header {
    width: 100%;
  }
  .media-folder {
    width: auto;
    padding: 0.4rem 0.8rem;
  }
}

/* 音频卡片图标 */
.admin-page__media-audio-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  gap: 0.5rem;
  color: var(--color-accent);
  opacity: 0.6;
}

.admin-page__media-audio-ext {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

/* 音频预览弹窗 */
.admin-page__preview-audio {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
  color: var(--color-accent);
}

.admin-page__preview-audio audio {
  width: 100%;
  min-width: 300px;
}
</style>
