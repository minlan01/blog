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
              <!-- 文章卡片列表 — Bento Grid 布局 -->
              <div v-if="allPosts.length" class="home__posts">
                <PostCard
                  v-for="(post, idx) in allPosts"
                  :key="post.id"
                  :post="post"
                  :index="idx"
                  :class="[
                    'scroll-reveal-up',
                    { 'card--bento-lg': idx === 0 && post.is_featured }
                  ]"
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
            <RouterLink to="/posts" class="home__more-btn" ref="moreBtnRef">
              <span>查看全部文章</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </RouterLink>
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
import { useMagnetic } from '@/composables/useMagnetic'
import SiteStatsWidget from '@/components/sidebar/SiteStatsWidget.vue'
import CategoryWidget from '@/components/sidebar/CategoryWidget.vue'
import TagCloudWidget from '@/components/sidebar/TagCloudWidget.vue'
import ArchiveWidget from '@/components/sidebar/ArchiveWidget.vue'
import ErrorBanner from '@/components/common/ErrorBanner.vue'
import { getPosts, getCategories, getTags } from '@/api/blog'
import { safeCall } from '@/api/http'
import { useSiteStore } from '@/stores/site'
import type { PostSummary, Category, Tag, PaginatedResponse } from '@/types/blog'

const siteStore = useSiteStore()
const profile = computed(() => siteStore.profile)

const route = useRoute()
const showOpening = ref(false)
const entered = ref(false)
const moreBtnRef = ref<HTMLElement | null>(null)
useMagnetic(moreBtnRef, 0.25)
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
    safeCall<PaginatedResponse<PostSummary>>(
      () => getPosts({ per_page: 7, featured: true }),
      { items: [], total: 0, page: 1, per_page: 7, total_pages: 0 }
    ),
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
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
}

/* Bento Grid：第一篇 featured 文章跨 2 列 */
.home__posts :deep(.card--bento-lg) {
  grid-column: 1 / -1;
}

.home__posts :deep(.card--bento-lg .card__cover) {
  aspect-ratio: 21/9;
}

.home__posts :deep(.card--bento-lg .card__title) {
  font-size: 1.3rem;
}

.home__posts :deep(.card) {
  transition: all var(--duration-fast) var(--ease-out);
}

/* Bento 卡片取消瀑布流的高度自适应限制 */
.home__posts :deep(.card__summary) {
  -webkit-line-clamp: 3;
  display: -webkit-box;
}

.home__posts :deep(.card__title) {
  -webkit-line-clamp: 2;
  display: -webkit-box;
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
  gap: 8px;
  padding: 12px 28px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-accent-gradient);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  transition: all var(--duration-fast) var(--ease-out);
  box-shadow: 0 4px 20px rgba(129, 140, 248, 0.25);
  cursor: pointer;
}

.home__more-btn:hover {
  filter: brightness(1.1);
  box-shadow: 0 6px 24px rgba(129, 140, 248, 0.35);
  transform: translateY(-2px);
}

.home__more-btn:active {
  transform: translateY(0);
}

[data-theme="light"] .home__more-btn {
  color: #fff;
}

/* ========================================
   Right Sidebar
   ======================================== */

.home__sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.home__music-float {
  position: fixed;
  left: 16px;
  bottom: 16px;
  z-index: 50;
}

@media (max-width: 768px) {
  .home__music-float {
    left: 12px;
    bottom: 12px;
  }
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
    grid-template-columns: 1fr;
  }
}
</style>
