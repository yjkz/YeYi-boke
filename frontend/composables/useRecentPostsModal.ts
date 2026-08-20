let recentPostsTrigger: HTMLElement | null = null

export function useRecentPostsModal() {
  const recentPostsOpen = useState('recent-posts-open', () => false)

  const openRecentPosts = (trigger?: EventTarget | null) => {
    recentPostsTrigger = trigger instanceof HTMLElement ? trigger : null
    recentPostsOpen.value = true
  }

  const closeRecentPosts = () => {
    recentPostsOpen.value = false
    nextTick(() => recentPostsTrigger?.focus())
  }

  return { recentPostsOpen, openRecentPosts, closeRecentPosts }
}
