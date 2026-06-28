export function useVisit() {
  const route = useRoute()
  const api = useApi()

  const recordVisit = () => {
    api.post('/api/v1/visit', {
      page_path: route.fullPath,
      page_title: document.title || null,
    }).catch(() => {})
  }

  return { recordVisit }
}
