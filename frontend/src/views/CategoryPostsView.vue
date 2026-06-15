<template>
  <section class="category-posts">
    <div class="container">
      <header class="category-posts__header">
        <span class="category-posts__label">分类</span>
        <h1 class="category-posts__title">{{ categoryName }}</h1>
        <p v-if="categoryDesc" class="category-posts__desc">{{ categoryDesc }}</p>
      </header>

      <div v-if="loadError" class="category-posts__error">{{ loadError }}</div>

      <!-- Loading state -->
      <div v-else-if="!loaded" class="category-posts__loading">
        <div class="category-posts__skeleton" v-for="n in 3" :key="n"></div>
      </div>

      <div class="category-posts__grid" v-else-if="posts.length">
        <PostCard v-for="(post, idx) in posts" :key="post.id" :post="post" :index="idx" />
      </div>

      <div v-else-if="loaded" class="category-posts__empty">
        <p>该分类下暂无文章</p>
        <RouterLink to="/posts" class="category-posts__back">返回文章列表</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import PostCard from '@/components/blog/PostCard.vue'
import { getPosts, getCategories } from '@/api/blog'
import type { PostSummary, Category } from '@/types/blog'

const route = useRoute()

const posts = ref<PostSummary[]>([])
const categories = ref<Category[]>([])
const categoryName = ref('')
const categoryDesc = ref('')
const loaded = ref(false)
const loadError = ref('')

async function loadData(slug: string) {
  loaded.value = false
  try {
    const [postData, cats] = await Promise.all([
      getPosts({ category: slug }),
      getCategories(),
    ])

    if (Array.isArray(postData)) {
      posts.value = postData
    } else {
      posts.value = (postData as any)?.items || []
    }

    categories.value = cats
    const cat = cats.find((c) => c.slug === slug)
    categoryName.value = cat?.name || slug
    categoryDesc.value = cat?.description || ''
  } catch {
    loadError.value = '分类文章加载失败，请刷新页面重试'
  }
  loaded.value = true
}

watch(() => route.params.slug, (slug) => {
  if (slug) loadData(slug as string)
}, { immediate: true })
</script>

<style scoped>
.category-posts {
  padding: var(--space-3xl) 0;
}

.category-posts__header {
  margin-bottom: var(--space-xl);
}

.category-posts__label {
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.category-posts__title {
  font-size: clamp(1.6rem, 3.5vw, 2.2rem);
  margin: var(--space-xs) 0;
}

.category-posts__desc {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin: 0;
}

.category-posts__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(320px, 100%), 1fr));
  gap: var(--space-lg);
}

.category-posts__error {
  text-align: center;
  padding: var(--space-xl);
  color: #e74c3c;
  font-size: 0.92rem;
  background: var(--glass-bg-strong);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
}

.category-posts__loading {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(320px, 100%), 1fr));
  gap: var(--space-lg);
}

.category-posts__skeleton {
  aspect-ratio: 4 / 3;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--glass-border);
}

.category-posts__empty {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-text-muted);
  font-size: 0.88rem;
}

.category-posts__back {
  display: inline-block;
  margin-top: var(--space-md);
  color: var(--color-accent);
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .category-posts__grid {
    grid-template-columns: 1fr;
  }

  .category-posts {
    padding: var(--space-xl) 0;
  }
}
</style>
