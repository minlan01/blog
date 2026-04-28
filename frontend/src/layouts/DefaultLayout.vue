<template>
  <AnimatedBackground />
  <div class="shell">
    <AppNavbar
      :is-logged-in="authStore.isLoggedIn"
      :username="authStore.username"
      :is-admin="authStore.isAdmin"
      @logout="handleLogout"
    />

    <main class="shell__main">
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
</style>
