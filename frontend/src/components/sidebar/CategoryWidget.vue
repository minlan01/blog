<template>
  <div class="cat-widget">
    <h4 class="cat-widget__title">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
      CATEGORIES
    </h4>
    <div class="cat-widget__list">
      <RouterLink
        v-for="cat in categories"
        :key="cat.id"
        :to="`/category/${cat.slug}`"
        class="cat-widget__item"
      >
        <span class="cat-widget__name">{{ cat.name }}</span>
        <span class="cat-widget__arrow">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
        </span>
      </RouterLink>
      <div v-if="!categories.length" class="cat-widget__empty">暂无分类</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Category } from '@/types/blog'

defineProps<{
  categories: Category[]
}>()
</script>

<style scoped>
.cat-widget {
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

.cat-widget::before {
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

.cat-widget > * {
  position: relative;
  z-index: 1;
}

.cat-widget__title {
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

.cat-widget__title svg {
  color: var(--color-accent);
}

.cat-widget__list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cat-widget__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  color: inherit;
  text-decoration: none;
  transition: all var(--duration-fast) ease;
}

.cat-widget__item:hover {
  background: var(--accent-tint-06);
}

.cat-widget__name {
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--color-text-soft);
  transition: color var(--duration-fast) ease;
}

.cat-widget__item:hover .cat-widget__name {
  color: var(--color-accent);
}

.cat-widget__arrow {
  display: flex;
  color: var(--color-text-muted);
  opacity: 0;
  transform: translateX(-4px);
  transition: all var(--duration-fast) ease;
}

.cat-widget__item:hover .cat-widget__arrow {
  opacity: 1;
  transform: translateX(0);
}

.cat-widget__empty {
  text-align: center;
  padding: var(--space-md) 0;
  color: var(--color-text-muted);
  font-size: 0.85rem;
}
</style>
