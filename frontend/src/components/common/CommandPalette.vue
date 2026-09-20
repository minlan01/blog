<template>
  <Teleport to="body">
    <Transition name="cmdk-fade">
      <div v-if="open" class="cmdk-overlay" @click.self="open = false">
        <div class="cmdk-panel">
          <div class="cmdk-header">
            <svg class="cmdk-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input
              ref="inputRef"
              v-model="query"
              class="cmdk-input"
              type="text"
              placeholder="输入命令或搜索..."
              @input="filter"
              aria-label="命令面板"
            />
            <kbd class="cmdk-kbd">ESC</kbd>
          </div>
          <ul v-if="filtered.length > 0" class="cmdk-list">
            <li
              v-for="(item, i) in filtered"
              :key="item.id"
              class="cmdk-item"
              :class="{ 'cmdk-item--active': i === selectedIndex }"
              @mouseenter="selectedIndex = i"
              @click="execute(item)"
            >
              <span class="cmdk-item-label">{{ item.label }}</span>
              <span v-if="item.hint" class="cmdk-item-hint">{{ item.hint }}</span>
            </li>
          </ul>
          <div v-else class="cmdk-empty">没有匹配的命令</div>
          <div class="cmdk-footer">
            <span><kbd>↑</kbd><kbd>↓</kbd> 导航</span>
            <span><kbd>↵</kbd> 执行</span>
            <span><kbd>ESC</kbd> 关闭</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useCommandPalette } from '@/composables/useCommandPalette'

const { open, query, filtered, selectedIndex, filter, execute } = useCommandPalette()
const inputRef = ref<HTMLInputElement | null>(null)

watch(open, (val) => {
  if (val) {
    query.value = ''
    nextTick(() => inputRef.value?.focus())
  }
})
</script>

<style scoped>
.cmdk-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
  z-index: 9999;
}

.cmdk-panel {
  width: 90%;
  max-width: 560px;
  background: var(--color-surface, #1a1a2e);
  border: 1px solid var(--color-border, #333);
  border-radius: var(--radius-md, 8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
  overflow: hidden;
}

.cmdk-header {
  display: flex;
  align-items: center;
  padding: var(--space-md, 12px) var(--space-lg, 16px);
  border-bottom: 1px solid var(--color-border-subtle, rgba(128, 128, 128, 0.2));
}

.cmdk-icon {
  flex-shrink: 0;
  color: var(--color-text-muted, #888);
  margin-right: var(--space-sm, 8px);
}

.cmdk-input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--color-text, #e0e0e0);
  font-size: 0.95rem;
  outline: none;
}

.cmdk-input::placeholder {
  color: var(--color-text-muted, #888);
  opacity: 0.6;
}

.cmdk-kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 22px;
  padding: 0 6px;
  border: 1px solid var(--color-border, #444);
  border-radius: 4px;
  font-size: 0.7rem;
  color: var(--color-text-muted, #888);
  background: rgba(0, 0, 0, 0.2);
}

.cmdk-list {
  list-style: none;
  padding: var(--space-xs, 4px);
  margin: 0;
  max-height: 320px;
  overflow-y: auto;
}

.cmdk-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-sm, 8px) var(--space-md, 12px);
  border-radius: var(--radius-sm, 4px);
  cursor: pointer;
  transition: background var(--duration-fast, 0.15s) ease;
}

.cmdk-item--active {
  background: var(--color-surface-hover, rgba(129, 140, 248, 0.15));
}

.cmdk-item-label {
  font-size: 0.9rem;
  color: var(--color-text, #e0e0e0);
}

.cmdk-item-hint {
  font-size: 0.75rem;
  color: var(--color-text-muted, #888);
}

.cmdk-empty {
  padding: var(--space-lg, 16px);
  text-align: center;
  color: var(--color-text-muted, #888);
  font-size: 0.85rem;
}

.cmdk-footer {
  display: flex;
  gap: var(--space-md, 12px);
  padding: var(--space-sm, 8px) var(--space-lg, 16px);
  border-top: 1px solid var(--color-border-subtle, rgba(128, 128, 128, 0.2));
  font-size: 0.72rem;
  color: var(--color-text-muted, #666);
}

.cmdk-footer span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.cmdk-footer kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 18px;
  padding: 0 4px;
  border: 1px solid var(--color-border, #444);
  border-radius: 3px;
  font-size: 0.65rem;
}

.cmdk-fade-enter-active,
.cmdk-fade-leave-active {
  transition: opacity var(--duration-fast, 0.15s) ease;
}

.cmdk-fade-enter-from,
.cmdk-fade-leave-to {
  opacity: 0;
}
</style>
