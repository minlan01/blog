import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { http } from '@/api/http'
import { login as apiLogin, register as apiRegister, getProfile } from '@/api/auth'
import type { User } from '@/types/blog'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'super_admin')
  const username = computed(() => user.value?.username ?? '')

  async function login(usernameInput: string, password: string) {
    const data = await apiLogin(usernameInput, password)
    token.value = data.access_token
    sessionStorage.setItem('token', data.access_token)
    // refresh_token 现在由后端通过 httpOnly cookie 设置，前端不再持有
    await fetchProfile()
  }

  async function register(payload: {
    username: string
    password: string
    confirm_password: string
    email?: string
    captcha_answer: number
    captcha_token: string
    captcha_ts: number
  }) {
    await apiRegister(payload)
    await login(payload.username, payload.password)
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      user.value = await getProfile()
    } catch {
      clearLocal()
    }
  }

  function setUser(updated: User) {
    user.value = updated
  }

  // 仅清理前端状态（不调用后端）
  function clearLocal() {
    token.value = null
    user.value = null
    sessionStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 完整登出：调用后端清除 cookie + 服务端 token，再清理前端状态
  async function logout() {
    try {
      await http.post('/auth/logout', {}, { withCredentials: true })
    } catch {
      // 后端调用失败也继续清理前端状态
    }
    clearLocal()
  }

  // Auto-restore session from sessionStorage on init
  const stored = sessionStorage.getItem('token')
  if (stored) {
    token.value = stored
    fetchProfile()
  }

  return { token, user, isLoggedIn, isAdmin, username, login, register, logout, fetchProfile, setUser }
})
