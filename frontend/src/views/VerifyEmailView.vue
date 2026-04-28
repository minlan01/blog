<template>
  <section class="auth-page">
    <div class="container">
      <div class="auth-page__card">
        <div class="auth-page__body" style="text-align: center;">
          <template v-if="loading">
            <div class="auth-page__spinner"></div>
            <p>验证中...</p>
          </template>
          <template v-else-if="verified">
            <div class="auth-page__check">&#10003;</div>
            <h1 class="auth-page__title">邮箱验证成功</h1>
            <p class="auth-page__subtitle">你的邮箱已成功验证</p>
            <RouterLink to="/" class="auth-page__submit" style="display:inline-block; text-decoration:none; margin-top: var(--space-md);">
              返回首页
            </RouterLink>
          </template>
          <template v-else>
            <div class="auth-page__cross">&#10007;</div>
            <h1 class="auth-page__title">验证失败</h1>
            <p class="auth-page__subtitle">{{ error }}</p>
            <RouterLink to="/" class="auth-page__submit" style="display:inline-block; text-decoration:none; margin-top: var(--space-md);">
              返回首页
            </RouterLink>
          </template>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { verifyEmail } from '@/api/auth'

const route = useRoute()
const loading = ref(true)
const verified = ref(false)
const error = ref('')

onMounted(async () => {
  const token = route.query.token as string
  if (!token) {
    error.value = '缺少验证令牌'
    loading.value = false
    return
  }
  try {
    await verifyEmail(token)
    verified.value = true
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '验证链接无效或已过期'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.auth-page {
  padding: var(--space-3xl) 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}
.auth-page > .container {
  background: none;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  border: none;
  padding: 0;
  border-radius: 0;
}
.auth-page__card {
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--glass-card-bg);
  backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  -webkit-backdrop-filter: var(--glass-card-blur) saturate(var(--glass-card-saturate));
  box-shadow: var(--shadow-elevated);
  overflow: hidden;
}
.auth-page__body { padding: var(--space-2xl); }
.auth-page__title { font-size: 1.5rem; margin: var(--space-sm) 0 var(--space-xs); color: var(--color-text-heading); }
.auth-page__subtitle { color: var(--color-text-muted); font-size: 0.85rem; }
.auth-page__submit { padding: 10px 24px; border: none; border-radius: var(--radius-sm); background: var(--color-accent-gradient); color: #fff; font-weight: 600; font-size: 0.9rem; cursor: pointer; text-decoration: none; }
.auth-page__check { font-size: 3rem; color: #4ade80; }
.auth-page__cross { font-size: 3rem; color: #f87171; }
.auth-page__spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto var(--space-md);
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
