<template>
  <section class="auth-page">
    <div class="container">
      <div class="auth-page__card">
        <div class="auth-page__body">
          <h1 class="auth-page__title">忘记密码</h1>
          <p class="auth-page__subtitle">输入注册时使用的邮箱，我们将发送重置链接</p>

          <div v-if="sent" class="auth-page__success">
            重置链接已发送到你的邮箱，请查收。
          </div>

          <div v-if="error" class="auth-page__error">{{ error }}</div>

          <form v-if="!sent" class="auth-page__form" @submit.prevent="handleSend">
            <div class="auth-page__field">
              <label class="auth-page__label">邮箱地址</label>
              <input
                v-model="email"
                type="email"
                class="auth-page__input"
                required
                placeholder="your@email.com"
              />
            </div>
            <button type="submit" class="auth-page__submit" :disabled="submitting">
              {{ submitting ? '发送中...' : '发送重置链接' }}
            </button>
          </form>

          <p class="auth-page__switch">
            <RouterLink to="/login">返回登录</RouterLink>
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { forgotPassword } from '@/api/auth'

const email = ref('')
const error = ref('')
const sent = ref(false)
const submitting = ref(false)

async function handleSend() {
  error.value = ''
  submitting.value = true
  try {
    await forgotPassword(email.value)
    sent.value = true
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '发送失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
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
.auth-page__title { font-size: 1.5rem; margin: 0 0 var(--space-xs); color: var(--color-text-heading); }
.auth-page__subtitle { color: var(--color-text-muted); font-size: 0.85rem; margin: 0 0 var(--space-xl); }
.auth-page__error { padding: var(--space-sm) var(--space-md); margin-bottom: var(--space-md); border: 1px solid var(--error-border-30); border-radius: var(--radius-sm); background: var(--error-bg-06); color: var(--error-main); font-size: 0.82rem; }
.auth-page__success { padding: var(--space-sm) var(--space-md); margin-bottom: var(--space-md); border: 1px solid rgba(34,197,94,0.3); border-radius: var(--radius-sm); background: rgba(34,197,94,0.1); color: #4ade80; font-size: 0.82rem; }
.auth-page__form { display: grid; gap: var(--space-lg); }
.auth-page__field { display: grid; gap: var(--space-xs); }
.auth-page__label { font-size: 0.82rem; font-weight: 500; color: var(--color-text-soft); }
.auth-page__input { padding: 10px var(--space-md); border: 1px solid var(--color-border); border-radius: var(--radius-sm); background: var(--color-bg-deep); color: var(--color-text); font-size: 0.88rem; }
.auth-page__input::placeholder { color: var(--color-text-muted); opacity: 0.5; }
.auth-page__input:focus { outline: none; border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--accent-tint-10); }
.auth-page__submit { margin-top: var(--space-sm); padding: 12px; border: none; border-radius: var(--radius-sm); background: var(--color-accent-gradient); color: #fff; font-weight: 600; font-size: 0.9rem; cursor: pointer; }
.auth-page__submit:hover:not(:disabled) { opacity: 0.9; }
.auth-page__submit:disabled { opacity: 0.4; cursor: not-allowed; }
.auth-page__switch { margin-top: var(--space-lg); text-align: center; font-size: 0.82rem; color: var(--color-text-muted); }
.auth-page__switch a { color: var(--color-accent); font-weight: 500; }
</style>
