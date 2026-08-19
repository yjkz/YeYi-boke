interface SiteConfig {
  site_title: string
  site_subtitle: string
  logo_url: string
  avatar_url: string
  favicon_url: string
  footer_text: string
  social_links: Record<string, string>
  comment_enabled: boolean
  comment_need_review: boolean
}

const siteConfig = ref<SiteConfig | null>(null)

export function useSiteConfig() {
  const api = useApi()

  const fetchConfig = async () => {
    if (!siteConfig.value) {
      siteConfig.value = await api.get<SiteConfig>('/site/config')
    }
    return siteConfig.value
  }

  return { siteConfig, fetchConfig }
}
