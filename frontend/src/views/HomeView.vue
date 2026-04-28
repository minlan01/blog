<template>
  <div class="home">
    <!-- Opening 全屏覆盖层 — Teleport 到 body 以避免父级 transform 破坏 fixed 定位 -->
    <Teleport to="body">
      <OpeningScreen
        v-if="showOpening"
        :title="profile?.hero_title || 'SYSTEM ONLINE\nACCESS GRANTED'"
        :subtitle="profile?.hero_subtitle || '// Terminal blog system ready.'"
        @enter="onEnter"
      />
    </Teleport>

    <!-- 博客主内容区 -->
    <Transition name="content-reveal">
      <div v-if="entered" class="home__body">

        <!-- 主网格：文章列表 + 右侧边栏 -->
        <div class="home__grid-wrap">
          <div class="home__grid">

            <!-- 左侧：文章卡片主内容区 -->
            <main class="home__main">
              <!-- 文章卡片列表 -->
              <div v-if="allPosts.length" class="home__posts">
                <PostCard
                  v-for="(post, idx) in allPosts"
                  :key="post.id"
                  :post="post"
                  :index="idx"
                />
              </div>

              <!-- 空状态 -->
              <div v-else-if="!loadError" class="home__empty">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                <p>还没有文章</p>
                <span>即将发布新内容，敬请期待。</span>
              </div>

              <ErrorBanner
                :visible="loadError"
                title="内容加载失败"
                description="后端服务可能未启动，请确认 FastAPI 在 http://127.0.0.1:8000 运行中。"
                @retry="loadData"
              />
            </main>

            <!-- 右侧边栏 -->
            <aside class="home__sidebar">
              <ProfileWidget />
              <div class="home__sidebar-sticky">
                <SiteStatsWidget
                  :post-count="allPosts.length"
                  :tag-count="tags.length"
                  :category-count="categories.length"
                  :last-update="lastUpdateDate"
                />
                <CategoryWidget :categories="categories" />
                <TagCloudWidget :tags="tags" />
                <ArchiveWidget :posts="allPosts" />
              </div>
            </aside>

          </div>

          <!-- 查看全部文章 — 独立于 grid，全宽居中 -->
          <div v-if="allPosts.length" class="home__more">
            <RouterLink to="/posts" class="home__more-btn">查看全部文章 &rarr;</RouterLink>
          </div>
        </div>

      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import OpeningScreen from '@/components/landing/OpeningScreen.vue'
import PostCard from '@/components/blog/PostCard.vue'
import ProfileWidget from '@/components/sidebar/ProfileWidget.vue'
import SiteStatsWidget from '@/components/sidebar/SiteStatsWidget.vue'
import CategoryWidget from '@/components/sidebar/CategoryWidget.vue'
import TagCloudWidget from '@/components/sidebar/TagCloudWidget.vue'
import ArchiveWidget from '@/components/sidebar/ArchiveWidget.vue'
import ErrorBanner from '@/components/common/ErrorBanner.vue'
import { getPosts, getCategories, getTags } from '@/api/blog'
import { safeCall } from '@/api/http'
import { useSiteStore } from '@/stores/site'
import type { PostSummary, Category, Tag } from '@/types/blog'

const siteStore = useSiteStore()
const profile = computed(() => siteStore.profile)

const route = useRoute()
const showOpening = ref(false)
const entered = ref(false)
const allPosts = ref<PostSummary[]>([])
const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const loadError = ref(false)

const lastUpdateDate = computed(() => {
  if (!allPosts.value.length) return ''
  const latest = allPosts.value.reduce((a, b) =>
    new Date(a.published_at) > new Date(b.published_at) ? a : b
  )
  return new Date(latest.published_at).toLocaleDateString('zh-CN', {
    month: 'short', day: 'numeric'
  })
})

function onEnter() {
  showOpening.value = false
  entered.value = true
  sessionStorage.setItem('blog_visited', '1')
}

watch(() => route.fullPath, (path) => {
  if (path.includes('intro=1')) {
    showOpening.value = true
    entered.value = false
  }
})

async function loadData() {
  loadError.value = false
  await siteStore.loadProfile()

  const [posts, cats, tagList] = await Promise.all([
    safeCall(() => getPosts(), []),
    safeCall(() => getCategories(), []),
    safeCall(() => getTags(), []),
  ])

  const items = Array.isArray(posts) ? posts : (posts as any)?.items || []
  allPosts.value = items
  categories.value = cats
  tags.value = tagList

  siteStore.setStats({
    posts: items.length,
    tags: tagList.length,
    categories: cats.length,
  })

  if (!items.length && !siteStore.profile) {
    loadError.value = true
  }
}

onMounted(() => {
  // Show opening animation on first visit (no "visited" flag in sessionStorage)
  const hasVisited = sessionStorage.getItem('blog_visited')
  if (hasVisited) {
    entered.value = true
  } else {
    showOpening.value = true
  }
  loadData()
})
</script>

<style scoped>
.content-reveal-enter-active {
  transition: opacity 0.6s ease 0.1s, transform 0.6s ease 0.1s;
}
.content-reveal-enter-from {
  opacity: 0;
  transform: translateY(16px);
}

.home__body {
  min-height: 100vh;
  padding-top: var(--space-xl);
  padding-bottom: var(--space-2xl);
}

/* ========================================
   Main Grid Layout
   ======================================== */

.home__grid-wrap {
  width: min(var(--content-width), calc(100% - 48px));
  margin: 0 auto;
}

.home__grid {
  display: grid;
  grid-template-columns: 1fr clamp(220px, 25vw, 280px);
  gap: clamp(16px, 3vw, var(--space-xl));
  align-items: start;
}

/* ========================================
   Main Content Area
   ======================================== */

.home__main {
  min-width: 0;
}

.home__posts {
  columns: 2;
  column-gap: var(--space-md);
}

.home__posts :deep(.card) {
  break-inside: avoid;
  margin-bottom: var(--space-md);
}

/* Remove line clamps so card height adapts to content */
.home__posts :deep(.card__summary) {
  -webkit-line-clamp: unset;
  display: block;
}

.home__posts :deep(.card__title) {
  -webkit-line-clamp: unset;
  display: block;
}

/* Empty state */
.home__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-3xl) var(--space-lg);
  text-align: center;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  box-shadow: var(--glass-card-shadow);
}

.home__empty svg {
  color: var(--color-text-muted);
  opacity: 0.3;
  margin-bottom: var(--space-md);
}

.home__empty p {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin-bottom: 6px;
}

.home__empty span {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

/* More button — 全宽居中，与文章列表保持固定距离 */
.home__more {
  margin-top: var(--space-3xl);
  text-align: center;
}

.home__more-btn {
  display: inline-flex;
  align-items: center;
  padding: 12px 28px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  color: var(--color-text-heading);
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  transition: all var(--duration-fast) ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.home__more-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: var(--accent-tint-06);
  transform: translateY(-1px);
  box-shadow: var(--shadow-elevated);
}

/* ========================================
   Right Sidebar
   ======================================== */

.home__sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.home__sidebar-sticky {
  position: sticky;
  top: calc(var(--header-height) + var(--space-md));
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ========================================
   Responsive
   ======================================== */

@media (max-width: 960px) {
  .home__grid {
    grid-template-columns: 1fr;
  }

  .home__sidebar {
    order: -1;
  }

  .home__sidebar-sticky {
    position: static;
  }
}

@media (max-width: 768px) {
  .home__grid-wrap {
    width: calc(100% - 32px);
  }
}

@media (max-width: 640px) {
  .home__body {
    padding-top: var(--space-md);
  }

  .home__grid-wrap {
    width: calc(100% - 24px);
  }

  .home__posts {
    columns: 1;
  }
}
</style>
