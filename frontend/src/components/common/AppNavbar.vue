<template>
  <header class="navbar" :class="{ 'navbar--scrolled': scrolled }">
    <div class="container navbar__inner">
      <a class="navbar__brand" href="/" @click.prevent="goHome">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        赤夜冥岚的编程小屋
      </a>

      <!-- Desktop nav -->
      <nav class="navbar__nav">
        <RouterLink to="/" class="navbar__link">首页</RouterLink>
        <RouterLink to="/archive" class="navbar__link">归档</RouterLink>
        <RouterLink to="/posts" class="navbar__link">文章</RouterLink>
        <RouterLink to="/link" class="navbar__link">友链</RouterLink>
        <RouterLink to="/message-board" class="navbar__link">留言板</RouterLink>
        <RouterLink to="/ai-chat" class="navbar__link">AI</RouterLink>
        <RouterLink to="/about" class="navbar__link">关于</RouterLink>
      </nav>

      <div class="navbar__actions">
        <button class="navbar__theme-btn" @click="toggleTheme" :title="mode === 'dark' ? '暗色模式 → 亮色模式' : mode === 'light' ? '亮色模式 → 自动模式' : '自动模式 → 暗色模式'">
          <!-- Dark mode: moon -->
          <svg v-if="mode === 'dark'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          <!-- Light mode: sun -->
          <svg v-else-if="mode === 'light'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
          <!-- Auto mode: sun-half -->
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v1m0 16v1m8.66-13.5l-.87.5M4.21 17l-.87.5M20.66 17.5l-.87-.5M4.21 7l-.87-.5M21 12h-1M4 12H3"/><circle cx="12" cy="12" r="4"/><path d="M12 8a4 4 0 0 1 0 8z"/></svg>
        </button>

        <!-- Always-visible search -->
        <div class="navbar__search">
          <svg class="navbar__search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            v-model="searchQuery"
            class="navbar__search-input"
            placeholder="搜索..."
            aria-label="搜索文章"
            @keydown.enter="doSearch"
          />
        </div>

        <RouterLink v-if="!isLoggedIn" to="/login" class="navbar__login-btn">登录</RouterLink>
        <div v-else class="navbar__user-menu">
          <RouterLink to="/profile" class="navbar__user-link">{{ username }}</RouterLink>
          <RouterLink v-if="isAdmin" to="/admin" class="navbar__admin-btn">管理</RouterLink>
          <button class="navbar__logout-btn" @click="handleLogout">退出</button>
        </div>
        <button class="navbar__hamburger" @click="mobileOpen = !mobileOpen" aria-label="菜单">
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>

    <!-- Mobile menu -->
    <Transition name="mobile-menu">
      <div v-if="mobileOpen" class="navbar__mobile-menu">
        <div class="navbar__mobile-search">
          <svg class="navbar__mobile-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            v-model="searchQuery"
            placeholder="搜索文章..."
            aria-label="搜索文章"
            @keydown.enter="doSearch"
          />
        </div>
        <RouterLink to="/" class="navbar__mobile-link" @click="mobileOpen = false">首页</RouterLink>
        <RouterLink to="/archive" class="navbar__mobile-link" @click="mobileOpen = false">归档</RouterLink>
        <RouterLink to="/posts" class="navbar__mobile-link" @click="mobileOpen = false">文章</RouterLink>
        <RouterLink to="/link" class="navbar__mobile-link" @click="mobileOpen = false">友链</RouterLink>
        <RouterLink to="/message-board" class="navbar__mobile-link" @click="mobileOpen = false">留言板</RouterLink>
        <RouterLink to="/ai-chat" class="navbar__mobile-link" @click="mobileOpen = false">AI</RouterLink>
        <RouterLink to="/about" class="navbar__mobile-link" @click="mobileOpen = false">关于</RouterLink>

        <div class="navbar__mobile-divider"></div>
        <button class="navbar__mobile-link" @click="toggleTheme">
          {{ mode === 'dark' ? '暗色模式' : mode === 'light' ? '亮色模式' : '自动模式' }} — 点击切换
        </button>
        <RouterLink v-if="!isLoggedIn" to="/login" class="navbar__mobile-link" @click="mobileOpen = false">登录</RouterLink>
        <RouterLink v-if="isLoggedIn" to="/profile" class="navbar__mobile-link" @click="mobileOpen = false">个人资料</RouterLink>
        <RouterLink v-if="isAdmin" to="/admin" class="navbar__mobile-link" @click="mobileOpen = false">后台管理</RouterLink>
        <button v-if="isLoggedIn" class="navbar__mobile-link navbar__mobile-logout" @click="handleLogout">退出登录</button>
      </div>
    </Transition>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSiteStore } from '@/stores/site'
import { useTheme } from '@/composables/useTheme'

defineProps<{
  isLoggedIn?: boolean
  username?: string
  isAdmin?: boolean
}>()

const emit = defineEmits<{
  (e: 'logout'): void
}>()

const siteStore = useSiteStore()
const router = useRouter()
const { theme, mode, toggle } = useTheme()

const scrolled = ref(false)
const mobileOpen = ref(false)
const searchQuery = ref('')

function toggleTheme() {
  toggle()
}

function handleScroll() {
  scrolled.value = window.scrollY > 10
}

function doSearch() {
  if (searchQuery.value.trim()) {
    router.push({ path: '/search', query: { q: searchQuery.value.trim() } })
    mobileOpen.value = false
  }
}

function handleLogout() {
  mobileOpen.value = false
  emit('logout')
}

function goHome() {
  mobileOpen.value = false
  router.push('/')
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  document.addEventListener('click', handleOutsideClick)
})
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.removeEventListener('click', handleOutsideClick)
})

function handleOutsideClick(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (mobileOpen.value && !target.closest('.navbar')) {
    mobileOpen.value = false
  }
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  height: var(--header-height);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur) saturate(1.6);
  -webkit-backdrop-filter: var(--glass-blur) saturate(1.6);
  border-bottom: 1px solid var(--glass-border);
  transition: all var(--duration-fast) ease;
  box-shadow: var(--glass-highlight);
}

.navbar--scrolled {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  border-bottom-color: var(--glass-border-highlight);
}

.navbar__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  gap: var(--space-lg);
}

.navbar__brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--color-accent);
  transition: opacity var(--duration-fast) ease;
  text-decoration: none;
  flex-shrink: 0;
}

.navbar__brand:hover {
  opacity: 0.85;
}

.navbar__brand svg {
  opacity: 0.8;
}

/* Nav links */
.navbar__nav {
  display: flex;
  align-items: center;
  gap: 12px;
}

.navbar__link {
  font-size: 0.92rem;
  font-weight: 500;
  color: var(--color-text-soft);
  padding: 8px 20px;
  border-radius: var(--radius-sm);
  position: relative;
  transition: all var(--duration-fast) ease;
  text-decoration: none;
  white-space: nowrap;
}

.navbar__link:hover,
.navbar__link.router-link-active {
  color: var(--color-text-heading);
  background: var(--color-surface-hover);
}

.navbar__link.router-link-exact-active {
  color: var(--color-accent);
}

/* Search */
.navbar__search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 18px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  transition: border-color var(--duration-fast) ease;
}

.navbar__search:focus-within {
  border-color: var(--color-accent);
}

.navbar__search-icon {
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.navbar__search-input {
  width: 180px;
  border: none;
  background: transparent;
  color: var(--color-text);
  font-size: 0.85rem;
  font-family: inherit;
  outline: none;
}

.navbar__search-input::placeholder {
  color: var(--color-text-muted);
}

/* Actions */
.navbar__actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.navbar__theme-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.navbar__theme-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.navbar__login-btn {
  font-size: 0.85rem;
  font-weight: 500;
  padding: 8px 24px;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-full);
  color: var(--color-text-soft);
  text-decoration: none;
  transition: all var(--duration-fast) ease;
}

.navbar__login-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: var(--accent-tint-06);
}

.navbar__user-menu {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.navbar__user-link {
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--color-accent);
  text-decoration: none;
}

.navbar__admin-btn {
  font-size: 0.8rem;
  font-weight: 500;
  padding: 7px 16px;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-full);
  color: var(--color-accent);
  text-decoration: none;
  transition: all var(--duration-fast) ease;
}

.navbar__admin-btn:hover {
  background: var(--accent-tint-10);
  border-color: var(--color-accent);
}

.navbar__logout-btn {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  transition: color var(--duration-fast) ease;
}

.navbar__logout-btn:hover {
  color: var(--color-ochre);
}

.navbar__hamburger {
  display: none;
  flex-direction: column;
  gap: 5px;
  width: 24px;
  padding: 2px 0;
}

.navbar__hamburger span {
  display: block;
  width: 100%;
  height: 2px;
  background: var(--color-text);
  border-radius: 1px;
  transition: transform var(--duration-fast) ease, opacity var(--duration-fast) ease;
}

/* Mobile menu */
.navbar__mobile-menu {
  display: none;
  flex-direction: column;
  padding: var(--space-md);
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-toolbar-blur) saturate(var(--glass-toolbar-saturate));
  -webkit-backdrop-filter: var(--glass-toolbar-blur) saturate(var(--glass-toolbar-saturate));
  border-bottom: 1px solid var(--color-border);
}

[data-theme="light"] .navbar__mobile-menu {
  background: rgba(255, 255, 255, 0.92);
}

.navbar__mobile-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: var(--space-sm) var(--space-md);
  margin-bottom: var(--space-xs);
}

.navbar__mobile-search-icon {
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.navbar__mobile-search input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: border-color var(--duration-fast) ease;
}

.navbar__mobile-search input:focus {
  border-color: var(--color-accent);
}

.navbar__mobile-link {
  display: block;
  padding: var(--space-sm) var(--space-md);
  font-size: 0.92rem;
  color: var(--color-text-soft);
  text-align: left;
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast) ease;
  text-decoration: none;
}

.navbar__mobile-link:hover {
  background: var(--color-surface-hover);
  color: var(--color-text-heading);
}

.navbar__mobile-logout {
  background: none;
  border: none;
  width: 100%;
  cursor: pointer;
  color: var(--color-text-muted);
}

.navbar__mobile-divider {
  height: 1px;
  background: var(--color-border);
  margin: var(--space-sm) 0;
}

.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ========================================
   Responsive breakpoints
   ======================================== */

/* Tablet — compact but still visible nav */
@media (max-width: 1100px) {
  .navbar__nav {
    gap: 4px;
  }

  .navbar__link {
    padding: 6px 12px;
    font-size: 0.85rem;
  }

  .navbar__search-input {
    width: 110px;
  }

  .navbar__search {
    padding: 5px 12px;
  }
}

/* Small tablet — collapse to hamburger */
@media (max-width: 768px) {
  .navbar__nav { display: none; }
  .navbar__user-menu { display: none; }
  .navbar__search { display: none; }
  .navbar__hamburger { display: flex; }
  .navbar__mobile-menu { display: flex; }
}
</style>
