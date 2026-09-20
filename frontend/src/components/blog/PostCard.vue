<template>
  <article
    class="card"
    ref="cardRef"
    :style="{
      'view-transition-name': `post-card-${post.id}`,
      '--mx': mx + 'px',
      '--my': my + 'px',
      '--rx': rx + 'deg',
      '--ry': ry + 'deg',
    }"
    @mousemove="onMouseMove"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <RouterLink :to="`/posts/${post.slug}`" class="card__link">
      <!-- Cover image -->
      <div class="card__cover" v-if="post.cover_image">
        <img
          :src="post.cover_image"
          alt=""
          class="card__cover-img"
          loading="lazy"
          :style="{ 'view-transition-name': `post-cover-${post.id}` }"
        />
      </div>

      <!-- No-cover placeholder -->
      <div v-else class="card__no-cover">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
      </div>

      <!-- Content -->
      <div class="card__body">
        <div class="card__meta">
          <span class="card__category">{{ post.category?.name || 'uncategorized' }}</span>
          <span class="card__dot"></span>
          <span>{{ formatDate(post.published_at) }}</span>
        </div>

        <h3
          class="card__title"
          :style="{ 'view-transition-name': `post-title-${post.id}` }"
        >{{ post.title }}</h3>
        <p class="card__summary">{{ post.summary }}</p>

        <div class="card__tags" v-if="post.tags.length">
          <span v-for="tag in post.tags" :key="tag.id" class="card__tag">{{ tag.name }}</span>
        </div>
      </div>
    </RouterLink>
  </article>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { PostSummary } from '@/types/blog'

defineProps<{
  post: PostSummary
  index?: number
}>()

const cardRef = ref<HTMLElement | null>(null)
const mx = ref(0)
const my = ref(0)
const rx = ref(0)
const ry = ref(0)

function onMouseEnter() {
  if (cardRef.value) {
    cardRef.value.style.transition = 'transform 0.1s ease-out'
  }
}

function onMouseMove(e: MouseEvent) {
  if (!cardRef.value) return
  const rect = cardRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  mx.value = x
  my.value = y
  // 3D 倾斜：鼠标偏离中心的比例 × 最大角度
  const maxTilt = 6
  rx.value = -(y / rect.height - 0.5) * maxTilt * 2
  ry.value = (x / rect.width - 0.5) * maxTilt * 2
}

function onMouseLeave() {
  if (cardRef.value) {
    cardRef.value.style.transition = 'transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease'
  }
  mx.value = -300
  my.value = -300
  rx.value = 0
  ry.value = 0
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}
</script>

<style scoped>
@property --border-angle {
  syntax: '<angle>';
  inherits: false;
  initial-value: 0deg;
}

.card {
  position: relative;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  overflow: hidden;
  transition: all var(--duration-fast) ease;
  box-shadow: var(--shadow-card), var(--glass-highlight);
  display: flex;
  flex-direction: column;
  /* 3D 透视 */
  transform-style: preserve-3d;
  transform: perspective(800px) rotateX(var(--rx, 0)) rotateY(var(--ry, 0)) translateY(0);
  isolation: isolate;
}

/* Spotlight 光标跟随：::before 做柔光 */
.card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    350px circle at var(--mx, -300px) var(--my, -300px),
    rgba(129, 140, 248, 0.12),
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: 2;
}

/* Gradient Border Draw：::after 做通电边框 */
.card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-lg);
  padding: 1px;
  background: conic-gradient(
    from var(--border-angle),
    transparent 0%,
    var(--color-accent) 15%,
    var(--color-accent-2) 30%,
    transparent 45%
  );
  -webkit-mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: 3;
  animation: border-rotate 3s linear infinite paused;
}

@keyframes border-rotate {
  to { --border-angle: 360deg; }
}

/* Hover 状态：激活所有效果 */
.card:hover {
  border-color: transparent;
  box-shadow: var(--shadow-elevated), 0 0 30px rgba(129, 140, 248, 0.08);
  transform: perspective(800px) rotateX(var(--rx, 0)) rotateY(var(--ry, 0)) translateY(-3px);
}

.card:hover::before {
  opacity: 1;
}

.card:hover::after {
  opacity: 1;
  animation-play-state: running;
}

.card:hover .card__title {
  color: var(--color-accent);
}

.card:hover .card__tag {
  border-color: var(--accent-tint-15);
  color: var(--color-accent);
}

.card:hover .card__cover-img {
  transform: scale(1.06);
}

.card__link {
  display: flex;
  flex-direction: column;
  flex: 1;
  color: inherit;
  text-decoration: none;
  position: relative;
  z-index: 1;
}

/* ── Cover ── */
.card__cover {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.card__cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s var(--ease-out);
}

/* ── No-cover ── */
.card__no-cover {
  width: 100%;
  aspect-ratio: 16 / 9;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 30% 50%, var(--accent-tint-06) 0%, transparent 60%),
    radial-gradient(circle at 70% 80%, rgba(167, 139, 250, 0.04) 0%, transparent 50%);
  color: var(--color-accent);
  opacity: 0.35;
}

/* ── Body ── */
.card__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 8px 10px 10px;
  gap: 2px;
}

.card__meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
  font-size: 0.64rem;
  color: var(--color-text-muted);
}

.card__category {
  color: var(--color-accent);
  font-weight: 500;
}

.card__dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--color-text-muted);
  opacity: 0.4;
}

.card__title {
  font-family: var(--font-display);
  font-size: 0.82rem;
  font-weight: 600;
  line-height: 1.4;
  margin: 0;
  color: var(--color-text-heading);
  transition: color var(--duration-fast) ease;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card__summary {
  margin: 1px 0 0;
  font-size: 0.74rem;
  color: var(--color-text-soft);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: auto;
  padding-top: var(--space-xs);
}

.card__tag {
  font-size: 0.58rem;
  color: var(--color-text-muted);
  background: var(--glass-bg-12);
  border: 1px solid var(--border-default);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  transition: all var(--duration-fast) ease;
}

.card__tag::before {
  content: '# ';
  opacity: 0.4;
}

/* Sibling De-emphasis：hover 一张卡片时其他卡片模糊后退 */
.home__posts:has(.card:hover) .card:not(:hover) {
  opacity: 0.5;
  filter: blur(2px);
  transform: scale(0.98);
}

@media (max-width: 640px) {
  .card__body {
    padding: 12px 14px 14px;
  }

  .card__title {
    font-size: 0.92rem;
  }

  /* 移动端关闭 3D 倾斜（触屏无 mousemove） */
  .card {
    transform: none !important;
  }
}

/* prefers-reduced-motion 尊重用户偏好 */
@media (prefers-reduced-motion: reduce) {
  .card {
    transform: none !important;
  }
  .card::after {
    animation: none !important;
  }
}
</style>
