import api from './index'

export interface Comment {
  id: number
  post_id: number
  parent_id: number | null
  nickname: string
  email: string | null
  website: string | null
  content: string
  status: string
  visitor_ip: string | null
  created_at: string
}

export const commentsApi = {
  list: (params?: any) => api.get<{ items: Comment[]; total: number }>('/api/v1/admin/comments', { params }),
  updateStatus: (id: number, status: string) => api.put<Comment>(`/api/v1/admin/comments/${id}`, { status }),
  delete: (id: number) => api.delete(`/api/v1/admin/comments/${id}`),
}
