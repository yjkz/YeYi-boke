import api from './index'

export interface SiteConfig {
  site_title: string
  site_subtitle: string
  logo_url: string
  avatar_url: string
  favicon_url: string
  about_content: string
  footer_text: string
  social_links: Record<string, string>
  comment_enabled: boolean
  comment_need_review: boolean
}

export const configApi = {
  get: () => api.get<SiteConfig>('/api/v1/site/config'),
  update: (data: Partial<SiteConfig>) => api.put<SiteConfig>('/api/v1/admin/site/config', data),
}
