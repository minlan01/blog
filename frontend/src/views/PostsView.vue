<template>
  <section class="posts-page">
    <div class="posts-page__wrap">

      <!-- Glass panel wraps everything -->
      <div class="posts-page__glass">

        <header class="posts-page__header">
          <h1 class="posts-page__title">文章列表</h1>
          <SearchBar @search="handleSearch" />
        </header>

        <div class="posts-page__content" v-if="loaded && !loadError">
          <!-- 分类筛选 -->
          <div class="posts-page__filters" v-if="categories.length">
            <button
              class="posts-page__filter-btn"
              :class="{ active: !activeCategory }"
              @click="activeCategory = null"
            >全部</button>
            <button
              v-for="cat in categories"
              :key="cat.id"
              class="posts-page__filter-btn"
              :class="{ active: activeCategory === cat.slug }"
              @click="activeCategory = cat.slug"
            >{{ cat.name }}</button>
          </div>

          <!-- 文章列表 -->
          <div class="posts-page__grid">
            <PostCard
              v-for="(post, idx) in filteredPosts"
              :key="post.id"
              :post="post"
              :index="idx"
            />
          </div>

          <Pagination
            v-if="totalPages > 1"
            :page="currentPage"
            :total-pages="totalPages"
            @change="handlePageChange"
          />

          <p v-if="!filteredPosts.length" class="posts-page__empty">
            没有找到匹配的文章。
          </p>
        </div>

        <!-- 加载态 -->
        <div v-else-if="!loaded" class="posts-page__loading">
          <div class="posts-page__grid">
            <div v-for="n in 6" :key="n" class="posts-page__skeleton"></div>
          </div>
        </div>

        <!-- 错误态 -->
        <div v-else class="posts-page__error">
          <p>数据加载失败，请检查后端状态。</p>
          <button class="posts-page__retry" @click="loadData">重试</button>
        </div>

      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import PostCard from '@/components/blog/PostCard.vue'
import SearchBar from '@/components/blog/SearchBar.vue'
import Pagination from '@/components/common/Pagination.vue'
import { getPosts, getCategories } from '@/api/blog'
import { safeCall } from '@/api/http'
import type { PostSummary, Category } from '@/types/blog'

const route = useRoute()

const allPosts = ref<PostSummary[]>([])
const categories = ref<Category[]>([])
const loaded = ref(false)
const loadError = ref(false)
const activeCategory = ref<string | null>(null)
const currentPage = ref(1)
const totalPages = ref(1)
const searchQuery = ref('')

const filteredPosts = computed(() => {
  let result = allPosts.value
  if (activeCategory.value) {
    result = result.filter((p) => p.category?.slug === activeCategory.value)
  }
  return result
})

function handleSearch(query: string) {
  if (query.trim()) {
    window.location.href = `/search?q=${encodeURIComponent(query)}`
  }
}

function handlePageChange(page: number) {
  currentPage.value = page
  loadData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function loadData() {
  loaded.value = false
  loadError.value = false

  if (route.query.category) activeCategory.value = route.query.category as string

  const [posts, cats] = await Promise.all([
    safeCall(() => getPosts({ page: currentPage.value, per_page: 12 }), [] as any),
    safeCall(() => getCategories(), []),
  ])

  // Handle paginated response
  if (Array.isArray(posts)) {
    allPosts.value = posts
    totalPages.value = 1
  } else {
    allPosts.value = (posts as any)?.items || []
    totalPages.value = (posts as any)?.total_pages || 1
  }

  categories.value = cats

  if (!allPosts.value.length && !cats.length) {
    loadError.value = true
  }

  loaded.value = true
}

watch(() => route.query.category, (val) => {
  if (val) activeCategory.value = val as string
})

onMounted(loadData)
</script>

<style scoped>
.posts-page {
  padding: var(--space-3xl) 0;
}

.posts-page__wrap {
  width: min(1600px, calc(100% - 48px));
  margin: 0 auto;
}

.posts-page__header {
  margin-bottom: var(--space-xl);
}

/* ── Glass panel ── */
.posts-page__glass {
  background: var(--glass-panel-bg) !important;
  backdrop-filter: var(--glass-panel-blur) saturate(var(--glass-panel-saturate)) !important;
  -webkit-backdrop-filter: var(--glass-panel-blur) saturate(var(--glass-panel-saturate)) !important;
  border: 1px solid var(--glass-panel-border);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  position: relative;
  overflow: hidden;
  box-shadow: var(--glass-panel-glow);
}

.posts-page__glass::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--glass-noise);
  background-size: 128px 128px;
  pointer-events: none;
  z-index: 0;
}

.posts-page__glass > * {
  position: relative;
  z-index: 1;
}

.posts-page__title {
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  font-weight: 600;
  margin: 0 0 var(--space-lg);
  color: var(--color-text);
}

/* Filters */
.posts-page__filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: var(--space-xl);
  padding: var(--space-md);
  background: var(--glass-bg-12);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
  -webkit-backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
}

.posts-page__filter-btn {
  font-size: 0.9rem;
  font-weight: 500;
  padding: 8px 18px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  background: var(--glass-bg-02);
  backdrop-filter: var(--glass-card-blur);
  transition: all var(--duration-fast) ease;
  cursor: pointer;
}

.posts-page__filter-btn:hover {
  border-color: var(--border-strong);
  background: var(--border-subtle);
  color: var(--color-text);
}

.posts-page__filter-btn.active {
  border-color: var(--accent-tint-40);
  background: var(--accent-tint-15);
  color: var(--color-accent);
  backdrop-filter: var(--glass-surface-blur);
  box-shadow: 0 4px 12px var(--accent-tint-10);
}

/* Grid — max 5 cols on wide, adapts down */
.posts-page__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--space-md);
}

.posts-page__empty {
  text-align: center;
  color: var(--color-text-muted);
  font-size: 1rem;
  padding: var(--space-3xl);
}

/* Loading */
.posts-page__skeleton {
  aspect-ratio: 4 / 3;
  border: 1px solid var(--glass-surface-border);
  border-radius: var(--radius-lg);
  background: var(--glass-surface-bg);
  backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
  -webkit-backdrop-filter: var(--glass-surface-blur) saturate(var(--glass-surface-saturate));
}

/* Error */
.posts-page__error {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-text-muted);
  font-size: 1rem;
}

.posts-page__retry {
  margin-top: var(--space-md);
  padding: 10px 24px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  font-size: 0.95rem;
  font-weight: 500;
  background: var(--glass-bg-02);
  backdrop-filter: var(--glass-card-blur);
  transition: all var(--duration-fast) ease;
  cursor: pointer;
}

.posts-page__retry:hover {
  border-color: var(--accent-tint-40);
  background: var(--accent-tint-10);
  color: var(--color-accent);
}

@media (max-width: 768px) {
  .posts-page__filters {
    padding: var(--space-sm);
  }

  .posts-page__filter-btn {
    padding: 6px 14px;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .posts-page {
    padding: var(--space-xl) 0;
  }

  .posts-page__filter-btn {
    padding: 5px 10px;
    font-size: 0.8rem;
  }
}
</style>
