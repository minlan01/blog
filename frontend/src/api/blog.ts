import { http } from './http'
import type { Category, FriendLink, PaginatedResponse, PostDetail, PostSummary, SiteProfile, Tag } from '@/types/blog'

export async function getSiteProfile() {
  const { data } = await http.get<SiteProfile>('/site/profile')
  return data
}

export async function getPosts(params?: { featured?: boolean; category?: string; tag?: string; search?: string; page?: number; per_page?: number }) {
  const { data } = await http.get<PaginatedResponse<PostSummary>>('/posts', { params })
  return data
}

export async function searchPosts(query: string) {
  const { data } = await http.get('/posts', { params: { search: query } })
  return data
}

export async function getPostBySlug(slug: string) {
  const { data } = await http.get<PostDetail>(`/posts/${slug}`)
  return data
}

export async function getCategories() {
  const { data } = await http.get<Category[]>('/categories')
  return data
}

export async function getTags() {
  const { data } = await http.get<Tag[]>('/tags')
  return data
}

export async function getFriendLinks() {
  const { data } = await http.get<FriendLink[]>('/friend-links')
  return data
}

export interface SiteStats {
  posts: number
  categories: number
  tags: number
  comments: number
  users: number
  messages: number
  friend_links: number
  total_views: number
  total_words: number
}

export async function getStats() {
  const { data } = await http.get<SiteStats>('/stats')
  return data
}

export async function getRelatedPosts(slug: string, limit = 4) {
  const { data } = await http.get<PostSummary[]>(`/posts/${slug}/related`, { params: { limit } })
  return data
}
