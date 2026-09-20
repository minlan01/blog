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
              <label class="auth-page__label">邮箱</label>
              <input
                v-model="email"
                type="email"
                class="auth-page__input"
                required
                placeholder="your@email.com"
              />
            </div>
            <div class="auth-page__field">
              <label class="auth-page__label">密码</label>
              <div class="auth-page__password-wrap">
                <input v-model="password" :type="showPassword ? 'text' : 'password'" class="auth-page__input" required autocomplete="new-password" minlength="8" placeholder="至少8位，含大小写字母和数字" />
                <button type="button" class="auth-page__password-toggle" @click="showPassword = !showPassword" :title="showPassword ? '隐藏密码' : '显示密码'">
                  <svg v-if="showPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                </button>
              </div>
            </div>
          <div class="auth-page__field-hint">
            密码至少 8 位，需包含大小写字母和数字
          </div>
          <div class="auth-page__field">
            <label class="auth-page__label">确认密码</label>
            <div class="auth-page__password-wrap">
                <input v-model="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" class="auth-page__input" required autocomplete="new-password" placeholder="再次输入密码" />
                <button type="button" class="auth-page__password-toggle" @click="showConfirmPassword = !showConfirmPassword">
                  <svg v-if="showConfirmPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                </button>
              </div>
              <span v-if="confirmPassword && password !== confirmPassword" class="auth-page__field-error">两次密码不一致</span>
            </div>
          <div class="auth-page__field">
            <label class="auth-page__label">验证码</label>
            <div class="auth-page__captcha-row">
              <span class="auth-page__captcha-question">{{ captchaQuestion || '加载中...' }}</span>
              <input
                v-model="captchaAnswer"
                type="text"
                class="auth-page__input auth-page__captcha-input"
                placeholder="答案"
                required
              />
              <button type="button" class="auth-page__captcha-refresh" @click="loadCaptcha" title="换一个">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
              </button>
            </div>
          </div>
          <button type="submit" class="auth-page__submit" :disabled="submitting || !!usernameError || !canSubmit">
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getRegisterCaptcha } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const email = ref('')
const error = ref('')
const usernameError = ref('')
const submitting = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const captchaQuestion = ref('')
const captchaToken = ref('')
const captchaTs = ref(0)
const captchaAnswer = ref('')

const canSubmit = computed(() => {
  return username.value.trim() &&
    email.value.trim() &&
    password.value &&
    confirmPassword.value &&
    password.value === confirmPassword.value &&
    String(captchaAnswer.value).trim()
})

function validateUsername() {
  if (!/^[a-zA-Z0-9]*$/.test(username.value)) {
    usernameError.value = '用户名只能包含英文字母和数字'
  } else {
    usernameError.value = ''
  }
}

function validatePassword(pwd: string): string[] {
  const errors: string[] = []
  if (pwd.length < 8) errors.push('密码至少 8 位')
  if (!/[A-Z]/.test(pwd)) errors.push('需包含大写字母')
  if (!/[a-z]/.test(pwd)) errors.push('需包含小写字母')
  if (!/[0-9]/.test(pwd)) errors.push('需包含数字')
  return errors
}

async function loadCaptcha() {
  try {
    const data = await getRegisterCaptcha()
    captchaQuestion.value = data.question
    captchaToken.value = data.token
    captchaTs.value = data.ts
    captchaAnswer.value = ''
  } catch {
    error.value = '验证码加载失败，请刷新页面'
  }
}

async function handleRegister() {
  if (!/^[a-zA-Z0-9]+$/.test(username.value)) {
    error.value = '用户名只能包含英文字母和数字'
    return
  }
  if (password.value !== confirmPassword.value) {
    error.value = '两次密码不一致'
    return
  }
  const pwdErrors = validatePassword(password.value)
  if (pwdErrors.length) {
    error.value = pwdErrors.join('；')
    return
  }
  error.value = ''
  submitting.value = true
  try {
    await authStore.register({
      username: username.value,
      password: password.value,
      confirm_password: confirmPassword.value,
      email: email.value.trim(),
      captcha_answer: parseInt(captchaAnswer.value, 10),
      captcha_token: captchaToken.value,
      captcha_ts: captchaTs.value,
    })
    router.push('/')
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    if (Array.isArray(detail)) {
      error.value = detail.map((d: any) => d.msg || String(d)).join('；')
    } else {
      error.value = typeof detail === 'string' ? detail : '注册失败，请稍后重试'
    }
    await loadCaptcha()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadCaptcha()
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

.auth-page__field-hint {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  opacity: 0.7;
}

.auth-page__password-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.auth-page__password-wrap .auth-page__input {
  width: 100%;
  padding-right: 40px;
}

.auth-page__password-toggle {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color var(--duration-fast) ease;
}

.auth-page__password-toggle:hover {
  color: var(--color-text);
}

.auth-page__captcha-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.auth-page__captcha-question {
  font-size: 0.9rem;
  font-weight: 600;
  font-family: var(--font-mono);
  color: var(--color-text);
  white-space: nowrap;
  padding: 10px 14px;
  background: var(--glass-bg-04);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
}

.auth-page__captcha-input {
  width: 80px;
  flex-shrink: 0;
  text-align: center;
}

.auth-page__captcha-refresh {
  flex-shrink: 0;
  padding: 8px;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) ease;
}

.auth-page__captcha-refresh:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
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

@media (max-width: 480px) {
  .auth-page__body {
    padding: var(--space-lg);
  }
  .auth-page__captcha-row {
    flex-wrap: wrap;
  }
  .auth-page__captcha-input {
    width: 60px;
  }
}
</style>
