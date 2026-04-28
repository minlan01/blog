<template>
  <div class="tag-widget">
    <h4 class="tag-widget__title">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
      TAGS
    </h4>
    <div class="tag-widget__cloud" v-if="tags.length">
      <span
        v-for="tag in tags"
        :key="tag.id"
        class="tag-widget__chip"
        @click="$router.push(`/posts?tag=${tag.slug}`)"
      >
        {{ tag.name }}
      </span>
    </div>
    <div v-else class="tag-widget__empty">暂无标签</div>
  </div>
</template>

<script setup lang="ts">
import type { Tag } from '@/types/blog'

defineProps<{
  tags: Tag[]
}>()
</script>

<style scoped>
.tag-widget {
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

.tag-widget::before {
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

.tag-widget > * {
  position: relative;
  z-index: 1;
}

.tag-widget__title {
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

.tag-widget__title svg {
  color: var(--color-accent);
}

.tag-widget__cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-widget__chip {
  font-size: 0.78rem;
  padding: 4px 12px;
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-full);
  background: var(--glass-bg-03);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.tag-widget__chip:hover {
  border-color: var(--accent-tint-25);
  color: var(--color-accent);
  background: var(--accent-tint-06);
}

.tag-widget__empty {
  text-align: center;
  padding: var(--space-md) 0;
  color: var(--color-text-muted);
  font-size: 0.85rem;
}
</style>
