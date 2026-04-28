<template>
  <nav class="pagination" v-if="totalPages > 1">
    <button class="pagination__btn" :disabled="page <= 1" @click="$emit('change', page - 1)">&larr; 上一页</button>
    <div class="pagination__pages">
      <button
        v-for="p in visiblePages"
        :key="p"
        class="pagination__page"
        :class="{ 'pagination__page--active': p === page, 'pagination__page--ellipsis': p === '...' }"
        :disabled="p === '...'"
        @click="typeof p === 'number' && $emit('change', p)"
      >{{ p }}</button>
    </div>
    <button class="pagination__btn" :disabled="page >= totalPages" @click="$emit('change', page + 1)">下一页 &rarr;</button>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  page: number
  totalPages: number
}>()

defineEmits<{
  (e: 'change', page: number): void
}>()

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const total = props.totalPages
  const current = props.page

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-xl) 0;
}

.pagination__btn {
  font-size: 0.8rem;
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  background: transparent;
  transition: all var(--duration-fast) ease;
}

.pagination__btn:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.pagination__btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.pagination__pages {
  display: flex;
  gap: 4px;
}

.pagination__page {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.82rem;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  background: transparent;
  transition: all var(--duration-fast) ease;
}

.pagination__page:hover:not(:disabled) {
  border-color: var(--color-border);
  color: var(--color-text);
}

.pagination__page--active {
  border-color: var(--color-accent);
  color: var(--color-accent);
  font-weight: 600;
  background: var(--accent-tint-06);
}

.pagination__page--ellipsis {
  cursor: default;
}
</style>
