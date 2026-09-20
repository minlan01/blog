import { http } from './http'
import type { User } from '@/types/blog'

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export async function login(username: string, password: string, hcaptchaToken?: string): Promise<TokenResponse> {
  const { data } = await http.post<TokenResponse>('/auth/login', {
    username,
    password,
    hcaptcha_token: hcaptchaToken || undefined,
  })
  return data
}

export async function getHcaptchaConfig(): Promise<{ enabled: boolean; sitekey: string }> {
  const { data } = await http.get('/auth/hcaptcha-config')
  return data
}

export async function register(payload: {
  username: string
  password: string
  confirm_password: string
  email?: string
  captcha_answer: number
  captcha_token: string
  captcha_ts: number
}): Promise<User> {
  const { data } = await http.post<User>('/auth/register', payload)
  return data
}

export async function getRegisterCaptcha(): Promise<{ question: string; token: string; ts: number }> {
  const { data } = await http.get<{ question: string; token: string; ts: number }>('/auth/captcha')
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

export async function changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
  const { data } = await http.post<{ message: string }>('/auth/change-password', {
    old_password: oldPassword,
    new_password: newPassword,
  })
  return data
}

export async function updateMyProfile(payload: { bio?: string; avatar?: string; email?: string }): Promise<User> {
  const { data } = await http.put<User>('/auth/me', payload)
  return data
}

export async function uploadAvatar(file: File): Promise<{ avatar: string }> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await http.post<{ avatar: string }>('/auth/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 0,
  })
  return data
}

export function getGithubLoginUrl(): string {
  const base = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  return `${base}/auth/github`
}
