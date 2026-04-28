import { http } from './http'

export interface MessageRead {
  id: number
  name: string
  email?: string | null
  content: string
  color: string
  parent_id?: number | null
  admin_reply?: string | null
  admin_reply_at?: string | null
  created_at: string
  replies: MessageRead[]
}

export async function getMessages(): Promise<MessageRead[]> {
  const { data } = await http.get<MessageRead[]>('/messages')
  return data
}

export async function createMessage(payload: { name: string; email?: string; content: string; parent_id?: number }): Promise<MessageRead> {
  const { data } = await http.post<MessageRead>('/messages', payload)
  return data
}

export async function deleteMessage(messageId: number): Promise<void> {
  await http.delete(`/messages/${messageId}`)
}
