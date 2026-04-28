<template>
  <div class="stats-widget">
    <h4 class="stats-widget__title">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>
      STATS
    </h4>
    <div class="stats-widget__grid">
      <div class="stats-widget__item">
        <span class="stats-widget__value">{{ postCount }}</span>
        <span class="stats-widget__label">文章</span>
      </div>
      <div class="stats-widget__item">
        <span class="stats-widget__value">{{ tagCount }}</span>
        <span class="stats-widget__label">标签</span>
      </div>
      <div class="stats-widget__item">
        <span class="stats-widget__value">{{ categoryCount }}</span>
        <span class="stats-widget__label">分类</span>
      </div>
      <div class="stats-widget__item" v-if="lastUpdate">
        <span class="stats-widget__value stats-widget__value--sm">{{ lastUpdate }}</span>
        <span class="stats-widget__label">最后更新</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  postCount: number
  tagCount: number
  categoryCount: number
  lastUpdate: string
}>()
</script>

<style scoped>
.stats-widget {
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

.stats-widget::before {
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

.stats-widget > * {
  position: relative;
  z-index: 1;
}

.stats-widget__title {
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

.stats-widget__title svg {
  color: var(--color-accent);
}

.stats-widget__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stats-widget__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 0;
  border-radius: var(--radius-sm);
  background: var(--glass-bg-02);
}

.stats-widget__value {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-accent);
  line-height: 1.2;
}

.stats-widget__value--sm {
  font-size: 0.75rem;
  font-weight: 600;
}

.stats-widget__label {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  letter-spacing: 0.02em;
}
</style>
