<template>
  <div class="reactions">
    <!-- Like button -->
    <button
      class="reactions__btn"
      :class="{ 'reactions__btn--active': likeActive, 'reactions__btn--burst': likeBurst }"
      :disabled="loading || !isLoggedIn"
      :title="isLoggedIn ? '点赞' : '请先登录'"
      @click="onToggle('like')"
    >
      <svg class="reactions__icon" viewBox="0 0 24 24" :fill="likeActive ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
      </svg>
      <span class="reactions__count" v-if="likeCount > 0">{{ likeCount }}</span>
    </button>

    <!-- Bookmark button -->
    <button
      class="reactions__btn reactions__btn--bookmark"
      :class="{ 'reactions__btn--active': bookmarkActive }"
      :disabled="loading || !isLoggedIn"
      :title="isLoggedIn ? '收藏' : '请先登录'"
      @click="onToggle('bookmark')"
    >
      <svg class="reactions__icon" viewBox="0 0 24 24" :fill="bookmarkActive ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
      </svg>
      <span class="reactions__count" v-if="bookmarkCount > 0">{{ bookmarkCount }}</span>
    </button>

    <!-- Floating particles for like burst -->
    <span
      v-for="i in particles"
      :key="i.id"
      class="reactions__particle"
      :style="{ '--dx': i.dx + 'px', '--dy': i.dy + 'px', '--delay': i.delay + 'ms' }"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getPostReactions, toggleReaction } from '@/api/reactions'

const props = defineProps<{
  postId: number
  isLoggedIn: boolean
}>()

const emit = defineEmits<{ (e: 'need-login'): void }>()

const loading = ref(true)
const likeCount = ref(0)
const likeActive = ref(false)
const bookmarkCount = ref(0)
const bookmarkActive = ref(false)
const likeBurst = ref(false)
const particles = ref<{ id: number; dx: number; dy: number; delay: number }[]>([])

async function load() {
  try {
    const r = await getPostReactions(props.postId)
    likeCount.value = r.like.count
    likeActive.value = r.like.user_reacted
    bookmarkCount.value = r.bookmark.count
    bookmarkActive.value = r.bookmark.user_reacted
  } catch {
    // silent fail — reactions are non-critical
  } finally {
    loading.value = false
  }
}

let particleSeq = 0
function spawnParticles() {
  const items = []
  for (let i = 0; i < 8; i++) {
    const angle = (Math.PI * 2 * i) / 8 + Math.random() * 0.5
    const dist = 30 + Math.random() * 25
    items.push({
      id: ++particleSeq,
      dx: Math.cos(angle) * dist,
      dy: Math.sin(angle) * dist,
      delay: Math.random() * 80,
    })
  }
  particles.value = items
  setTimeout(() => { particles.value = [] }, 700)
}

async function onToggle(type: 'like' | 'bookmark') {
  if (!props.isLoggedIn) {
    emit('need-login')
    return
  }
  if (loading.value) return

  const wasActive = type === 'like' ? likeActive.value : bookmarkActive.value
  loading.value = true

  // Optimistic update
  if (type === 'like') {
    likeActive.value = !likeActive.value
    likeCount.value += likeActive.value ? 1 : -1
    if (likeActive.value && !wasActive) {
      likeBurst.value = true
      spawnParticles()
      setTimeout(() => { likeBurst.value = false }, 400)
    }
  } else {
    bookmarkActive.value = !bookmarkActive.value
    bookmarkCount.value += bookmarkActive.value ? 1 : -1
  }

  try {
    const result = await toggleReaction(props.postId, type)
    // Sync with server truth
    if (type === 'like') {
      likeCount.value = result.count
      likeActive.value = result.user_reacted
    } else {
      bookmarkCount.value = result.count
      bookmarkActive.value = result.user_reacted
    }
  } catch {
    // Revert on failure
    if (type === 'like') {
      likeActive.value = !likeActive.value
      likeCount.value += likeActive.value ? 1 : -1
    } else {
      bookmarkActive.value = !bookmarkActive.value
      bookmarkCount.value += bookmarkActive.value ? 1 : -1
    }
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.postId, load)
</script>

<style scoped>
.reactions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reactions__btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  color: var(--color-text-muted);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  position: relative;
}

.reactions__btn:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
  transform: translateY(-1px);
}

.reactions__btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reactions__btn--active {
  color: var(--color-accent);
  border-color: var(--color-accent);
  background: var(--accent-tint-08);
}

.reactions__btn--bookmark.reactions__btn--active {
  color: var(--color-accent-2, #f59e0b);
  border-color: var(--color-accent-2, #f59e0b);
}

.reactions__icon {
  width: 18px;
  height: 18px;
  transition: transform var(--duration-fast) ease;
}

.reactions__btn--active .reactions__icon {
  transform: scale(1.15);
}

.reactions__btn--burst .reactions__icon {
  animation: heartbeat 0.4s ease;
}

@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  30% { transform: scale(1.4); }
  60% { transform: scale(0.9); }
}

.reactions__count {
  min-width: 16px;
  text-align: center;
}

/* Particles */
.reactions__particle {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent);
  pointer-events: none;
  animation: particle-fly 0.6s ease-out forwards;
  animation-delay: var(--delay, 0ms);
  opacity: 0;
}

@keyframes particle-fly {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(calc(-50% + var(--dx)), calc(-50% + var(--dy))) scale(0);
    opacity: 0;
  }
}
</style>
