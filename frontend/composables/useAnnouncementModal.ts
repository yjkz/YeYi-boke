let announcementTrigger: HTMLElement | null = null

export function useAnnouncementModal() {
  const announcementContent = useState('announcement-content', () => '')
  const announcementOpen = useState('announcement-open', () => false)

  const openAnnouncement = (content: string, trigger?: EventTarget | null) => {
    if (!content.trim()) return
    announcementContent.value = content
    announcementTrigger = trigger instanceof HTMLElement ? trigger : null
    announcementOpen.value = true
  }

  const closeAnnouncement = () => {
    announcementOpen.value = false
    nextTick(() => announcementTrigger?.focus())
  }

  return {
    announcementContent,
    announcementOpen,
    openAnnouncement,
    closeAnnouncement,
  }
}
