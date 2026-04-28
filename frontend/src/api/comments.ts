import { http } from './http'
import type { CommentRead } from '@/types/blog'

interface CommentCreatePayload {
  content: string
  post_id: number
  parent_id?: number | null
}

export async function getComments(postId: number): Promise<CommentRead[]> {
  const { data } = await http.get<CommentRead[]>('/comments', { params: { post_id: postId } })
  return data
}

export async function createComment(payload: CommentCreatePayload): Promise<CommentRead> {
  const { data } = await http.post<CommentRead>('/comments', payload)
  return data
}

export async function deleteComment(commentId: number): Promise<void> {
  await http.delete(`/comments/${commentId}`)
}
