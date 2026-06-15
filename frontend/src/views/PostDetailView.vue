<template>
  <div>
  <article class="detail" v-if="post">
    <!-- Reading progress bar -->
    <div class="detail__progress-bar">
      <div class="detail__progress-fill" :style="{ width: readProgress + '%' }"></div>
    </div>

    <div class="detail__wrap">
      <!-- Left: Article content -->
      <div class="detail__main">
        <nav class="detail__nav">
          <RouterLink to="/posts" class="detail__back">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
            返回文章列表
          </RouterLink>
        </nav>

        <!-- Hero header -->
        <header class="detail__hero">
          <div class="detail__cover" v-if="post.cover_image">
            <img :src="post.cover_image" :alt="post.title + ' 封面图'" class="detail__cover-img" />
            <div class="detail__cover-mask"></div>
          </div>

          <div class="detail__hero-content" :class="{ 'detail__hero-content--with-cover': post.cover_image }">
            <div class="detail__meta">
              <span class="detail__category">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                {{ post.category?.name || 'uncategorized' }}
              </span>
              <span class="detail__dot"></span>
              <span class="detail__meta-item">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                {{ formatDate(post.published_at) }}
              </span>
              <span class="detail__dot"></span>
              <span class="detail__meta-item">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                {{ post.reading_time }}
              </span>
            </div>

            <h1 class="detail__title">{{ post.title }}</h1>
            <p class="detail__summary" v-if="post.summary">{{ post.summary }}</p>

            <div class="detail__tags" v-if="post.tags.length">
              <span v-for="tag in post.tags" :key="tag.id" class="detail__tag">{{ tag.name }}</span>
            </div>
          </div>
        </header>

        <!-- Article body -->
        <section class="detail__content prose" v-html="renderedHtml"></section>

        <!-- Share section -->
        <div class="detail__share">
          <span class="detail__share-label">分享：</span>
          <button class="detail__share-btn" @click="copyPostLink" :title="'复制链接'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            <span class="detail__share-text">{{ linkCopied ? '已复制!' : '复制链接' }}</span>
          </button>
          <a class="detail__share-btn" :href="`https://twitter.com/intent/tweet?url=${encodeURIComponent(currentUrl)}&text=${encodeURIComponent(post.title)}`" target="_blank" rel="noopener">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"/></svg>
            <span class="detail__share-text">Twitter</span>
          </a>
          <a class="detail__share-btn" :href="`https://service.weibo.com/share/share.php?url=${encodeURIComponent(currentUrl)}&title=${encodeURIComponent(post.title)}`" target="_blank" rel="noopener">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M10.098 20.323c-3.977.391-7.414-1.406-7.672-4.02-.259-2.609 2.759-5.047 6.74-5.441 3.979-.394 7.413 1.404 7.671 4.018.259 2.6-2.759 5.049-6.739 5.443zm7.782-8.063c-.39-.116-.656-.195-.453-.703.443-1.106.489-2.063.009-2.745-.898-1.276-3.353-1.209-6.193-.034 0 0-.889.395-.661-.321.434-1.399.369-2.571-.309-3.246-1.545-1.536-5.661.058-9.19 3.558C-1.881 11.194-3.1 14.826-3.1 17.994c0 6.199 7.947 9.973 15.73 9.973 10.218 0 17.026-5.938 17.026-10.652 0-2.853-2.408-4.47-4.776-5.055z"/></svg>
            <span class="detail__share-text">微博</span>
          </a>
        </div>

        <!-- Bottom nav -->
        <div class="detail__bottom-nav">
          <RouterLink to="/posts" class="detail__back">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
            返回文章列表
          </RouterLink>
        </div>

        <!-- Related Posts -->
        <section class="detail__related" v-if="relatedPosts.length">
          <h3 class="detail__related-title">相关文章</h3>
          <div class="detail__related-grid">
            <RouterLink
              v-for="rp in relatedPosts"
              :key="rp.id"
              :to="`/posts/${rp.slug}`"
              class="detail__related-card"
            >
              <h4 class="detail__related-card-title">{{ rp.title }}</h4>
              <p class="detail__related-card-summary">{{ rp.summary }}</p>
              <span class="detail__related-card-meta">{{ formatDate(rp.published_at) }} &middot; {{ rp.reading_time }}</span>
            </RouterLink>
          </div>
        </section>

        <!-- Comments -->
        <CommentSection
          :post-id="post.id"
          :is-logged-in="authStore.isLoggedIn"
          :user-id="authStore.user?.id"
        />
      </div>

      <!-- Right sidebar: TOC -->
      <aside class="detail__sidebar" v-if="headings.length">
        <div class="detail__toc">
          <h4 class="detail__toc-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
            目录
          </h4>
          <nav class="detail__toc-list">
            <a
              v-for="h in headings"
              :key="h.id"
              :href="'#' + h.id"
              class="detail__toc-item"
              :class="{ 'detail__toc-item--active': activeHeading === h.id, 'detail__toc-item--h3': h.level === 3 }"
              @click.prevent="scrollTo(h.id)"
            >{{ h.text }}</a>
          </nav>
        </div>
      </aside>
    </div>
  </article>

  <div v-else-if="loading" class="detail__loading">
    <div class="article-container">
      <div class="detail__skeleton detail__skeleton--title"></div>
      <div class="detail__skeleton detail__skeleton--text"></div>
      <div class="detail__skeleton detail__skeleton--text short"></div>
    </div>
  </div>

  <div v-else class="detail__empty">
    <div class="article-container detail__empty-inner">
      <h1 class="detail__empty-title">404</h1>
      <p class="detail__empty-text">{{ errorMessage || '请求的内容不存在或 API 不可用' }}</p>
      <RouterLink to="/posts" class="detail__back">返回文章列表</RouterLink>
    </div>
  </div>

  <!-- Lightbox -->
  <Teleport to="body">
    <Transition name="lightbox">
      <div v-if="lightboxSrc" class="lightbox-overlay" @click="closeLightbox">
        <img :src="lightboxSrc" class="lightbox-img" @click.stop />
        <button class="lightbox-close" @click="closeLightbox">&times;</button>
      </div>
    </Transition>
  </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getPostBySlug, getRelatedPosts } from '@/api/blog'
import { isAxiosError } from '@/api/http'
import { renderMarkdown } from '@/utils/markdown'
import { useAuthStore } from '@/stores/auth'
import { useSeo } from '@/composables/useSeo'
import CommentSection from '@/components/blog/CommentSection.vue'
import type { PostDetail, PostSummary } from '@/types/blog'

const route = useRoute()
const authStore = useAuthStore()
useSeo()

const post = ref<PostDetail | null>(null)
const relatedPosts = ref<PostSummary[]>([])
const loading = ref(true)
const errorMessage = ref('')
const activeHeading = ref('')
const lightboxSrc = ref<string | null>(null)
const readProgress = ref(0)
const linkCopied = ref(false)
const currentUrl = ref('')

const renderedHtml = computed(() => renderMarkdown(post.value?.content_markdown || ''))

interface Heading { id: string; text: string; level: number }

const headings = computed<Heading[]>(() => {
  if (!post.value) return []
  const html = renderedHtml.value
  const result: Heading[] = []
  const re = /<h([23])[^>]*id="([^"]*)"[^>]*>(.*?)<\/h[23]>/gi
  let m
  while ((m = re.exec(html)) !== null) {
    result.push({ level: parseInt(m[1]), id: m[2], text: m[3].replace(/<[^>]+>/g, '') })
  }
  return result
})

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric'
  })
}

function scrollTo(id: string) {
  const el = document.getElementById(id)
  if (el) {
    const y = el.getBoundingClientRect().top + window.scrollY - 80
    window.scrollTo({ top: y, behavior: 'smooth' })
  }
}

function updateActiveHeading() {
  for (let i = headings.value.length - 1; i >= 0; i--) {
    const el = document.getElementById(headings.value[i].id)
    if (el && el.getBoundingClientRect().top <= 100) {
      activeHeading.value = headings.value[i].id
      return
    }
  }
  activeHeading.value = headings.value[0]?.id || ''

  // Update reading progress
  const article = document.querySelector('.detail__content')
  if (article) {
    const rect = article.getBoundingClientRect()
    const scrolled = -rect.top
    const total = rect.height - window.innerHeight + 200
    readProgress.value = Math.min(100, Math.max(0, (scrolled / total) * 100))
  }
}

function copyPostLink() {
  currentUrl.value = window.location.href
  navigator.clipboard.writeText(window.location.href)
  linkCopied.value = true
  setTimeout(() => { linkCopied.value = false }, 2000)
}

let _scrollTicking = false
function onScroll() {
  if (_scrollTicking) return
  _scrollTicking = true
  requestAnimationFrame(() => {
    updateActiveHeading()
    _scrollTicking = false
  })
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  document.querySelectorAll('script[type="application/ld+json"]').forEach(el => el.remove())
})

// Enhance content with copy buttons and lightbox
function enhanceContent() {
  nextTick(() => {
    // Add copy buttons and language labels to code blocks
    document.querySelectorAll('.detail__content pre').forEach((pre) => {
      if (pre.querySelector('.code-copy-btn')) return
      const code = pre.querySelector('code')
      const btn = document.createElement('button')
      btn.className = 'code-copy-btn'
      btn.textContent = '复制'
      btn.addEventListener('click', async () => {
        const text = code ? code.textContent : pre.textContent
        if (text) {
          await navigator.clipboard.writeText(text)
          btn.textContent = '已复制!'
          setTimeout(() => { btn.textContent = '复制' }, 2000)
        }
      })
      ;(pre as HTMLElement).style.position = 'relative'
      pre.appendChild(btn)

      // Add language label
      if (code) {
        const cls = code.className || ''
        const langMatch = cls.match(/language-(\w+)/)
        if (langMatch) {
          const label = document.createElement('span')
          label.className = 'code-lang-label'
          label.textContent = langMatch[1]
          pre.appendChild(label)
        }
      }
    })

    // Add lightbox + lazy loading to images
    document.querySelectorAll('.detail__content img').forEach((img) => {
      if ((img as HTMLElement).dataset.lightboxEnabled) return
      ;(img as HTMLElement).dataset.lightboxEnabled = '1'
      ;(img as HTMLImageElement).loading = 'lazy'
      ;(img as HTMLElement).style.cursor = 'zoom-in'
      img.addEventListener('click', () => {
        lightboxSrc.value = (img as HTMLImageElement).src
      })
    })
  })
}

function closeLightbox() {
  lightboxSrc.value = null
}

watch(renderedHtml, enhanceContent)

async function loadPost(slug: string) {
  loading.value = true
  errorMessage.value = ''
  post.value = null
  relatedPosts.value = []
  window.scrollTo({ top: 0, behavior: 'auto' })

  try {
    post.value = await getPostBySlug(slug)
    if (post.value) {
      document.title = `${post.value.title} — minlan01`
      route.meta.postTitle = post.value.title
      route.meta.postDescription = post.value.summary
      route.meta.postImage = post.value.cover_image || undefined
      useSeo({
        title: post.value.title,
        description: post.value.summary,
        image: post.value.cover_image || undefined,
        type: 'article',
      })

      // Inject JSON-LD structured data
      injectJsonLd(post.value)

      // Load related posts
      try {
        relatedPosts.value = await getRelatedPosts(slug)
      } catch {
        // Non-critical, ignore
      }
    }
  } catch (error: any) {
    if (isAxiosError(error)) {
      if (error.response?.status === 404) {
        errorMessage.value = '文章不存在或链接已失效'
      } else {
        errorMessage.value = error.response?.data?.detail || '请求失败，请稍后重试'
      }
    } else {
      errorMessage.value = '发生未知错误，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

function injectJsonLd(p: PostDetail) {
  // Remove existing JSON-LD
  document.querySelectorAll('script[type="application/ld+json"]').forEach(el => el.remove())

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: p.title,
    description: p.summary,
    datePublished: p.published_at,
    author: {
      '@type': 'Person',
      name: 'minlan01',
    },
    publisher: {
      '@type': 'Person',
      name: 'minlan01',
    },
    mainEntityOfPage: window.location.href,
    ...(p.cover_image ? { image: p.cover_image } : {}),
    ...(p.category ? { articleSection: p.category.name } : {}),
    keywords: p.tags?.map(t => t.name).join(', ') || '',
  }

  const script = document.createElement('script')
  script.type = 'application/ld+json'
  script.textContent = JSON.stringify(jsonLd).replace(/<\/script/gi, '<\\/script')
  document.head.appendChild(script)
}

watch(
  () => route.params.slug,
  (slug) => {
    if (typeof slug === 'string' && slug) {
      loadPost(slug)
    }
  },
  { immediate: true }
)
</script>

<style scoped>
/* ========================================
   Layout
   ======================================== */
.detail {
  padding: var(--space-lg) 0 var(--space-3xl);
}

.detail__wrap {
  width: min(1240px, calc(100% - 32px));
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 220px;
  gap: var(--space-xl);
  align-items: start;
}

.detail__main {
  min-width: 0;
  background: var(--glass-panel-bg) !important;
  backdrop-filter: var(--glass-panel-blur) saturate(var(--glass-panel-saturate)) !important;
  -webkit-backdrop-filter: var(--glass-panel-blur) saturate(var(--glass-panel-saturate)) !important;
  border: 1px solid var(--glass-panel-border);
  border-radius: var(--radius-xl);
  padding: var(--space-xl) var(--space-xl) var(--space-lg);
  position: relative;
  overflow: hidden;
  box-shadow: var(--glass-panel-glow);
}

.detail__main::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--glass-noise);
  background-size: 128px 128px;
  pointer-events: none;
  z-index: 0;
}

.detail__main > * {
  position: relative;
  z-index: 1;
}

/* Nav */
.detail__nav {
  margin-bottom: var(--space-md);
}

.detail__back {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-muted);
  transition: all var(--duration-fast) ease;
  text-decoration: none;
}

.detail__back:hover {
  color: var(--color-accent);
}

.detail__back svg {
  transition: transform var(--duration-fast) ease;
}

.detail__back:hover svg {
  transform: translateX(-2px);
}

/* ========================================
   Hero
   ======================================== */
.detail__hero {
  margin-bottom: var(--space-xl);
}

.detail__cover {
  margin: 0 calc(-1 * var(--space-xl)) var(--space-xl);
  height: 280px;
  position: relative;
  overflow: hidden;
}

.detail__cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail__cover-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(15, 15, 30, 0.72) 0%, transparent 60%);
}

.detail__hero-content--with-cover {
  margin-top: calc(-1 * var(--space-lg));
}

.detail__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  margin-bottom: var(--space-md);
  flex-wrap: wrap;
}

.detail__category {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--color-accent);
  font-weight: 500;
}

.detail__category svg { opacity: 0.7; }

.detail__dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--color-text-muted);
  opacity: 0.4;
}

.detail__meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.detail__meta-item svg { opacity: 0.5; }

.detail__title {
  font-family: var(--font-display);
  font-size: clamp(1.6rem, 4vw, 2.4rem);
  line-height: 1.25;
  margin: 0 0 var(--space-md);
  color: var(--color-text-heading);
  font-weight: 700;
  letter-spacing: -0.01em;
}

.detail__summary {
  font-size: 0.95rem;
  color: var(--color-text-soft);
  line-height: 1.8;
  margin: 0 0 var(--space-md);
  padding-left: var(--space-md);
  border-left: 3px solid var(--color-accent);
}

.detail__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail__tag {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  padding: 4px 12px;
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  transition: all var(--duration-fast) ease;
}

.detail__tag::before {
  content: '#';
  color: var(--color-accent);
  opacity: 0.6;
  margin-right: 2px;
}

.detail__tag:hover {
  border-color: var(--accent-tint-30);
  color: var(--color-accent);
}

/* ========================================
   Prose — Article Content
   ======================================== */
.detail__content {
  padding-bottom: var(--space-2xl);
  line-height: 1.9;
  font-size: 0.95rem;
}

.detail__content :deep(h2) {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-text-heading);
  margin: var(--space-2xl) 0 var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 2px solid var(--color-accent);
  position: relative;
}

.detail__content :deep(h3) {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin: var(--space-xl) 0 var(--space-sm);
  padding-left: 12px;
  border-left: 3px solid var(--color-accent);
}

.detail__content :deep(h4) {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin: var(--space-lg) 0 var(--space-sm);
}

.detail__content :deep(p) {
  color: var(--color-text);
  line-height: 2;
  margin: 0 0 var(--space-lg);
}

.detail__content :deep(strong) {
  color: var(--color-text-heading);
  font-weight: 600;
}

.detail__content :deep(em) {
  color: var(--color-accent-2);
  font-style: italic;
}

.detail__content :deep(ul),
.detail__content :deep(ol) {
  color: var(--color-text);
  line-height: 2;
  padding-left: var(--space-lg);
  margin: 0 0 var(--space-lg);
}

.detail__content :deep(li) {
  margin-bottom: 6px;
}

.detail__content :deep(li)::marker {
  color: var(--color-accent);
}

.detail__content :deep(a) {
  color: var(--color-accent);
  text-decoration: underline;
  text-underline-offset: 3px;
  text-decoration-color: var(--accent-tint-40);
  transition: all var(--duration-fast) ease;
}

.detail__content :deep(a:hover) {
  text-decoration-color: var(--color-accent);
}

.detail__content :deep(code) {
  font-family: var(--font-mono);
  font-size: 0.85em;
}

.detail__content :deep(p code),
.detail__content :deep(li code) {
  background: var(--accent-tint-10);
  padding: 2px 8px;
  border-radius: 4px;
  color: var(--color-accent-2);
  border: 1px solid var(--accent-tint-15);
}

.detail__content :deep(pre) {
  margin: var(--space-lg) 0;
  padding: var(--space-lg);
  border-radius: var(--radius-md);
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--glass-border);
  overflow-x: auto;
  font-size: 0.85rem;
  line-height: 1.7;
}

.detail__content :deep(pre code) {
  background: none;
  border: none;
  padding: 0;
  color: var(--color-text);
}

.detail__content :deep(blockquote) {
  margin: var(--space-lg) 0;
  padding: var(--space-md) var(--space-lg);
  border-left: 3px solid var(--color-accent);
  background: var(--color-surface);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--color-text-soft);
  font-style: italic;
}

.detail__content :deep(blockquote p) {
  margin: 0;
}

.detail__content :deep(hr) {
  border: none;
  height: 1px;
  background: var(--color-border);
  margin: var(--space-xl) 0;
}

.detail__content :deep(img) {
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border);
  margin: var(--space-lg) 0;
}

.detail__content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-lg) 0;
  font-size: 0.88rem;
}

.detail__content :deep(th),
.detail__content :deep(td) {
  padding: 10px 14px;
  border: 1px solid var(--glass-border);
  text-align: left;
}

.detail__content :deep(th) {
  background: var(--color-surface);
  font-weight: 600;
  color: var(--color-text-heading);
}

.detail__content :deep(td) {
  color: var(--color-text);
}

/* Bottom nav */
.detail__bottom-nav {
  padding: var(--space-lg) 0;
  border-top: 1px solid var(--color-border);
}

/* ========================================
   Sidebar TOC
   ======================================== */
.detail__sidebar {
  position: sticky;
  top: calc(var(--header-height) + var(--space-lg));
}

.detail__toc {
  padding: var(--space-md);
  background: var(--glass-card-bg) !important;
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate)) !important;
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate)) !important;
  border: 1px solid var(--glass-panel-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--glass-card-shadow);
}

.detail__toc-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin: 0 0 var(--space-sm);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

.detail__toc-title svg {
  color: var(--color-accent);
  opacity: 0.6;
}

.detail__toc-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.detail__toc-item {
  display: block;
  padding: 5px 8px;
  font-size: 0.78rem;
  color: var(--color-text-muted);
  text-decoration: none;
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast) ease;
  line-height: 1.4;
  border-left: 2px solid transparent;
}

.detail__toc-item--h3 {
  padding-left: 20px;
}

.detail__toc-item:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.detail__toc-item--active {
  color: var(--color-accent);
  border-left-color: var(--color-accent);
  background: var(--accent-tint-08);
}

/* ========================================
   Empty / Loading
   ======================================== */
.detail__loading,
.detail__empty {
  min-height: 50vh;
  padding: var(--space-3xl) 0;
}

.detail__empty-inner {
  text-align: center;
}

.detail__empty-title {
  font-family: var(--font-display);
  font-size: clamp(2rem, 5vw, 3rem);
  margin: 0 0 var(--space-md);
  color: var(--color-accent);
  font-weight: 600;
}

.detail__empty-text {
  margin: 0 0 var(--space-lg);
  color: var(--color-text-soft);
  font-size: 0.95rem;
  max-width: 480px;
  margin-inline: auto;
  line-height: 1.8;
}

.detail__skeleton {
  border-radius: var(--radius-sm);
  background: var(--color-bg-soft);
}

.detail__skeleton--title {
  width: min(600px, 100%);
  height: 44px;
  margin: var(--space-2xl) 0 var(--space-lg);
}

.detail__skeleton--text {
  width: min(700px, 100%);
  height: 16px;
  margin-bottom: 12px;
}

.detail__skeleton--text.short {
  width: min(400px, 80%);
}

/* ========================================
   Responsive
   ======================================== */
@media (max-width: 960px) {
  .detail__wrap {
    grid-template-columns: 1fr;
  }

  .detail__sidebar {
    display: none;
  }

  .detail__main {
    padding: var(--space-lg) var(--space-lg) 0;
  }

  .detail__cover {
    margin: calc(-1 * var(--space-lg));
    margin-bottom: var(--space-lg);
    height: 200px;
  }
}

@media (max-width: 640px) {
  .detail__main {
    padding: var(--space-md) var(--space-md) 0;
    border-radius: var(--radius-md);
  }

  .detail__cover {
    margin: calc(-1 * var(--space-md));
    margin-bottom: var(--space-md);
    height: 160px;
  }

  .detail__title {
    font-size: 1.35rem;
  }

  .detail__content {
    font-size: 0.9rem;
  }

  .detail__content :deep(pre) {
    padding: var(--space-md);
    font-size: 0.8rem;
    border-radius: var(--radius-sm);
  }

  .detail__content :deep(h2) {
    font-size: 1.2rem;
  }

  .detail__content :deep(h3) {
    font-size: 1.05rem;
  }
}

/* ========================================
   Code Copy Button
   ======================================== */
.detail__content :deep(.code-copy-btn) {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 12px;
  border: 1px solid var(--border-strong);
  border-radius: 4px;
  background: var(--border-strong);
  color: var(--color-text-muted);
  font-size: 0.72rem;
  font-family: var(--font-mono);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  z-index: 2;
}

.detail__content :deep(.code-copy-btn:hover) {
  background: var(--border-strong);
  color: var(--color-text);
}

/* ========================================
   Lightbox
   ======================================== */
.lightbox-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(20px);
}

.lightbox-img {
  max-width: 92vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: var(--radius-md);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.lightbox-close {
  position: absolute;
  top: 20px;
  right: 24px;
  background: none;
  border: 1px solid var(--border-heavy-2);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 1.4rem;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.lightbox-close:hover {
  background: var(--border-medium);
}

.lightbox-enter-active,
.lightbox-leave-active {
  transition: opacity 0.2s ease;
}

.lightbox-enter-from,
.lightbox-leave-to {
  opacity: 0;
}

/* ========================================
   Reading Progress Bar
   ======================================== */
.detail__progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  z-index: 100;
  background: transparent;
}

.detail__progress-fill {
  height: 100%;
  background: var(--color-accent-gradient);
  transition: width 0.1s linear;
  border-radius: 0 2px 2px 0;
}

/* ========================================
   Share Section
   ======================================== */
.detail__share {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-lg) 0;
  border-top: 1px solid var(--color-border);
}

.detail__share-label {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

.detail__share-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text-soft);
  font-size: 0.82rem;
  cursor: pointer;
  text-decoration: none;
  transition: all var(--duration-fast) ease;
}

.detail__share-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.detail__share-text {
  font-size: 0.78rem;
}

/* ========================================
   Related Posts
   ======================================== */
.detail__related {
  padding: var(--space-xl) 0;
  border-top: 1px solid var(--color-border);
}

.detail__related-title {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin: 0 0 var(--space-lg);
}

.detail__related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--space-md);
}

.detail__related-card {
  display: block;
  padding: var(--space-md);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  text-decoration: none;
  transition: all var(--duration-fast) ease;
}

.detail__related-card:hover {
  border-color: var(--color-accent);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.detail__related-card-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text-heading);
  margin: 0 0 var(--space-xs);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.detail__related-card-summary {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  margin: 0 0 var(--space-sm);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.detail__related-card-meta {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  opacity: 0.7;
}

/* ========================================
   Code Language Label
   ======================================== */
.detail__content :deep(.code-lang-label) {
  position: absolute;
  top: 8px;
  left: 12px;
  font-size: 0.68rem;
  font-family: var(--font-mono);
  color: var(--color-text-muted);
  opacity: 0.6;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  pointer-events: none;
}
</style>
