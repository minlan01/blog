import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
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
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    await fetchProfile()
  }

  async function register(usernameInput: string, password: string, email?: string) {
    await apiRegister(usernameInput, password, email)
    await login(usernameInput, password)
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      user.value = await getProfile()
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  // Auto-restore session from localStorage on init
  const stored = localStorage.getItem('token')
  if (stored) {
    token.value = stored
    fetchProfile()
  }

  return { token, user, isLoggedIn, isAdmin, username, login, register, logout, fetchProfile }
})
