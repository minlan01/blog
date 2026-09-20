<template>
  <div class="emoji-bar">
    <!-- Existing reactions -->
    <div class="emoji-bar__list">
      <button
        v-for="g in groups"
        :key="g.emoji"
        class="emoji-bar__chip"
        :class="{ 'emoji-bar__chip--active': g.user_reacted }"
        :disabled="loading"
        :title="g.count + ' 人反应'"
        @click="onToggle(g.emoji)"
      >
        <span class="emoji-bar__emoji">{{ g.emoji }}</span>
        <span class="emoji-bar__count" v-if="g.count > 0">{{ g.count }}</span>
      </button>

      <!-- Add reaction trigger -->
      <button
        v-if="isLoggedIn && !showPicker"
        class="emoji-bar__add"
        :disabled="loading"
        @click="showPicker = true"
        title="添加反应"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>
      </button>
    </div>

    <!-- Picker popover -->
    <Transition name="picker">
      <div v-if="showPicker" class="emoji-bar__picker">
        <button
          v-for="e in EMOJI_LIST"
          :key="e"
          class="emoji-bar__picker-emoji"
          @click="onPick(e)"
        >{{ e }}</button>
        <button class="emoji-bar__picker-close" @click="showPicker = false">×</button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCommentReactions, toggleCommentReaction, type CommentReactionGroup } from '@/api/reactions'

const props = defineProps<{
  commentId: number
  isLoggedIn: boolean
}>()

const EMOJI_LIST = ['👍', '❤️', '😂', '🎉', '🚀', '👀']

const groups = ref<CommentReactionGroup[]>([])
const loading = ref(true)
const showPicker = ref(false)

async function load() {
  try {
    groups.value = await getCommentReactions(props.commentId)
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

async function onToggle(emoji: string) {
  if (!props.isLoggedIn) return
  loading.value = true
  try {
    const result = await toggleCommentReaction(props.commentId, emoji)
    if (result) {
      // Update or insert the group
      const idx = groups.value.findIndex(g => g.emoji === emoji)
      if (idx >= 0) {
        if (result.count === 0) {
          groups.value.splice(idx, 1)
        } else {
          groups.value[idx] = result
        }
      } else if (result.count > 0) {
        groups.value.push(result)
      }
    } else {
      // toggle returned null = removed
      const idx = groups.value.findIndex(g => g.emoji === emoji)
      if (idx >= 0) {
        if (groups.value[idx].count <= 1) {
          groups.value.splice(idx, 1)
        } else {
          groups.value[idx].count--
          groups.value[idx].user_reacted = false
        }
      }
    }
    showPicker.value = false
  } finally {
    loading.value = false
  }
}

function onPick(emoji: string) {
  onToggle(emoji)
}

onMounted(load)
</script>

<style scoped>
.emoji-bar {
  display: inline-flex;
  align-items: center;
  position: relative;
}

.emoji-bar__list {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.emoji-bar__chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 8px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  cursor: pointer;
  font-size: 0.75rem;
  transition: all var(--duration-fast) ease;
}

.emoji-bar__chip:hover:not(:disabled) {
  border-color: var(--color-accent);
  transform: translateY(-1px);
}

.emoji-bar__chip--active {
  border-color: var(--color-accent);
  background: var(--accent-tint-10);
}

.emoji-bar__chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.emoji-bar__emoji {
  font-size: 0.9rem;
  line-height: 1;
}

.emoji-bar__count {
  color: var(--color-text-muted);
  font-weight: 500;
}

.emoji-bar__add {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: 1px dashed var(--glass-border);
  border-radius: var(--radius-full);
  background: none;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.emoji-bar__add:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
  border-style: solid;
}

.emoji-bar__add:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Picker popover */
.emoji-bar__picker {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 6px 8px;
  background: var(--glass-panel-bg, rgba(20, 20, 35, 0.95));
  backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  z-index: 10;
}

.emoji-bar__picker-emoji {
  font-size: 1.1rem;
  padding: 4px 6px;
  border: none;
  background: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  line-height: 1;
}

.emoji-bar__picker-emoji:hover {
  background: var(--color-surface-hover);
  transform: scale(1.2);
}

.emoji-bar__picker-close {
  font-size: 1rem;
  color: var(--color-text-muted);
  border: none;
  background: none;
  cursor: pointer;
  padding: 0 4px;
}

.picker-enter-active,
.picker-leave-active {
  transition: all 0.15s ease;
}

.picker-enter-from,
.picker-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
