<template>
  <div class="search-bar">
    <svg class="search-bar__icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input
      v-model="query"
      class="search-bar__input"
      type="text"
      placeholder="搜索文章..."
      aria-label="搜索文章"
      @keyup.enter="$emit('search', query)"
    />
    <button class="search-bar__btn" @click="$emit('search', query)">
      搜索
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const query = ref('')

defineEmits<{
  (e: 'search', query: string): void
}>()
</script>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  overflow: hidden;
  transition: all var(--duration-fast) ease;
}

.search-bar:focus-within {
  border-color: var(--color-accent);
  box-shadow: 0 0 8px var(--accent-tint-08);
}

.search-bar__icon {
  flex-shrink: 0;
  color: var(--color-text-muted);
  margin-left: var(--space-md);
}

.search-bar__input {
  flex: 1;
  padding: 10px var(--space-sm);
  border: none;
  background: transparent;
  color: var(--color-text);
  font-size: 0.85rem;
  outline: none;
}

.search-bar__input::placeholder {
  color: var(--color-text-muted);
  opacity: 0.5;
}

.search-bar__btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 14px;
  font-size: 0.78rem;
  color: var(--color-text-muted);
  transition: all var(--duration-fast) ease;
}

.search-bar__btn:hover {
  color: var(--color-accent);
}
</style>
