import api from './index'

export interface Post {
  id: number
  title: string
  slug: string
  content_md: string | null
  content_html: string | null
  excerpt: string | null
  cover_image: string | null
  status: string
  category: { id: number; name: string; slug: string } | null
  tags: { id: number; name: string; slug: string }[]
  view_count: number
  is_top: boolean
  created_at: string
  updated_at: string
  published_at: string | null
}

export interface PostCreate {
  title: string
  slug?: string
  content_md: string
  excerpt?: string
  cover_image?: string
  category_id?: number
  tag_ids?: number[]
  is_top?: boolean
}

export const postsApi = {
  list: (params?: any) => api.get<{ items: Post[]; total: number }>('/api/v1/admin/posts', { params }),
  get: (slug: string) => api.get<Post>(`/api/v1/posts/${slug}`),
  getById: (id: number) => api.get<Post>(`/api/v1/admin/posts/${id}`),
  create: (data: PostCreate) => api.post<Post>('/api/v1/admin/posts', data),
  update: (id: number, data: Partial<PostCreate>) => api.put<Post>(`/api/v1/admin/posts/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/admin/posts/${id}`),
  publish: (id: number) => api.post<Post>(`/api/v1/admin/posts/${id}/publish`),
  draft: (id: number) => api.post<Post>(`/api/v1/admin/posts/${id}/draft`),
}
