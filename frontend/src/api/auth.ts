import { http } from './http'
import type { User } from '@/types/blog'

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export async function login(username: string, password: string): Promise<TokenResponse> {
  const { data } = await http.post<TokenResponse>('/auth/login', { username, password })
  return data
}

export async function register(username: string, password: string, email?: string): Promise<User> {
  const { data } = await http.post<User>('/auth/register', { username, password, email })
  return data
}

export async function getProfile(): Promise<User> {
  const { data } = await http.get<User>('/auth/me')
  return data
}

export async function forgotPassword(email: string): Promise<{ message: string }> {
  const { data } = await http.post<{ message: string }>('/auth/forgot-password', { email })
  return data
}

export async function resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
  const { data } = await http.post<{ message: string }>('/auth/reset-password', {
    token,
    new_password: newPassword,
  })
  return data
}

export async function verifyEmail(token: string): Promise<{ message: string }> {
  const { data } = await http.post<{ message: string }>('/auth/verify-email', { token })
  return data
}

export function getGithubLoginUrl(): string {
  const base = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  return `${base}/auth/github`
}
