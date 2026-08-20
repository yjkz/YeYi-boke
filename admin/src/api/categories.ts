import api from './index'

export interface Category { id: number; name: string; slug: string; description: string | null; sort_order: number }
export type CategoryInput = { name: string; slug: string; description?: string; sort_order?: number }
export const categoriesApi = {
  list: () => api.get<Category[]>('/api/v1/categories'),
  create: (data: CategoryInput) => api.post<Category>('/api/v1/admin/categories', data),
  update: (id: number, data: CategoryInput) => api.put<Category>(`/api/v1/admin/categories/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/admin/categories/${id}`),
}
