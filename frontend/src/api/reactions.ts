import { http } from './http'
import type { PostSummary } from '@/types/blog'

export interface ReactionSummary {
  type: 'like' | 'bookmark'
  count: number
  user_reacted: boolean
}

export interface PostReactions {
  post_id: number
  like: ReactionSummary
  bookmark: ReactionSummary
}

/** Get reaction counts for a post (and whether current user reacted) */
export async function getPostReactions(postId: number): Promise<PostReactions> {
  const { data } = await http.get<PostReactions>(`/posts/${postId}/reactions`)
  return data
}

/** Toggle like / bookmark (idempotent) */
export async function toggleReaction(postId: number, type: 'like' | 'bookmark'): Promise<ReactionSummary> {
  const { data } = await http.post<ReactionSummary>(`/posts/${postId}/reactions`, { type })
  return data
}

/** Get current user's bookmarked posts */
export async function getMyBookmarks(): Promise<PostSummary[]> {
  const { data } = await http.get<PostSummary[]>('/posts/me/bookmarks')
  return data
}

// ── Comment emoji reactions ──

export interface CommentReactionGroup {
  emoji: string
  count: number
  user_reacted: boolean
}

export async function getCommentReactions(commentId: number): Promise<CommentReactionGroup[]> {
  const { data } = await http.get<CommentReactionGroup[]>(`/comments/${commentId}/reactions`)
  return data
}

export async function toggleCommentReaction(commentId: number, emoji: string): Promise<CommentReactionGroup | null> {
  const { data } = await http.post<CommentReactionGroup | null>(`/comments/${commentId}/reactions`, { emoji })
  return data
}
