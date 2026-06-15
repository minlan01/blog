<template>
  <section class="archive-page">
    <div class="container">
      <header class="archive-page__header">
        <span class="archive-page__label">ARCHIVE</span>
        <h1 class="archive-page__title">归档</h1>
        <p class="archive-page__count">共 {{ allPosts.length }} 篇文章</p>
      </header>

      <div v-if="loading" class="archive-page__loading">
        <div class="archive-page__skeleton" v-for="n in 4" :key="n"></div>
      </div>

      <div v-else-if="loadError" class="archive-page__error">{{ loadError }}</div>
      <div v-else-if="allPosts.length" class="archive-page__timeline">
        <div
          v-for="year in groupedPosts"
          :key="year.year"
          class="archive-page__year-group"
        >
          <div class="archive-page__year-marker">
            <div class="archive-page__year-dot"></div>
            <h2 class="archive-page__year">{{ year.year }}</h2>
            <span class="archive-page__year-count">{{ year.count }} 篇</span>
          </div>

          <div
            v-for="month in year.months"
            :key="month.key"
            class="archive-page__month-group"
          >
            <div class="archive-page__month-header">
              <span class="archive-page__month">{{ month.label }}</span>
              <span class="archive-page__month-count">{{ month.posts.length }}</span>
            </div>

            <div class="archive-page__posts">
              <RouterLink
                v-for="post in month.posts"
                :key="post.id"
                :to="`/posts/${post.slug}`"
                class="archive-page__post"
              >
                <span class="archive-page__post-date">{{ formatDate(post.published_at) }}</span>
                <span class="archive-page__post-title">{{ post.title }}</span>
                <span v-if="post.category" class="archive-page__post-cat">{{ post.category.name }}</span>
              </RouterLink>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="archive-page__empty">
        <p>暂无文章</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getPosts } from '@/api/blog'
import type { PostSummary } from '@/types/blog'

const allPosts = ref<PostSummary[]>([])
const loading = ref(true)
const loadError = ref('')

interface MonthGroup {
  key: string
  label: string
  posts: PostSummary[]
}

interface YearGroup {
  year: number
  count: number
  months: MonthGroup[]
}

const groupedPosts = computed<YearGroup[]>(() => {
  const yearMap = new Map<number, Map<string, MonthGroup>>()

  for (const post of allPosts.value) {
    const d = new Date(post.published_at)
    const y = d.getFullYear()
    const mKey = `${y}-${String(d.getMonth() + 1).padStart(2, '0')}`
    const mLabel = `${d.getMonth() + 1}月`

    if (!yearMap.has(y)) yearMap.set(y, new Map())
    const months = yearMap.get(y)!
    if (!months.has(mKey)) months.set(mKey, { key: mKey, label: mLabel, posts: [] })
    months.get(mKey)!.posts.push(post)
  }

  return Array.from(yearMap.entries())
    .sort((a, b) => b[0] - a[0])
    .map(([year, months]) => {
      const monthArr = Array.from(months.values())
        .sort((a, b) => b.key.localeCompare(a.key))
      return {
        year,
        count: monthArr.reduce((s, m) => s + m.posts.length, 0),
        months: monthArr,
      }
    })
})

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(async () => {
  try {
    const res = await getPosts({ per_page: 50 })
    allPosts.value = Array.isArray(res) ? res : (res as any)?.items || []
  } catch {
    loadError.value = '文章加载失败，请刷新页面重试'
  }
  loading.value = false
})
</script>

<style scoped>
.archive-page {
  padding: var(--space-3xl) 0;
}

.archive-page__header {
  margin-bottom: var(--space-xl);
}

.archive-page__label {
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.archive-page__title {
  font-size: clamp(1.6rem, 3.5vw, 2.2rem);
  margin: var(--space-xs) 0;
}

.archive-page__count {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

/* Loading */
.archive-page__loading {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.archive-page__skeleton {
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
}

/* Timeline */
.archive-page__timeline {
  position: relative;
  padding-left: 24px;
  border-left: 2px solid var(--color-border);
}

.archive-page__year-group {
  position: relative;
  margin-bottom: var(--space-xl);
}

.archive-page__year-group:last-child {
  margin-bottom: 0;
}

.archive-page__year-marker {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
  margin-left: -25px;
}

.archive-page__year-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--color-accent);
  box-shadow: 0 0 12px var(--accent-tint-40);
  flex-shrink: 0;
}

.archive-page__year {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-text-heading);
}

.archive-page__year-count {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

.archive-page__month-group {
  margin-bottom: var(--space-lg);
}

.archive-page__month-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.archive-page__month {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--color-text-heading);
}

.archive-page__month-count {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  background: var(--color-surface);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-family: var(--font-mono);
}

.archive-page__posts {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.archive-page__post {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--color-text);
  transition: all var(--duration-fast) ease;
}

.archive-page__post:hover {
  background: var(--color-surface-hover);
}

.archive-page__post:hover .archive-page__post-title {
  color: var(--color-accent);
}

.archive-page__post-date {
  font-size: 0.78rem;
  font-family: var(--font-mono);
  color: var(--color-text-muted);
  flex-shrink: 0;
  min-width: 40px;
}

.archive-page__post-title {
  font-size: 0.9rem;
  color: var(--color-text);
  transition: color var(--duration-fast) ease;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.archive-page__post-cat {
  font-size: 0.72rem;
  color: var(--color-accent);
  background: var(--accent-tint-10);
  padding: 2px 10px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.archive-page__empty {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-text-muted);
}

.archive-page__error {
  text-align: center;
  padding: var(--space-3xl);
  color: #ef4444;
  font-size: 0.88rem;
}

@media (max-width: 768px) {
  .archive-page {
    padding: var(--space-xl) 0;
  }

  .archive-page__post {
    flex-wrap: wrap;
    gap: var(--space-xs);
    padding: 8px 10px;
  }

  .archive-page__post-title {
    font-size: 0.85rem;
  }

  .archive-page__post-cat {
    margin-left: 44px;
  }
}

@media (max-width: 480px) {
  .archive-page__post-cat {
    margin-left: 0;
  }

  .archive-page__year-marker {
    gap: var(--space-sm);
    margin-left: -17px;
  }

  .archive-page__year {
    font-size: 1.2rem;
  }
}
</style>
