<template>
  <article class="card">
    <RouterLink :to="`/posts/${post.slug}`" class="card__link">
      <!-- Cover image -->
      <div class="card__cover" v-if="post.cover_image">
        <img :src="post.cover_image" alt="" class="card__cover-img" loading="lazy" />
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

        <h3 class="card__title">{{ post.title }}</h3>
        <p class="card__summary">{{ post.summary }}</p>

        <div class="card__tags" v-if="post.tags.length">
          <span v-for="tag in post.tags" :key="tag.id" class="card__tag">{{ tag.name }}</span>
        </div>
      </div>
    </RouterLink>
  </article>
</template>

<script setup lang="ts">
import type { PostSummary } from '@/types/blog'

defineProps<{
  post: PostSummary
  index?: number
}>()

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}
</script>

<style scoped>
.card {
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
}

.card:hover {
  border-color: var(--accent-tint-30);
  box-shadow: var(--shadow-elevated);
  transform: translateY(-3px);
}

.card__link {
  display: flex;
  flex-direction: column;
  flex: 1;
  color: inherit;
  text-decoration: none;
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

.card:hover .card__cover-img {
  transform: scale(1.06);
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

.card:hover .card__title {
  color: var(--color-accent);
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

.card:hover .card__tag {
  border-color: var(--accent-tint-15);
  color: var(--color-accent);
}

@media (max-width: 640px) {
  .card__body {
    padding: 12px 14px 14px;
  }

  .card__title {
    font-size: 0.92rem;
  }
}
</style>
