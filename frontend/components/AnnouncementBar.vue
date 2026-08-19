<script setup lang="ts">
import { Megaphone } from 'lucide-vue-next'

const props = defineProps<{ content: string }>()
const { openAnnouncement } = useAnnouncementModal()
</script>

<template>
  <button
    v-if="props.content"
    type="button"
    class="group mb-6 flex w-full items-start gap-2 rounded-xl border border-rocom-outline bg-rocom-primary-soft px-4 py-3 text-left text-sm text-rocom-text-strong transition-all duration-200 hover:border-rocom-primary-outline hover:shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rocom-primary"
    aria-label="查看完整站点公告"
    @click="openAnnouncement(props.content, $event.currentTarget)"
  >
    <Megaphone :size="16" class="text-rocom-primary mt-0.5 shrink-0" />
    <span class="line-clamp-2 flex-1">{{ props.content }}</span>
    <span class="shrink-0 text-xs text-rocom-primary-outline opacity-80 transition-opacity group-hover:opacity-100">查看全文</span>
  </button>
</template>
