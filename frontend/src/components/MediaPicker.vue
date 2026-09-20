<template>
  <Teleport to="body">
    <Transition name="picker-fade">
      <div v-if="visible" class="media-picker-overlay" @click.self="handleClose">
        <div class="media-picker">
          <header class="media-picker__header">
            <h3 class="media-picker__title">选择图片</h3>
            <button class="media-picker__close" @click="handleClose"><span>&times;</span></button>
          </header>

          <div class="media-picker__toolbar">
            <div class="media-picker__filter">
              <button
                v-for="f in filters"
                :key="f.key"
                class="media-picker__filter-btn"
                :class="{ active: currentFilter === f.key }"
                @click="currentFilter = f.key"
              >{{ f.label }}</button>
            </div>
            <span class="media-picker__count">{{ filteredItems.length }} 张图片</span>
          </div>

          <div v-if="loading" class="media-picker__loading">加载中...</div>
          <div v-else-if="!filteredItems.length" class="media-picker__empty">暂无图片</div>
          <div v-else class="media-picker__grid">
            <button
              v-for="item in filteredItems"
              :key="item.id"
              class="media-picker__item"
              :class="{ 'media-picker__item--selected': selectedId === item.id }"
              @click="selectItem(item)"
            >
              <img
                :src="fullUrl(item.url)"
                :alt="item.filename"
                class="media-picker__img"
                loading="lazy"
                @error="onImgError($event)"
              />
              <span v-if="selectedId === item.id" class="media-picker__check">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <path d="m20 6-11 11-5-5" />
                </svg>
              </span>
              <span class="media-picker__name">{{ item.filename }}</span>
            </button>
          </div>

          <footer class="media-picker__footer">
            <button class="media-picker__btn media-picker__btn--cancel" @click="handleClose">取消</button>
            <button
              class="media-picker__btn media-picker__btn--confirm"
              :disabled="!selectedId"
              @click="handleConfirm"
            >{{ confirmText || '确认选择' }}</button>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getImages, type ImageItem } from '@/api/admin'

const props = withDefaults(defineProps<{
  visible: boolean
  confirmText?: string
  acceptType?: 'image' | 'all'
}>(), {
  confirmText: '确认选择',
  acceptType: 'image',
})

const emit = defineEmits<{
  (e: 'update:visible', val: boolean): void
  (e: 'select', item: ImageItem): void
}>()

const items = ref<ImageItem[]>([])
const loading = ref(false)
const selectedId = ref<number | null>(null)
const selectedItem = ref<ImageItem | null>(null)
const currentFilter = ref('all')

const filters = [
  { key: 'all', label: '全部' },
  { key: 'image', label: '图片' },
]

function isImage(item: ImageItem): boolean {
  return item.media_type === 'image' || (item.mime_type?.startsWith('image/') ?? false)
}

const filteredItems = computed(() => {
  if (currentFilter.value === 'image' || props.acceptType === 'image') {
    return items.value.filter(isImage)
  }
  return items.value
})

async function loadImages() {
  loading.value = true
  try {
    items.value = await getImages()
  } catch {
    // silent fail
  } finally {
    loading.value = false
  }
}

function fullUrl(url: string): string {
  if (url.startsWith('http') || url.startsWith('data:') || url.startsWith('blob:')) return url
  if (url.startsWith('/api/') || url.startsWith('/uploads/')) return url
  const base = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
  return `${base}${url.startsWith('/') ? url : `/${url}`}`
}

function selectItem(item: ImageItem) {
  if (selectedId.value === item.id) {
    selectedId.value = null
    selectedItem.value = null
  } else {
    selectedId.value = item.id
    selectedItem.value = item
  }
}

function handleConfirm() {
  if (selectedItem.value) {
    emit('select', selectedItem.value)
    handleClose()
  }
}

function handleClose() {
  emit('update:visible', false)
}

function onImgError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

watch(() => props.visible, (val) => {
  if (val) {
    selectedId.value = null
    selectedItem.value = null
    currentFilter.value = props.acceptType === 'image' ? 'image' : 'all'
    loadImages()
  }
})
</script>

<style scoped>
.media-picker-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(12px);
}

.media-picker {
  width: 100%;
  max-width: 860px;
  max-height: 82vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
  overflow: hidden;
}

.media-picker__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--glass-card-bg);
}

.media-picker__title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.media-picker__close {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text-muted);
  font-size: 1.4rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.media-picker__close:hover {
  background: var(--error-bg-12);
  color: #f87171;
}

.media-picker__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
}

.media-picker__filter {
  display: flex;
  gap: 4px;
}

.media-picker__filter-btn {
  padding: 4px 14px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  background: transparent;
  color: var(--color-text-soft);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.media-picker__filter-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-text);
}

.media-picker__filter-btn.active {
  background: var(--accent-tint-12);
  border-color: var(--accent-tint-25);
  color: var(--color-accent);
  font-weight: 500;
}

.media-picker__count {
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

.media-picker__loading,
.media-picker__empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 240px;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.media-picker__grid {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  max-height: 50vh;
}

.media-picker__item {
  position: relative;
  aspect-ratio: 1;
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  background: var(--glass-bg-04);
  padding: 0;
  transition: all 0.15s ease;
}

.media-picker__item:hover {
  border-color: var(--accent-tint-30);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.media-picker__item--selected {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px var(--accent-tint-20), 0 4px 12px rgba(0, 0, 0, 0.15);
}

.media-picker__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.media-picker__check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--color-accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
}

.media-picker__name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 6px 8px;
  font-size: 0.7rem;
  color: #fff;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  pointer-events: none;
}

.media-picker__footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border);
  background: var(--glass-card-bg);
}

.media-picker__btn {
  padding: 0.55rem 1.4rem;
  border-radius: var(--radius-md);
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid var(--color-border);
}

.media-picker__btn--cancel {
  background: transparent;
  color: var(--color-text-soft);
}

.media-picker__btn--cancel:hover {
  background: var(--glass-surface-bg);
  color: var(--color-text);
}

.media-picker__btn--confirm {
  background: var(--color-accent);
  color: #fff;
  border-color: var(--color-accent);
}

.media-picker__btn--confirm:hover:not(:disabled) {
  opacity: 0.9;
  filter: brightness(1.05);
}

.media-picker__btn--confirm:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.picker-fade-enter-active,
.picker-fade-leave-active {
  transition: all 0.25s ease;
}

.picker-fade-enter-from,
.picker-fade-leave-to {
  opacity: 0;
}

.picker-fade-enter-from .media-picker,
.picker-fade-leave-to .media-picker {
  transform: scale(0.96) translateY(10px);
}
</style>
