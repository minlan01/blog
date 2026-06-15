<template>
  <AnimatedBackground />
  <a href="#main-content" class="skip-link">跳到主要内容</a>
  <div class="shell">
    <AppNavbar
      :is-logged-in="authStore.isLoggedIn"
      :username="authStore.username"
      :is-admin="authStore.isAdmin"
      @logout="handleLogout"
    />

    <main id="main-content" class="shell__main">
      <RouterView v-slot="{ Component, route }">
        <Transition name="page-fade">
          <component :is="Component" :key="route.path" />
        </Transition>
      </RouterView>
    </main>

    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import AppNavbar from '@/components/common/AppNavbar.vue'
import AppFooter from '@/components/common/AppFooter.vue'
import AnimatedBackground from '@/components/common/AnimatedBackground.vue'
import { useSiteStore } from '@/stores/site'
import { useAuthStore } from '@/stores/auth'

const siteStore = useSiteStore()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
}

onMounted(() => {
  siteStore.loadProfile()
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
