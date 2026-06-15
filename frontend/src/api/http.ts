import axios from 'axios'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
})

const apiCache = new Map<string, { data: any; expiry: number }>()
const CACHE_TTL = 5 * 60 * 1000
const MAX_CACHE_SIZE = 50

function cleanupCache() {
  const now = Date.now()
  for (const [key, entry] of apiCache) {
    if (now >= entry.expiry) {
      apiCache.delete(key)
    }
  }
}

const CACHEABLE_PATTERNS = ['/categories', '/tags', '/site/profile', '/stats']

function getCacheKey(config: any): string | null {
  if (config.method !== 'get' || !config.url) return null
  if (!CACHEABLE_PATTERNS.some(p => config.url!.startsWith(p))) return null
  return config.url + JSON.stringify(config.params || '')
}

const pendingRequests = new Map<string, Promise<any>>()

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers = config.headers || {}
    config.headers['Authorization'] = `Bearer ${token}`
  }

  const cacheKey = getCacheKey(config)
  if (cacheKey) {
    const cached = apiCache.get(cacheKey)
    if (cached && Date.now() < cached.expiry) {
      const adapter = config.adapter
      config.adapter = () => {
        return Promise.resolve({
          data: cached.data,
          status: 200,
          statusText: 'OK',
          config,
          headers: {},
        })
      }
      return config
    }

    const pending = pendingRequests.get(cacheKey)
    if (pending) {
      const adapter = config.adapter
      config.adapter = () => {
        return pending.then((response: any) => ({
          data: response.data,
          status: response.status,
          statusText: response.statusText,
          config,
          headers: response.headers,
        }))
      }
      return config
    }

    const originalAdapter = config.adapter
    config.adapter = (config) => {
      const promise = (originalAdapter || axios.defaults.adapter)!(config)
      pendingRequests.set(cacheKey!, promise as Promise<any>)
      return (promise as Promise<any>).finally(() => {
        pendingRequests.delete(cacheKey!)
      })
    }
  }

  return config
})

let isRefreshing = false
let refreshSubscribers: Array<{ resolve: (token: string) => void; reject: (err: any) => void }> = []

function onRefreshed(token: string) {
  refreshSubscribers.forEach(cb => cb.resolve(token))
  refreshSubscribers = []
}

function onRefreshFailed(err: any) {
  refreshSubscribers.forEach(cb => cb.reject(err))
  refreshSubscribers = []
}

http.interceptors.response.use(
  (response) => {
    const cacheKey = getCacheKey(response.config)
    if (cacheKey) {
      cleanupCache()
      if (apiCache.size >= MAX_CACHE_SIZE) {
        const oldest = apiCache.keys().next().value
        if (oldest !== undefined) apiCache.delete(oldest)
      }
      apiCache.set(cacheKey, { data: response.data, expiry: Date.now() + CACHE_TTL })
    }
    return response
  },
  async (error) => {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status
      const url = error.config?.url || ''
      const originalRequest = error.config as any

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
          } catch (refreshErr) {
            onRefreshFailed(refreshErr)
            localStorage.removeItem('token')
            localStorage.removeItem('refresh_token')
            // Give user feedback before redirecting
            sessionStorage.setItem('auth_expired', '1')
            window.location.href = '/login'
          } finally {
            isRefreshing = false
          }
        }

        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            refreshSubscribers.push({ resolve, reject })
          }).then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return http(originalRequest)
          })
        }
      }

      if (!error.response) {
        console.warn(`[API] 网络不可达: ${url}`)
      } else if (status === 404) {
      } else if (status && status >= 500) {
        console.error(`[API] 服务端错误 ${status}: ${url}`)
      }
    }
    return Promise.reject(error)
  }
)

export async function safeCall<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await fn()
  } catch {
    return fallback
  }
}

export function isAxiosError(error: unknown): boolean {
  return axios.isAxiosError(error)
}
