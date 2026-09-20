<template>
  <section class="tags-page">
    <div class="container narrow-container">
      <header class="tags-page__header">
        <h1 class="tags-page__title">标签</h1>
        <p class="tags-page__count" v-if="tags.length">{{ totalPosts }} 篇文章 · {{ tags.length }} 个标签</p>
      </header>

      <div v-if="loading" class="tags-page__loading">
        <div v-for="n in 8" :key="n" class="tags-page__skeleton skeleton-shimmer"></div>
      </div>

      <div v-else-if="tags.length === 0" class="tags-page__empty">暂无标签</div>

      <div v-else class="tags-page__cloud">
        <RouterLink
          v-for="tag in tags"
          :key="tag.id"
          :to="`/posts?tag=${tag.slug}`"
          class="tags-page__tag"
          :style="{ fontSize: tagFontSize(tag.post_count) + 'rem' }"
        >
          <span class="tags-page__tag-name">{{ tag.name }}</span>
          <span class="tags-page__tag-count">{{ tag.post_count }}</span>
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getTagsCloud, type TagWithCount } from '@/api/blog'

const tags = ref<TagWithCount[]>([])
const loading = ref(true)

const totalPosts = computed(() => tags.value.reduce((sum, t) => sum + t.post_count, 0))

function tagFontSize(count: number): number {
  if (!tags.value.length) return 1
  const max = Math.max(...tags.value.map(t => t.post_count))
  const min = Math.min(...tags.value.map(t => t.post_count))
  if (max === min) return 1.1
  const ratio = (count - min) / (max - min)
  return 0.85 + ratio * 0.8 // 0.85rem ~ 1.65rem
}

onMounted(async () => {
  try {
    tags.value = await getTagsCloud()
  } catch {
    // ignore
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.tags-page {
  padding: var(--space-xl) 0;
  min-height: 60vh;
}

.tags-page__header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.tags-page__title {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--color-text-heading);
  letter-spacing: 0.05em;
}

.tags-page__count {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin-top: 0.4rem;
}

.tags-page__loading {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}

.tags-page__skeleton {
  width: 80px;
  height: 36px;
  border-radius: var(--radius-md);
}

.tags-page__empty {
  text-align: center;
  color: var(--color-text-muted);
  padding: 4rem 0;
}

.tags-page__cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem 0.75rem;
  justify-content: center;
  align-items: center;
  max-width: 700px;
  margin: 0 auto;
}

.tags-page__tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.9rem;
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  color: var(--color-text);
  text-decoration: none;
  font-weight: 500;
  line-height: 1.4;
  transition: all 0.15s ease;
}

.tags-page__tag:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--color-accent-glow);
}

.tags-page__tag-name {
  white-space: nowrap;
}

.tags-page__tag-count {
  font-size: 0.75em;
  color: var(--color-text-muted);
  background: var(--glass-surface-bg);
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  min-width: 1.2rem;
  text-align: center;
}
</style>
