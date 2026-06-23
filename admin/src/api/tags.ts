import api from './index'

export interface Tag { id: number; name: string; slug: string }
export const tagsApi = {
  list: () => api.get<Tag[]>('/api/v1/tags'),
  create: (data: { name: string; slug: string }) => api.post<Tag>('/api/v1/admin/tags', data),
}
