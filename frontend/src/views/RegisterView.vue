<template>
  <section class="auth-page">
    <div class="container">
      <div class="auth-page__card">
        <div class="auth-page__body">
          <h1 class="auth-page__title">注册</h1>
          <p class="auth-page__subtitle">创建一个新账号</p>

          <div v-if="error" class="auth-page__error">{{ error }}</div>

          <form class="auth-page__form" @submit.prevent="handleRegister">
            <div class="auth-page__field">
              <label class="auth-page__label">用户名</label>
              <input
                v-model="username"
                type="text"
                class="auth-page__input"
                required
                autocomplete="username"
                placeholder="只支持英文和数字"
                @input="validateUsername"
              />
              <span v-if="usernameError" class="auth-page__field-error">{{ usernameError }}</span>
            </div>
            <div class="auth-page__field">
              <label class="auth-page__label">密码</label>
              <input v-model="password" type="password" class="auth-page__input" required autocomplete="new-password" minlength="6" placeholder="至少6位" />
            </div>
            <button type="submit" class="auth-page__submit" :disabled="submitting || !!usernameError">
              {{ submitting ? '注册中...' : '注册' }}
            </button>
          </form>

          <p class="auth-page__switch">
            已有账号？<RouterLink to="/login">登录</RouterLink>
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const usernameError = ref('')
const submitting = ref(false)

function validateUsername() {
  if (!/^[a-zA-Z0-9]*$/.test(username.value)) {
    usernameError.value = 'Username can only contain letters (a-z, A-Z) and numbers (0-9)'
  } else {
    usernameError.value = ''
  }
}

async function handleRegister() {
  if (!/^[a-zA-Z0-9]+$/.test(username.value)) {
    error.value = 'Username can only contain letters and numbers'
    return
  }
  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }
  error.value = ''
  submitting.value = true
  try {
    await authStore.register(username.value, password.value)
    router.push('/')
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Registration failed. Try again.'
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

/* 移除全局毛玻璃（auth-page__card 自带玻璃效果） */
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

.auth-page__body {
  padding: var(--space-2xl);
}

.auth-page__title {
  font-size: 1.5rem;
  margin: 0 0 var(--space-xs);
  color: var(--color-text-heading);
}

.auth-page__subtitle {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin: 0 0 var(--space-xl);
}

.auth-page__error {
  padding: var(--space-sm) var(--space-md);
  margin-bottom: var(--space-md);
  border: 1px solid var(--error-border-30);
  border-radius: var(--radius-sm);
  background: var(--error-bg-06);
  color: var(--error-main);
  font-size: 0.82rem;
}

.auth-page__form {
  display: grid;
  gap: var(--space-lg);
}

.auth-page__field {
  display: grid;
  gap: var(--space-xs);
}

.auth-page__label {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-soft);
}

.auth-page__input {
  padding: 10px var(--space-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg-deep);
  color: var(--color-text);
  font-size: 0.88rem;
  transition: all var(--duration-fast) ease;
}

.auth-page__input::placeholder {
  color: var(--color-text-muted);
  opacity: 0.5;
}

.auth-page__input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--accent-tint-10);
}

.auth-page__field-error {
  font-size: 0.75rem;
  color: var(--error-main);
}

.auth-page__submit {
  margin-top: var(--space-sm);
  padding: 12px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--color-accent-gradient);
  color: #fff;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.auth-page__submit:hover:not(:disabled) {
  opacity: 0.9;
  box-shadow: 0 4px 16px var(--accent-tint-25);
}

.auth-page__submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.auth-page__switch {
  margin-top: var(--space-lg);
  text-align: center;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.auth-page__switch a {
  color: var(--color-accent);
  font-weight: 500;
}
</style>
