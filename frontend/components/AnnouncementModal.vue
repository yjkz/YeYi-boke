<script setup lang="ts">
import { X } from 'lucide-vue-next'

const { announcementContent, announcementOpen, closeAnnouncement } = useAnnouncementModal()
const closeButton = ref<HTMLButtonElement | null>(null)
let previousOverflow = ''

const onKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') closeAnnouncement()
}

watch(announcementOpen, async (open) => {
  if (import.meta.server) return
  if (open) {
    previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', onKeydown)
    await nextTick()
    closeButton.value?.focus()
  } else {
    document.body.style.overflow = previousOverflow
    window.removeEventListener('keydown', onKeydown)
  }
})

onUnmounted(() => {
  if (import.meta.client) {
    document.body.style.overflow = previousOverflow
    window.removeEventListener('keydown', onKeydown)
  }
})
</script>

<template>
  <Transition name="announcement-modal" appear>
    <div
      v-if="announcementOpen"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-black/35 p-4 sm:p-6"
      role="presentation"
      @click.self="closeAnnouncement"
    >
      <section
        class="announcement-dialog w-full max-w-[640px] overflow-hidden rounded-2xl border border-rocom-outline bg-rocom-surface-strong shadow-float"
        role="dialog"
        aria-modal="true"
        aria-labelledby="announcement-dialog-title"
      >
        <header class="flex items-center justify-between gap-4 border-b border-rocom-outline px-5 py-4 sm:px-6">
          <h2 id="announcement-dialog-title" class="text-lg font-bold text-rocom-text-strong">站点公告</h2>
          <button
            ref="closeButton"
            type="button"
            class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-rocom-text-secondary transition-colors hover:bg-rocom-control hover:text-rocom-text-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rocom-primary"
            aria-label="关闭公告"
            @click="closeAnnouncement"
          >
            <X :size="18" />
          </button>
        </header>
        <div class="max-h-[70vh] overflow-y-auto px-5 py-5 text-base leading-8 text-rocom-text sm:px-6 sm:py-6">
          {{ announcementContent }}
        </div>
      </section>
    </div>
  </Transition>
</template>
