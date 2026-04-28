<template>
  <section class="auth-page">
    <div class="container">
      <div class="auth-page__card">
        <div class="auth-page__body">
          <h1 class="auth-page__title">重置密码</h1>
          <p class="auth-page__subtitle">输入新密码</p>

          <div v-if="success" class="auth-page__success">
            密码重置成功！<RouterLink to="/login">去登录</RouterLink>
          </div>

          <div v-if="error" class="auth-page__error">{{ error }}</div>

          <form v-if="!success" class="auth-page__form" @submit.prevent="handleReset">
            <div class="auth-page__field">
              <label class="auth-page__label">新密码</label>
              <input v-model="password" type="password" class="auth-page__input" required placeholder="至少8位" />
              <div class="auth-page__strength">
                <div class="auth-page__strength-bar" :style="{ width: strengthPercent + '%' }" :class="strengthClass"></div>
              </div>
              <span v-if="strengthText" class="auth-page__strength-text">{{ strengthText }}</span>
            </div>
            <div class="auth-page__field">
              <label class="auth-page__label">确认密码</label>
              <input v-model="confirmPassword" type="password" class="auth-page__input" required placeholder="再次输入新密码" />
            </div>
            <button type="submit" class="auth-page__submit" :disabled="submitting">
              {{ submitting ? '重置中...' : '重置密码' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { resetPassword } from '@/api/auth'

const route = useRoute()
const token = (route.query.token as string) || ''

const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const success = ref(false)
const submitting = ref(false)

const strengthPercent = computed(() => {
  let score = 0
  if (password.value.length >= 8) score += 25
  if (/[A-Z]/.test(password.value)) score += 25
  if (/[a-z]/.test(password.value)) score += 25
  if (/\d/.test(password.value)) score += 25
  return score
})

const strengthClass = computed(() => {
  if (strengthPercent.value <= 25) return 'weak'
  if (strengthPercent.value <= 50) return 'fair'
  if (strengthPercent.value <= 75) return 'good'
  return 'strong'
})

const strengthText = computed(() => {
  if (!password.value) return ''
  if (strengthPercent.value <= 25) return '弱'
  if (strengthPercent.value <= 50) return '一般'
  if (strengthPercent.value <= 75) return '良好'
  return '强'
})

async function handleReset() {
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  if (password.value.length < 8) {
    error.value = '密码至少需要8位'
    return
  }
  error.value = ''
  submitting.value = true
  try {
    await resetPassword(token, password.value)
    success.value = true
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '重置失败，链接可能已过期'
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
.auth-page__success a { color: var(--color-accent); font-weight: 500; }
.auth-page__form { display: grid; gap: var(--space-lg); }
.auth-page__field { display: grid; gap: var(--space-xs); }
.auth-page__label { font-size: 0.82rem; font-weight: 500; color: var(--color-text-soft); }
.auth-page__input { padding: 10px var(--space-md); border: 1px solid var(--color-border); border-radius: var(--radius-sm); background: var(--color-bg-deep); color: var(--color-text); font-size: 0.88rem; }
.auth-page__input::placeholder { color: var(--color-text-muted); opacity: 0.5; }
.auth-page__input:focus { outline: none; border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--accent-tint-10); }
.auth-page__submit { margin-top: var(--space-sm); padding: 12px; border: none; border-radius: var(--radius-sm); background: var(--color-accent-gradient); color: #fff; font-weight: 600; font-size: 0.9rem; cursor: pointer; }
.auth-page__submit:hover:not(:disabled) { opacity: 0.9; }
.auth-page__submit:disabled { opacity: 0.4; cursor: not-allowed; }
.auth-page__strength { height: 4px; background: var(--color-border); border-radius: 2px; overflow: hidden; }
.auth-page__strength-bar { height: 100%; border-radius: 2px; transition: width 0.3s ease; }
.auth-page__strength-bar.weak { background: #ef4444; }
.auth-page__strength-bar.fair { background: #f59e0b; }
.auth-page__strength-bar.good { background: #3b82f6; }
.auth-page__strength-bar.strong { background: #22c55e; }
.auth-page__strength-text { font-size: 0.75rem; color: var(--color-text-muted); }
</style>
