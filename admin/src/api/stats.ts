import api from './index'

export interface StatsOverview {
  today_pv: number
  total_posts: number
  total_comments: number
}

export interface TrendPoint {
  date: string
  page_views: number
  unique_visitors: number
}

export const statsApi = {
  getOverview: () => api.get<StatsOverview>('/api/v1/admin/stats'),
  getTrend: (days: number = 7) => api.get<{ data: TrendPoint[] }>('/api/v1/admin/stats/trend', { params: { days } }),
}
