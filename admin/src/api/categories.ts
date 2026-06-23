import api from './index'

export interface Category { id: number; name: string; slug: string; description: string | null; sort_order: number }
export const categoriesApi = {
  list: () => api.get<Category[]>('/api/v1/categories'),
  create: (data: { name: string; slug: string; description?: string }) => api.post<Category>('/api/v1/admin/categories', data),
}
