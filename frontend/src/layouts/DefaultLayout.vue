<template>
  <AnimatedBackground />
  <a href="#main-content" class="skip-link">跳到主要内容</a>
  <div class="shell">
    <AppNavbar
      :is-logged-in="authStore.isLoggedIn"
      :username="authStore.username"
      :is-admin="authStore.isAdmin"
      :avatar="(authStore.user as any)?.avatar"
      @logout="handleLogout"
    />

    <main id="main-content" class="shell__main">
      <RouterView v-slot="{ Component, route }">
        <Transition name="page-fade" mode="out-in">
          <component :is="Component" :key="route.path" />
        </Transition>
      </RouterView>
    </main>

    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '@/components/common/AppNavbar.vue'
import AppFooter from '@/components/common/AppFooter.vue'
import AnimatedBackground from '@/components/common/AnimatedBackground.vue'
import { useSiteStore } from '@/stores/site'
import { useAuthStore } from '@/stores/auth'
import { http } from '@/api/http'

const siteStore = useSiteStore()
const authStore = useAuthStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
}

// 访问统计：路由切换后静默上报
function trackPage(path: string) {
  // 忽略管理后台页面（不统计自己人的操作）
  if (path.startsWith('/admin') || path.startsWith('/login') || path.startsWith('/register')) return
  // navigator.sendBeacon 静默发送，不阻塞、不等待
  const payload = JSON.stringify({ path, referrer: document.referrer || '' })
  try {
    navigator.sendBeacon('/api/v1/track', new Blob([payload], { type: 'application/json' }))
  } catch {
    // fallback：sendBeacon 不可用时用 fetch fire-and-forget
    http.post('/track', { path, referrer: document.referrer || '' }).catch(() => {})
  }
}

function onKeydown(e: KeyboardEvent) {
  // 忽略输入框内的按键
  const tag = (e.target as HTMLElement)?.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || (e.target as HTMLElement)?.isContentEditable) return

  // / 聚焦搜索
  if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
    e.preventDefault()
    const searchInput = document.querySelector<HTMLInputElement>('.navbar__search-input')
    if (searchInput) {
      searchInput.focus()
    } else {
      // 移动端：打开汉堡菜单后聚焦
      const mobileInput = document.querySelector<HTMLInputElement>('.navbar__mobile-search input')
      mobileInput?.focus()
    }
  }
  // g 回首页
  if (e.key === 'g' && !e.ctrlKey && !e.metaKey) {
    router.push('/')
  }
}

onMounted(() => {
  siteStore.loadProfile()
  document.addEventListener('keydown', onKeydown)
  // 首次加载上报
  trackPage(router.currentRoute.value.path)
  // 路由切换上报
  router.afterEach((to) => {
    trackPage(to.path)
  })
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.shell {
  min-height: 100vh;
}

.shell__main {
  position: relative;
  min-height: calc(100vh - var(--header-height) - 80px);
}

.skip-link {
  position: absolute;
  top: -100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 20px;
  background: var(--color-accent);
  color: #fff;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  z-index: 9999;
  text-decoration: none;
  transition: top 0.2s ease;
}

.skip-link:focus {
  top: 0;
}
</style>
