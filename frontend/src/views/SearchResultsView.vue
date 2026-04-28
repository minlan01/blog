<template>
  <section class="search-results">
    <div class="container">
      <header class="search-results__header">
        <h1 class="search-results__title">
          {{ query ? `搜索 "${query}"` : '搜索' }}
        </h1>
        <SearchBar @search="handleSearch" />
      </header>

      <div v-if="loaded && results.length" class="search-results__list">
        <RouterLink
          v-for="post in results"
          :key="post.id"
          :to="`/posts/${post.slug}`"
          class="search-results__item"
        >
          <span class="search-results__meta">
            {{ post.category?.name || '未分类' }} · {{ post.reading_time }}
          </span>
          <h3 class="search-results__item-title">{{ post.title }}</h3>
          <p class="search-results__item-summary">{{ post.summary }}</p>
        </RouterLink>
      </div>

      <div v-else-if="loaded && query" class="search-results__empty">
        <p>未找到与 "{{ query }}" 相关的结果</p>
      </div>

      <div v-else-if="!query" class="search-results__hint">
        <p>输入关键词开始搜索</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SearchBar from '@/components/blog/SearchBar.vue'
import { getPosts } from '@/api/blog'
import type { PostSummary } from '@/types/blog'

const route = useRoute()
const router = useRouter()

const query = ref('')
const results = ref<PostSummary[]>([])
const loaded = ref(false)

function handleSearch(q: string) {
  if (q.trim()) {
    router.push({ path: '/search', query: { q: q.trim() } })
  }
}

async function doSearch(q: string) {
  if (!q) {
    results.value = []
    loaded.value = true
    return
  }
  loaded.value = false
  try {
    const data = await getPosts({ search: q })
    if (Array.isArray(data)) {
      results.value = data
    } else {
      results.value = (data as any)?.items || []
    }
  } catch {
    results.value = []
  }
  loaded.value = true
}

onMounted(() => {
  const q = route.query.q as string
  if (q) {
    query.value = q
    doSearch(q)
  } else {
    loaded.value = true
  }
})

watch(() => route.query.q, (newQ) => {
  const q = (newQ as string) || ''
  query.value = q
  if (q) {
    doSearch(q)
  } else {
    results.value = []
    loaded.value = true
  }
})
</script>

<style scoped>
.search-results {
  padding: var(--space-3xl) 0;
}

.search-results__header {
  margin-bottom: var(--space-xl);
}

.search-results__title {
  font-size: clamp(1.4rem, 3vw, 1.8rem);
  margin: 0 0 var(--space-lg);
  color: var(--color-text-heading);
}

.search-results__list {
  display: grid;
  gap: 0;
}

.search-results__item {
  display: block;
  padding: var(--space-lg) 0;
  border-bottom: 1px solid var(--color-border);
  color: inherit;
  transition: all 0.2s ease;
}

.search-results__item:first-child {
  border-top: 1px solid var(--color-border);
}

.search-results__item:hover {
  background: var(--accent-tint-04);
}

.search-results__meta {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.search-results__item-title {
  font-size: 1.05rem;
  margin: 4px 0;
  transition: all var(--duration-fast) ease;
}

.search-results__item:hover .search-results__item-title {
  color: var(--color-accent);
}

.search-results__item-summary {
  font-size: 0.85rem;
  color: var(--color-text-soft);
  margin: 0;
  line-height: 1.6;
}

.search-results__empty,
.search-results__hint {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-text-muted);
  font-size: 0.88rem;
}

/* Responsive */
@media (max-width: 768px) {
  .search-results {
    padding: var(--space-xl) 0;
  }

  .search-results__item {
    padding: var(--space-md) 0;
  }

  .search-results__item-title {
    font-size: 1rem;
  }

  .search-results__item-summary {
    font-size: 0.82rem;
  }
}

@media (max-width: 480px) {
  .search-results {
    padding: var(--space-lg) 0;
  }

  .search-results__title {
    font-size: 1.3rem;
  }

  .search-results__item-title {
    font-size: 0.95rem;
  }

  .search-results__item-summary {
    font-size: 0.8rem;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    display: -webkit-box;
    overflow: hidden;
  }
}
</style>
