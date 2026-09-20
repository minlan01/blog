<template>
  <div class="search-bar" :class="{ 'search-bar--open': showDropdown }">
    <svg class="search-bar__icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input
      v-model="query"
      class="search-bar__input"
      type="text"
      :placeholder="placeholder"
      aria-label="搜索文章"
      @input="onInput"
      @keyup.enter="onSearch"
      @focus="onFocus"
      @blur="onBlur"
    />
    <button v-if="query" class="search-bar__clear" @click="clear" aria-label="清除">×</button>
    <button class="search-bar__btn" @click="onSearch">
      搜索
    </button>

    <!-- 实时搜索预览下拉 -->
    <Transition name="search-dropdown">
      <div v-if="showDropdown && (suggestions.length > 0 || searched)" class="search-bar__dropdown">
        <div v-if="loading" class="search-bar__loading">
          <span class="search-bar__spinner"></span> 搜索中...
        </div>
        <div v-else-if="suggestions.length === 0 && searched" class="search-bar__empty">
          没有找到相关文章
        </div>
        <ul v-else class="search-bar__results">
          <li
            v-for="item in suggestions"
            :key="item.id"
            class="search-bar__result"
            @mousedown.prevent="goToPost(item.slug)"
          >
            <div class="search-bar__result-title" v-html="item.title_snippet"></div>
            <div v-if="!item.title_snippet" class="search-bar__result-title">{{ item.title }}</div>
            <div v-if="item.content_snippet" class="search-bar__result-snippet" v-html="item.content_snippet"></div>
          </li>
        </ul>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { http } from '@/api/http'

interface SearchSuggestion {
  id: number
  title: string
  slug: string
  title_snippet?: string
  content_snippet?: string
  cover_image?: string
}

const props = withDefaults(defineProps<{
  placeholder?: string
}>(), {
  placeholder: '搜索文章...',
})

const emit = defineEmits<{
  (e: 'search', query: string): void
}>()

const router = useRouter()
const query = ref('')
const suggestions = ref<SearchSuggestion[]>([])
const loading = ref(false)
const showDropdown = ref(false)
const searched = ref(false)
const isFocused = ref(false)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

async function fetchSuggestions(q: string) {
  if (!q.trim()) {
    suggestions.value = []
    searched.value = false
    return
  }
  loading.value = true
  searched.value = true
  try {
    const resp = await http.get('/posts', {
      params: { search: q, per_page: 8 },
    })
    suggestions.value = resp.data.items || []
  } catch {
    suggestions.value = []
  } finally {
    loading.value = false
  }
}

function onInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  if (!query.value.trim()) {
    suggestions.value = []
    searched.value = false
    return
  }
  debounceTimer = setTimeout(() => {
    fetchSuggestions(query.value)
  }, 250)
}

function onSearch() {
  if (!query.value.trim()) return
  showDropdown.value = false
  emit('search', query.value)
}

function onFocus() {
  isFocused.value = true
  if (query.value.trim()) {
    showDropdown.value = true
  }
}

function onBlur() {
  isFocused.value = false
  // 延迟关闭让 click 事件先触发
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

function clear() {
  query.value = ''
  suggestions.value = []
  searched.value = false
}

function goToPost(slug: string) {
  showDropdown.value = false
  router.push(`/posts/${slug}`)
}

// Ctrl+K / Cmd+K 全局快捷键
function onKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    const input = document.querySelector('.search-bar__input') as HTMLInputElement
    if (input) input.focus()
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<style scoped>
.search-bar {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  overflow: visible;
  transition: all var(--duration-fast) ease;
}

.search-bar:focus-within {
  border-color: var(--color-accent);
  box-shadow: 0 0 8px var(--accent-tint-08);
}

.search-bar--open {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.search-bar__icon {
  flex-shrink: 0;
  color: var(--color-text-muted);
  margin-left: var(--space-md);
  pointer-events: none;
}

.search-bar__input {
  flex: 1;
  padding: 10px var(--space-sm);
  border: none;
  background: transparent;
  color: var(--color-text);
  font-size: 0.85rem;
  outline: none;
  min-width: 0;
}

.search-bar__input::placeholder {
  color: var(--color-text-muted);
  opacity: 0.5;
}

.search-bar__clear {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  background: var(--color-border);
  color: var(--color-text-muted);
  font-size: 0.9rem;
  cursor: pointer;
  margin-right: 4px;
  transition: background var(--duration-fast) ease;
}

.search-bar__clear:hover {
  background: var(--color-accent);
  color: var(--color-bg);
}

.search-bar__btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 14px;
  font-size: 0.78rem;
  color: var(--color-text-muted);
  transition: all var(--duration-fast) ease;
  border: none;
  background: transparent;
  cursor: pointer;
}

.search-bar__btn:hover {
  color: var(--color-accent);
}

/* 下拉预览 */
.search-bar__dropdown {
  position: absolute;
  top: 100%;
  left: -1px;
  right: -1px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-top: none;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  max-height: 400px;
  overflow-y: auto;
  z-index: 100;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.search-bar__loading,
.search-bar__empty {
  padding: var(--space-md);
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.search-bar__spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.search-bar__results {
  list-style: none;
  padding: 0;
  margin: 0;
}

.search-bar__result {
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  transition: background var(--duration-fast) ease;
  border-bottom: 1px solid var(--color-border-subtle, rgba(128, 128, 128, 0.1));
}

.search-bar__result:last-child {
  border-bottom: none;
}

.search-bar__result:hover {
  background: var(--color-surface-hover, rgba(128, 128, 128, 0.08));
}

.search-bar__result-title {
  font-size: 0.85rem;
  color: var(--color-text);
  margin-bottom: 2px;
  line-height: 1.4;
}

.search-bar__result-title :deep(mark) {
  background: var(--accent-tint-15, rgba(129, 140, 248, 0.25));
  color: var(--color-accent);
  padding: 0 2px;
  border-radius: 2px;
  font-weight: 600;
}

.search-bar__result-snippet {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.search-bar__result-snippet :deep(mark) {
  background: var(--accent-tint-15, rgba(129, 140, 248, 0.25));
  color: var(--color-accent);
  padding: 0 1px;
  border-radius: 2px;
}

/* 下拉动画 */
.search-dropdown-enter-active,
.search-dropdown-leave-active {
  transition: opacity var(--duration-fast) ease, transform var(--duration-fast) ease;
}

.search-dropdown-enter-from,
.search-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
