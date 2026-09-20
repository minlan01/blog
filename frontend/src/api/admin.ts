import { http } from './http'
import type { PostDetail, PostSummary, Category, Tag, SiteProfile, FriendLink, User, CommentRead } from '@/types/blog'

// ── Posts ──

export async function getAdminPosts(): Promise<PostSummary[]> {
  const { data } = await http.get<PostSummary[]>('/admin/posts')
  return data
}

export interface PostCreatePayload {
  title: string
  slug: string
  summary: string
  content_markdown: string
  cover_image?: string
  reading_time?: string
  is_featured?: boolean
  category_id?: number | null
  tag_ids?: number[]
  status?: string
}

export type PostUpdatePayload = Partial<PostCreatePayload> & {
  is_featured?: boolean
  featured_order?: number
  status?: string
}

export async function createPost(data: PostCreatePayload) {
  const { data: result } = await http.post<PostDetail>('/admin/posts', data)
  return result
}

export async function updatePost(id: number, data: PostUpdatePayload) {
  const { data: result } = await http.put<PostDetail>(`/admin/posts/${id}`, data)
  return result
}

export async function deletePost(id: number) {
  await http.delete(`/admin/posts/${id}`)
}

// ── Categories ──

export interface CategoryPayload {
  name: string
  slug: string
  description?: string
}

export async function createCategory(data: CategoryPayload) {
  const { data: result } = await http.post<Category>('/admin/categories', data)
  return result
}

export async function updateCategory(id: number, data: Partial<CategoryPayload>) {
  const { data: result } = await http.put<Category>(`/admin/categories/${id}`, data)
  return result
}

export async function deleteCategory(id: number) {
  await http.delete(`/admin/categories/${id}`)
}

// ── Tags ──

export interface TagPayload {
  name: string
  slug: string
}

export async function createTag(data: TagPayload) {
  const { data: result } = await http.post<Tag>('/admin/tags', data)
  return result
}

export async function updateTag(id: number, data: Partial<TagPayload>) {
  const { data: result } = await http.put<Tag>(`/admin/tags/${id}`, data)
  return result
}

export async function deleteTag(id: number) {
  await http.delete(`/admin/tags/${id}`)
}

// ── Site ──

export async function updateSiteProfile(data: Partial<SiteProfile>) {
  const { data: result } = await http.put<SiteProfile>('/admin/site/profile', data)
  return result
}

// ── Friend Links ──

export interface FriendLinkPayload {
  name: string
  url: string
  avatar?: string | null
  description?: string | null
  category?: string
  badge?: string | null
  sort_order?: number
  is_active?: boolean
}

export async function createFriendLink(data: FriendLinkPayload) {
  const { data: result } = await http.post<FriendLink>('/admin/friend-links', data)
  return result
}

export async function updateFriendLink(id: number, data: Partial<FriendLinkPayload>) {
  const { data: result } = await http.put<FriendLink>(`/admin/friend-links/${id}`, data)
  return result
}

export async function deleteFriendLink(id: number) {
  await http.delete(`/admin/friend-links/${id}`)
}

// ── Users ──

export async function getUsers(): Promise<User[]> {
  const { data } = await http.get<User[]>('/admin/users')
  return data
}

export async function updateUser(id: number, data: { role?: string; bio?: string; avatar?: string; new_password?: string }) {
  const { data: result } = await http.put<User>(`/admin/users/${id}`, data)
  return result
}

export async function deleteUser(id: number) {
  await http.delete(`/admin/users/${id}`)
}

// ── Comments (Admin) ──

export async function getAdminComments(postId?: number): Promise<CommentRead[]> {
  const { data } = await http.get<CommentRead[]>('/admin/comments', { params: postId ? { post_id: postId } : {} })
  return data
}

export async function approveComment(id: number) {
  const { data } = await http.put<CommentRead>(`/admin/comments/${id}/approve`)
  return data
}

export async function adminDeleteComment(id: number) {
  await http.delete(`/admin/comments/${id}`)
}

// ── Messages (Admin) ──

export interface AdminMessageRead {
  id: number
  name: string
  email?: string | null
  content: string
  color: string
  parent_id?: number | null
  admin_reply?: string | null
  admin_reply_at?: string | null
  status?: string
  created_at: string
}

export async function getAdminMessages(): Promise<AdminMessageRead[]> {
  const { data } = await http.get<AdminMessageRead[]>('/admin/messages')
  return data
}

export async function replyMessage(id: number, content: string): Promise<AdminMessageRead> {
  const { data } = await http.put<AdminMessageRead>(`/admin/messages/${id}/reply`, { content })
  return data
}

export async function updateMessageStatus(id: number, status: string): Promise<AdminMessageRead> {
  const { data } = await http.put<AdminMessageRead>(`/admin/messages/${id}/status`, { status })
  return data
}

export async function adminDeleteMessage(id: number) {
  await http.delete(`/admin/messages/${id}`)
}

// ── Images (Media Library) ──

export interface ImageItem {
  id: number
  filename: string
  url: string
  size: number
  mime_type?: string
  media_type?: 'image' | 'video' | 'music' | 'audio'
  uploaded_by?: string
  created_at: string
}

export async function getImages(): Promise<ImageItem[]> {
  const { data } = await http.get<ImageItem[]>('/upload')
  return data
}

export interface MusicTrack {
  id: number
  filename: string
  url: string
}

export async function getMusicTracks(): Promise<MusicTrack[]> {
  const { data } = await http.get<MusicTrack[]>('/upload/music')
  return data
}

export async function deleteImage(id: number) {
  await http.delete(`/upload/${id}`)
}

export async function updateImage(id: number, data: { filename: string }) {
  const { data: result } = await http.put<ImageItem>(`/upload/${id}`, data)
  return result
}

// ── Batch Operations ──

export async function batchDeletePosts(ids: number[]) {
  await http.post('/admin/posts/batch-delete', { ids })
}

export async function batchActionComments(ids: number[], action: 'approve' | 'delete') {
  const { data } = await http.post('/admin/comments/batch-action', { ids, action })
  return data
}

// ── Post Revisions ──

export interface PostRevision {
  id: number
  post_id: number
  title: string
  summary?: string
  version_number: number
  created_at: string
}

export interface PostRevisionDetail extends PostRevision {
  content_markdown: string
}

export async function getPostRevisions(postId: number): Promise<PostRevision[]> {
  const { data } = await http.get<PostRevision[]>(`/admin/posts/${postId}/revisions`)
  return data
}

export async function getPostRevision(postId: number, revId: number): Promise<PostRevisionDetail> {
  const { data } = await http.get<PostRevisionDetail>(`/admin/posts/${postId}/revisions/${revId}`)
  return data
}

export async function restorePostRevision(postId: number, revId: number): Promise<PostDetail> {
  const { data } = await http.post<PostDetail>(`/admin/posts/${postId}/revisions/${revId}/restore`)
  return data
}

// ── Export/Import ──

export async function exportPosts(): Promise<Blob> {
  const { data } = await http.get('/admin/posts/export', { responseType: 'blob' })
  return data
}

export async function importPosts(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await http.post('/admin/posts/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 0,
  })
  return data
}

// ── Pending Comments (Moderation) ──

export async function getPendingComments(): Promise<CommentRead[]> {
  const { data } = await http.get<CommentRead[]>('/admin/comments/pending')
  return data
}

export async function rejectComment(id: number) {
  const { data } = await http.put(`/admin/comments/${id}/reject`)
  return data
}

// ── Upload Image ──

export async function uploadImage(file: File): Promise<ImageItem> {
  // 大文件上传不设超时（视频/音频可能很大）
  const formData = new FormData()
  formData.append('file', file)

  async function doUpload(): Promise<ImageItem> {
    const { data } = await http.post<ImageItem>('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 0,
    })
    return data
  }

  try {
    return await doUpload()
  } catch (e: any) {
    // 401 时 token 可能过期，等 1 秒让拦截器刷新后重试
    if (e?.response?.status === 401) {
      await new Promise(r => setTimeout(r, 1000))
      return await doUpload()
    }
    throw e
  }
}

// ── Personal Access Tokens ──

export interface ApiToken {
  id: number
  name: string
  scopes: string
  expires_at: string | null
  last_used_at: string | null
  created_at: string
  revoked: boolean
}

export interface ApiTokenCreateResponse {
  token: string
  token_info: ApiToken
}

export async function getTokens(): Promise<ApiToken[]> {
  const { data } = await http.get<ApiToken[]>('/tokens')
  return data
}

export async function createToken(payload: { name: string; scopes?: string; expires_in_days?: number }): Promise<ApiTokenCreateResponse> {
  const { data } = await http.post<ApiTokenCreateResponse>('/tokens', payload)
  return data
}

export async function revokeToken(id: number): Promise<void> {
  await http.delete(`/tokens/${id}`)
}
