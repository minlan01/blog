import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

// Mock the API module
vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  register: vi.fn(),
  getProfile: vi.fn(),
  forgotPassword: vi.fn(),
  resetPassword: vi.fn(),
  verifyEmail: vi.fn(),
  getGithubLoginUrl: vi.fn(() => '/api/v1/auth/github'),
}))

import { login as apiLogin, getProfile } from '@/api/auth'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('starts with no user', () => {
    const store = useAuthStore()
    expect(store.isLoggedIn).toBe(false)
    expect(store.user).toBeNull()
  })

  it('login stores token and fetches profile', async () => {
    const mockLogin = vi.mocked(apiLogin)
    const mockProfile = vi.mocked(getProfile)

    mockLogin.mockResolvedValue({
      access_token: 'test-token',
      refresh_token: 'test-refresh',
      token_type: 'bearer',
    })
    mockProfile.mockResolvedValue({
      id: 1,
      username: 'testuser',
      role: 'user',
      bio: null,
      avatar: null,
      email_verified: false,
      created_at: '2024-01-01T00:00:00Z',
    })

    const store = useAuthStore()
    await store.login('testuser', 'password')

    expect(store.isLoggedIn).toBe(true)
    expect(store.username).toBe('testuser')
    expect(localStorage.getItem('token')).toBe('test-token')
    expect(localStorage.getItem('refresh_token')).toBe('test-refresh')
  })

  it('logout clears state and storage', async () => {
    const mockLogin = vi.mocked(apiLogin)
    const mockProfile = vi.mocked(getProfile)

    mockLogin.mockResolvedValue({
      access_token: 'token',
      refresh_token: 'refresh',
      token_type: 'bearer',
    })
    mockProfile.mockResolvedValue({
      id: 1,
      username: 'test',
      role: 'user',
      bio: null,
      avatar: null,
      email_verified: false,
      created_at: '2024-01-01T00:00:00Z',
    })

    const store = useAuthStore()
    await store.login('test', 'pass')
    store.logout()

    expect(store.isLoggedIn).toBe(false)
    expect(store.user).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })

  it('isAdmin checks role', async () => {
    const mockLogin = vi.mocked(apiLogin)
    const mockProfile = vi.mocked(getProfile)

    mockLogin.mockResolvedValue({
      access_token: 'admin-token',
      refresh_token: 'admin-refresh',
      token_type: 'bearer',
    })
    mockProfile.mockResolvedValue({
      id: 1,
      username: 'admin',
      role: 'super_admin',
      bio: null,
      avatar: null,
      email_verified: true,
      created_at: '2024-01-01T00:00:00Z',
    })

    const store = useAuthStore()
    await store.login('admin', 'pass')
    expect(store.isAdmin).toBe(true)
  })
})
