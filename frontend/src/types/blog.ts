export interface Category {
  id: number
  name: string
  slug: string
  description?: string | null
}

export interface Tag {
  id: number
  name: string
  slug: string
}

export interface PostSummary {
  id: number
  title: string
  slug: string
  summary: string
  cover_image?: string | null
  reading_time: string
  published_at: string
  updated_at?: string | null
  is_featured: boolean
  view_count: number
  status: string
  category?: Category | null
  tags: Tag[]
}

export interface PostDetail extends PostSummary {
  content_markdown: string
}

export interface SiteProfile {
  site_name: string
  hero_title: string
  hero_subtitle: string
  intro_text: string
  avatar: string
  email: string
  github_url: string
  location: string
  icp_filing?: string
  icp_link?: string
}

export interface User {
  id: number
  username: string
  email?: string | null
  role: string
  bio?: string | null
  avatar?: string | null
  email_verified?: boolean
  created_at: string
}

export interface CommentRead {
  id: number
  content: string
  post_id: number
  user_id: number | null
  parent_id: number | null
  is_approved: boolean
  created_at: string
  author_name: string | null
  replies: CommentRead[]
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface FriendLink {
  id: number
  name: string
  url: string
  avatar?: string | null
  description?: string | null
  category: string
  badge?: string | null
  sort_order: number
  is_active: boolean
  created_at: string
}
