<template>
  <div class="error-banner" v-if="visible">
    <div class="error-banner__inner">
      <div class="error-banner__icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      </div>
      <div class="error-banner__content">
        <p class="error-banner__title">{{ title }}</p>
        <p class="error-banner__desc">{{ description }}</p>
      </div>
      <button v-if="retryable" class="error-banner__retry" @click="$emit('retry')">
        重试
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  visible: boolean
  title?: string
  description?: string
  retryable?: boolean
}>(), {
  title: '数据加载失败',
  description: '请检查后端是否正常启动（默认地址 http://127.0.0.1:8000）',
  retryable: true,
})

defineEmits<{
  (e: 'retry'): void
}>()
</script>

<style scoped>
.error-banner {
  padding: var(--space-md) 0;
}

.error-banner__inner {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  border: 1px solid rgba(245, 158, 11, 0.2);
  background: rgba(245, 158, 11, 0.06);
  backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
  -webkit-backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
}

.error-banner__icon {
  display: flex;
  align-items: center;
  color: var(--color-ochre);
  flex-shrink: 0;
}

.error-banner__content {
  flex: 1;
  min-width: 0;
}

.error-banner__title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-ochre);
  margin: 0 0 2px;
}

.error-banner__desc {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  margin: 0;
}

.error-banner__retry {
  flex-shrink: 0;
  font-size: 0.78rem;
  padding: 6px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(245, 158, 11, 0.25);
  color: var(--color-ochre);
  background: transparent;
  transition: background var(--duration-fast) ease;
}

.error-banner__retry:hover {
  background: rgba(245, 158, 11, 0.08);
}
</style>
