import api from './index'

export interface Tag { id: number; name: string; slug: string }
export type TagInput = { name: string; slug: string }
export const tagsApi = {
  list: () => api.get<Tag[]>('/api/v1/tags'),
  create: (data: TagInput) => api.post<Tag>('/api/v1/admin/tags', data),
  update: (id: number, data: TagInput) => api.put<Tag>(`/api/v1/admin/tags/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/admin/tags/${id}`),
}
