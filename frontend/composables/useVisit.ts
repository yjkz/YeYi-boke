export function useVisit() {
  const route = useRoute()
  const api = useApi()

  const recordVisit = () => {
    if (import.meta.server) return
    api.post('/visit', {
      page_path: route.fullPath,
      page_title: document.title || null,
    }).catch(() => {})
  }

  return { recordVisit }
}
