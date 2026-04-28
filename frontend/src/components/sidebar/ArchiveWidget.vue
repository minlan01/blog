<template>
  <div class="archive-widget" v-if="archives.length">
    <h4 class="archive-widget__title">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
      ARCHIVES
    </h4>
    <div class="archive-widget__list">
      <RouterLink
        v-for="item in archives"
        :key="item.key"
        :to="`/posts?month=${item.key}`"
        class="archive-widget__item"
      >
        <span class="archive-widget__month">{{ item.label }}</span>
        <span class="archive-widget__count">{{ item.count }}</span>
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PostSummary } from '@/types/blog'

const props = defineProps<{
  posts: PostSummary[]
}>()

interface ArchiveItem {
  key: string
  label: string
  count: number
}

const archives = computed<ArchiveItem[]>(() => {
  const map = new Map<string, { label: string; count: number }>()

  for (const post of props.posts) {
    const d = new Date(post.published_at)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    const label = `${d.getFullYear()} 年 ${d.getMonth() + 1} 月`

    const existing = map.get(key)
    if (existing) {
      existing.count++
    } else {
      map.set(key, { label, count: 1 })
    }
  }

  return Array.from(map.entries())
    .map(([key, val]) => ({ key, ...val }))
    .sort((a, b) => b.key.localeCompare(a.key))
    .slice(0, 12)
})
</script>

<style scoped>
.archive-widget {
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  padding: var(--space-lg);
  box-shadow: var(--glass-card-shadow);
  position: relative;
  overflow: hidden;
}

.archive-widget::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--glass-noise-highlight);
  background-size: var(--glass-noise-highlight-size);
  background-repeat: repeat, no-repeat;
  background-position: 0 0, 0 0;
  pointer-events: none;
  z-index: 0;
}

.archive-widget > * {
  position: relative;
  z-index: 1;
}

.archive-widget__title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  color: var(--color-text-heading);
  margin: 0 0 var(--space-md);
}

.archive-widget__title svg {
  color: var(--color-accent);
}

.archive-widget__list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 240px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--border-medium) transparent;
}

.archive-widget__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  color: inherit;
  text-decoration: none;
  transition: all var(--duration-fast) ease;
}

.archive-widget__item:hover {
  background: var(--accent-tint-06);
}

.archive-widget__month {
  font-size: 0.82rem;
  color: var(--color-text-soft);
  transition: color var(--duration-fast) ease;
}

.archive-widget__item:hover .archive-widget__month {
  color: var(--color-accent);
}

.archive-widget__count {
  font-size: 0.72rem;
  font-family: var(--font-mono);
  color: var(--color-text-muted);
  background: var(--glass-bg-12);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}
</style>
