<template>
  <div class="admin-page__panel">
    <div class="admin-page__media-toolbar">
      <div class="admin-page__media-toolbar__left">
        <button class="admin-page__media-btn admin-page__media-btn--primary" @click="triggerMediaUpload">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          选择文件
        </button>
        <input ref="mediaFileInput" type="file" accept="image/*" style="position:absolute;width:0;height:0;opacity:0;pointer-events:none;" @change="handleMediaUpload" />
        <span v-if="mediaUploading" class="admin-page__media-status">上传中...</span>
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
        <div class="admin-page__media-img-wrap" @click="toggleMediaSelect(img.id)">
          <img :src="mediaUrl(img.url)" :alt="img.filename" class="admin-page__media-img" />
          <span class="admin-page__media-check-mark">
            <svg v-if="mediaSelectedIds.has(img.id)" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
          </span>
          <span class="admin-page__media-preview-hint" @click.stop="previewImage = img">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          </span>
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
        <div v-if="previewImage" class="modal-overlay" @click.self="previewImage = null">
          <div class="admin-page__preview-modal">
            <img :src="mediaUrl(previewImage.url)" class="admin-page__preview-img" />
            <div class="admin-page__preview-info">
              <span>{{ previewImage.filename }}</span>
              <span style="color:var(--color-text-muted);font-size:0.78rem;margin-left:8px;">{{ formatSize(previewImage.size) }}</span>
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
import { getImages, deleteImage, updateImage, type ImageItem } from '@/api/admin'
import { safeCall } from '@/api/http'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()

const mediaItems = ref<ImageItem[]>([])
const mediaLoaded = ref(false)
const mediaUploading = ref(false)
const mediaUploadError = ref('')
const mediaFileInput = ref<HTMLInputElement | null>(null)
const mediaSelectedIds = ref<Set<number>>(new Set())
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
  mediaLoaded.value = true
}

function triggerMediaUpload() {
  mediaFileInput.value?.click()
}

async function handleMediaUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  mediaUploading.value = true
  mediaUploadError.value = ''
  try {
    const formData = new FormData()
    formData.append('file', file)
    const { http } = await import('@/api/http')
    await http.post('/upload', formData)
    await loadMedia()
  } catch (e: any) {
    mediaUploadError.value = e?.response?.data?.detail || e?.message || '上传失败'
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
  return url.startsWith('http') ? url : '/api/v1' + url
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

.admin-page__media-status {
  font-size: 0.82rem;
  color: var(--color-text-muted);
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
  cursor: pointer;
}

.admin-page__media-img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
}

.admin-page__media-check-mark {
  position: absolute;
  top: 6px;
  left: 6px;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(4px);
  border: 1.5px solid var(--border-heavy);
  color: var(--text-overlay-30);
  transition: all var(--duration-fast) ease;
  pointer-events: none;
}

.admin-page__media-card:hover .admin-page__media-check-mark {
  border-color: var(--text-overlay-45);
  color: var(--text-overlay-50);
}

.admin-page__media-card--selected .admin-page__media-check-mark {
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

.admin-page__media-preview-hint:hover {
  background: var(--accent-tint-50);
  color: #fff;
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
