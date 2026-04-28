import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getSiteProfile } from '@/api/blog'
import type { SiteProfile } from '@/types/blog'

export const useSiteStore = defineStore('site', () => {
  const profile = ref<SiteProfile | null>(null)
  const loading = ref(false)
  const error = ref(false)

  /* 站点统计 */
  const postCount = ref(0)
  const tagCount = ref(0)
  const categoryCount = ref(0)

  function setStats(stats: { posts: number; tags: number; categories: number }) {
    postCount.value = stats.posts
    tagCount.value = stats.tags
    categoryCount.value = stats.categories
  }

  async function loadProfile(force = false) {
    if (profile.value && !force) return
    loading.value = true
    error.value = false
    try {
      profile.value = await getSiteProfile()
    } catch {
      error.value = true
      console.warn('[SiteStore] 站点信息加载失败，后端可能未启动')
    } finally {
      loading.value = false
    }
  }

  return { profile, loading, error, loadProfile, postCount, tagCount, categoryCount, setStats }
})
