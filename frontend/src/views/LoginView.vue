<template>
  <section class="auth-page">
    <div class="container">
      <div class="auth-page__card">
        <div class="auth-page__body">
          <h1 class="auth-page__title">登录</h1>
          <p class="auth-page__subtitle">登录后即可发表评论</p>

          <div v-if="error" class="auth-page__error">{{ error }}</div>

          <form class="auth-page__form" @submit.prevent="handleLogin">
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
              <input v-model="password" type="password" class="auth-page__input" required autocomplete="current-password" placeholder="输入密码" />
            </div>
            <button type="submit" class="auth-page__submit" :disabled="submitting || !!usernameError">
              {{ submitting ? '登录中...' : '登录' }}
            </button>
          </form>

          <p class="auth-page__switch">
            还没有账号？<RouterLink to="/register">注册</RouterLink>
            <span class="auth-page__divider">|</span>
            <RouterLink to="/forgot-password">忘记密码？</RouterLink>
          </p>

          <div class="auth-page__divider-line">
            <span>或</span>
          </div>

          <a :href="githubLoginUrl" class="auth-page__github-btn">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            使用 GitHub 登录
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getGithubLoginUrl } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const githubLoginUrl = getGithubLoginUrl()

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

async function handleLogin() {
  if (!/^[a-zA-Z0-9]+$/.test(username.value)) {
    error.value = 'Username can only contain letters and numbers'
    return
  }
  error.value = ''
  submitting.value = true
  try {
    await authStore.login(username.value, password.value)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Login failed. Check your credentials.'
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

.auth-page__divider {
  margin: 0 var(--space-xs);
  color: var(--color-text-muted);
  opacity: 0.4;
}

.auth-page__divider-line {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin: var(--space-lg) 0;
  color: var(--color-text-muted);
  font-size: 0.8rem;
}
.auth-page__divider-line::before,
.auth-page__divider-line::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--color-border);
}

.auth-page__github-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg-deep);
  color: var(--color-text);
  font-size: 0.88rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}
.auth-page__github-btn:hover {
  border-color: var(--color-accent);
  background: var(--accent-tint-10);
}

/* Responsive */
@media (max-width: 768px) {
  .auth-page {
    padding: var(--space-xl) 0;
    min-height: 50vh;
  }

  .auth-page__card {
    max-width: 100%;
  }

  .auth-page__body {
    padding: var(--space-xl);
  }
}

@media (max-width: 480px) {
  .auth-page__body {
    padding: var(--space-lg);
  }

  .auth-page__input {
    padding: 8px 12px;
    font-size: 0.85rem;
  }

  .auth-page__submit {
    padding: 10px;
    font-size: 0.85rem;
  }
}
</style>
