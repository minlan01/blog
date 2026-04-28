import axios from 'axios'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
})

// Simple in-memory cache for GET requests
const apiCache = new Map<string, { data: any; expiry: number }>()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

const CACHEABLE_PATTERNS = ['/categories', '/tags', '/site/profile', '/stats']

// Request interceptor: attach JWT token + cache check
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers = config.headers || {}
    config.headers['Authorization'] = `Bearer ${token}`
  }

  // Return cached response for cacheable GET requests
  if (config.method === 'get' && config.url) {
    const key = config.url + JSON.stringify(config.params || '')
    const isCacheable = CACHEABLE_PATTERNS.some(p => config.url!.startsWith(p))
    if (isCacheable) {
      const cached = apiCache.get(key)
      if (cached && Date.now() < cached.expiry) {
        const source = axios.CancelToken.source()
        config.cancelToken = source.token
        source.cancel(JSON.stringify({ __cached: cached.data }))
      }
    }
  }

  return config
})

// Response interceptor: cache storage + auto-refresh token on 401
let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

function onRefreshed(token: string) {
  refreshSubscribers.forEach(cb => cb(token))
  refreshSubscribers = []
}

http.interceptors.response.use(
  (response) => {
    // Store in cache if cacheable GET
    if (response.config.method === 'get' && response.config.url) {
      const key = response.config.url + JSON.stringify(response.config.params || '')
      const isCacheable = CACHEABLE_PATTERNS.some(p => response.config.url!.startsWith(p))
      if (isCacheable) {
        apiCache.set(key, { data: response.data, expiry: Date.now() + CACHE_TTL })
      }
    }
    return response
  },
  async (error) => {
    // Handle cached responses
    if (axios.isCancel(error)) {
      const msg = error.message || ''
      try {
        const parsed = JSON.parse(msg)
        if (parsed.__cached !== undefined) {
          return { data: parsed.__cached, status: 200, config: {}, headers: {} }
        }
      } catch {}
    }

    if (axios.isAxiosError(error)) {
      const status = error.response?.status
      const url = error.config?.url || ''
      const originalRequest = error.config as any

      // Auto-refresh token on 401
      if (status === 401 && originalRequest && !originalRequest._retry && !url.includes('/auth/')) {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken && !isRefreshing) {
          originalRequest._retry = true
          isRefreshing = true

          try {
            const { data } = await axios.post(
              (import.meta.env.VITE_API_BASE_URL || '/api/v1') + '/auth/refresh',
              { refresh_token: refreshToken }
            )
            localStorage.setItem('token', data.access_token)
            localStorage.setItem('refresh_token', data.refresh_token)
            onRefreshed(data.access_token)
            originalRequest.headers.Authorization = `Bearer ${data.access_token}`
            return http(originalRequest)
          } catch {
            // Refresh failed, logout
            localStorage.removeItem('token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
          } finally {
            isRefreshing = false
          }
        }

        // Queue request while refreshing
        if (isRefreshing) {
          return new Promise((resolve) => {
            refreshSubscribers.push((token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(http(originalRequest))
            })
          })
        }
      }

      if (!error.response) {
        console.warn(`[API] 网络不可达: ${url}`)
      } else if (status === 404) {
        // 404 是正常业务状态，不需要警告
      } else if (status && status >= 500) {
        console.error(`[API] 服务端错误 ${status}: ${url}`)
      }
    }
    return Promise.reject(error)
  }
)

/**
 * 安全地调用 API，失败时返回 fallback 值而非抛出
 * 用于页面初始化时的非关键数据加载
 */
export async function safeCall<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await fn()
  } catch {
    return fallback
  }
}
