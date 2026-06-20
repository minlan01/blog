<template>
  <div class="admin-page__panel">
    <div class="admin-page__media-toolbar">
      <div class="admin-page__media-toolbar__left">
        <button class="admin-page__media-btn admin-page__media-btn--primary" :disabled="mediaUploading" @click="triggerMediaUpload">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          {{ mediaUploading ? '上传中...' : '选择图片' }}
        </button>
        <input ref="mediaFileInput" type="file" accept="image/*" multiple class="admin-page__media-file-input" @change="handleMediaUpload" />
        <span v-if="mediaUploading" class="admin-page__media-status">正在上传 {{ mediaUploadProgress.done }}/{{ mediaUploadProgress.total }}</span>
        <span v-else-if="mediaUploadSuccess" class="admin-page__media-status admin-page__media-status--success">{{ mediaUploadSuccess }}</span>
        <span v-if="mediaUploadError" class="admin-page__media-status admin-page__media-status--error">{{ mediaUploadError }}</span>
      </div>
      <div class="admin-page__media-toolbar__right">
        <template v-if="mediaSelectedIds.size > 0">
          <span class="admin-page__media-badge">已选 {{ mediaSelectedIds.size }} 项</span>
          <button class="admin-page__media-btn" :disabled="mediaSelectedIds.size !== 1" :title="mediaSelectedIds.size > 1 ? '只能选择一张图片进行编辑' : '编辑'" @click="handleEditSelectedImage">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            编辑
          </button>
          <button class="admin-page__media-btn admin-page__media-btn--danger" @click="handleDeleteSelectedImages">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            删除
          </button>
          <button class="admin-page__media-btn" @click="mediaSelectAll">全选</button>
          <button class="admin-page__media-btn" @click="mediaSelectedIds = new Set()">取消</button>
        </template>
      </div>
    </div>
    <div v-if="!mediaLoaded" class="admin-page__loading">加载中...</div>
    <div v-else-if="!mediaItems.length" class="admin-page__loading">暂无图片</div>
    <div v-else class="admin-page__media-grid">
      <div
        v-for="img in mediaItems"
        :key="img.id"
        class="admin-page__media-card"
        :class="{ 'admin-page__media-card--selected': mediaSelectedIds.has(img.id), 'admin-page__media-card--editing': editingImgName?.id === img.id }"
      >
        <div class="admin-page__media-img-wrap">
          <button
            type="button"
            class="admin-page__media-select"
            :class="{ 'admin-page__media-select--active': mediaSelectedIds.has(img.id) }"
            :title="mediaSelectedIds.has(img.id) ? '取消选择' : '选择图片'"
            @click.stop="toggleMediaSelect(img.id)"
          >
            <svg v-if="mediaSelectedIds.has(img.id)" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
          </button>
          <button type="button" class="admin-page__media-img-button" :title="`查看 ${img.filename}`" @click="openPreview(img)">
            <img
              v-show="!mediaBrokenIds.has(img.id)"
              :src="mediaUrl(img.url)"
              :alt="img.filename"
              class="admin-page__media-img"
              loading="lazy"
              @load="clearMediaBroken(img.id)"
              @error="markMediaBroken(img.id)"
            />
            <span v-if="mediaBrokenIds.has(img.id)" class="admin-page__media-img-error">图片加载失败</span>
            <span class="admin-page__media-preview-hint">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </span>
          </button>
        </div>
        <div class="admin-page__media-info">
          <template v-if="editingImgName?.id === img.id">
            <input v-model="editingImgName.filename" class="admin-input admin-input--inline" @keyup.enter="handleSaveImageName(img.id)" @keyup.escape="editingImgName = null" />
            <div class="admin-page__media-edit-actions">
              <button class="admin-btn admin-btn--edit" @click="handleSaveImageName(img.id)">保存</button>
              <button class="admin-btn" @click="editingImgName = null">取消</button>
            </div>
          </template>
          <template v-else>
            <span class="admin-page__media-name" :title="img.filename">{{ img.filename }}</span>
            <span class="admin-page__media-size">{{ formatSize(img.size) }}</span>
          </template>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="previewImage" class="admin-page__media-modal-overlay" @click.self="previewImage = null">
          <div class="admin-page__preview-modal">
            <img :src="mediaUrl(previewImage.url)" :alt="previewImage.filename" class="admin-page__preview-img" />
            <div class="admin-page__preview-info">
              <span>{{ previewImage.filename }}</span>
              <span style="color:var(--color-text-muted);font-size:0.78rem;margin-left:8px;">{{ formatSize(previewImage.size) }}</span>
              <a :href="mediaUrl(previewImage.url)" target="_blank" rel="noopener" class="admin-page__preview-link">打开原图</a>
            </div>
            <button class="admin-page__preview-close" @click="previewImage = null">&times;</button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getImages, deleteImage, updateImage, uploadImage, type ImageItem } from '@/api/admin'
import { safeCall } from '@/api/http'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()

const mediaItems = ref<ImageItem[]>([])
const mediaLoaded = ref(false)
const mediaUploading = ref(false)
const mediaUploadError = ref('')
const mediaUploadSuccess = ref('')
const mediaUploadProgress = ref({ done: 0, total: 0 })
const mediaFileInput = ref<HTMLInputElement | null>(null)
const mediaSelectedIds = ref<Set<number>>(new Set())
const mediaBrokenIds = ref<Set<number>>(new Set())
const previewImage = ref<ImageItem | null>(null)
const editingImgName = ref<{ id: number; filename: string } | null>(null)

function handleEditSelectedImage() {
  if (mediaSelectedIds.value.size !== 1) return
  const id = [...mediaSelectedIds.value][0]
  const img = mediaItems.value.find(i => i.id === id)
  if (img) editingImgName.value = { id: img.id, filename: img.filename }
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
  const imageFiles = selectedFiles.filter(file => file.type.startsWith('image/'))
  if (!selectedFiles.length) return
  if (!imageFiles.length) {
    mediaUploadError.value = '请选择图片文件'
    target.value = ''
    return
  }

  mediaUploading.value = true
  mediaUploadError.value = ''
  mediaUploadSuccess.value = ''
  mediaUploadProgress.value = { done: 0, total: imageFiles.length }

  const failures: string[] = []
  try {
    for (const file of imageFiles) {
      try {
        await uploadImage(file)
      } catch (e: any) {
        const reason = e?.response?.data?.detail || e?.message || '上传失败'
        failures.push(`${file.name}: ${reason}`)
      } finally {
        mediaUploadProgress.value = {
          done: mediaUploadProgress.value.done + 1,
          total: imageFiles.length,
        }
      }
    }

    await loadMedia()

    const skipped = selectedFiles.length - imageFiles.length
    if (failures.length) {
      const successCount = imageFiles.length - failures.length
      mediaUploadError.value = `${successCount} 张上传成功，${failures.length} 张失败${skipped ? `，${skipped} 个非图片文件已跳过` : ''}`
    } else {
      mediaUploadSuccess.value = imageFiles.length === 1 ? '上传成功' : `已上传 ${imageFiles.length} 张图片`
      if (skipped) mediaUploadError.value = `${skipped} 个非图片文件已跳过`
    }
  } finally {
    mediaUploading.value = false
    target.value = ''
  }
}

async function handleDeleteImage(id: number) {
  try {
    await deleteImage(id)
    mediaItems.value = mediaItems.value.filter(img => img.id !== id)
    mediaSelectedIds.value.delete(id)
  } catch {
    toast.error('删除图片失败，请稍后重试')
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
  mediaSelectedIds.value = new Set(mediaItems.value.map(img => img.id))
}

function openPreview(img: ImageItem) {
  previewImage.value = img
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
  mediaItems.value = mediaItems.value.filter(img => !mediaSelectedIds.value.has(img.id))
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
    toast.error('保存图片名失败，请稍后重试')
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
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
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
}

.admin-page__media-toolbar__right {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-left: auto;
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

.admin-page__media-btn--active {
  color: var(--color-accent);
  border-color: var(--accent-tint-50);
  background: var(--accent-tint-12);
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
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
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
  height: 120px;
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
  height: 120px;
  object-fit: cover;
  display: block;
}

.admin-page__media-img-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 120px;
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
  cursor: pointer;
}

.admin-page__media-card:hover .admin-page__media-preview-hint {
  opacity: 1;
}

.admin-page__media-img-button:hover .admin-page__media-preview-hint,
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
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.admin-page__preview-img {
  max-width: 90vw;
  max-height: 80vh;
  object-fit: contain;
  border-radius: var(--radius-md);
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
</style>
