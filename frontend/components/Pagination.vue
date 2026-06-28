<script setup lang="ts">
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps<{
  page: number
  totalPages: number
}>()
const emit = defineEmits<{ (e: 'change', page: number): void }>()

const pages = computed(() => {
  const p: number[] = []
  const start = Math.max(1, props.page - 2)
  const end = Math.min(props.totalPages, props.page + 2)
  for (let i = start; i <= end; i++) p.push(i)
  return p
})
</script>

<template>
  <nav v-if="totalPages > 1" class="flex items-center justify-center gap-1 mt-8" aria-label="分页导航">
    <button
      :disabled="page <= 1"
      class="h-11 px-3 text-sm rounded-lg bg-rocom-control hover:bg-rocom-control-hover disabled:opacity-40 text-rocom-text inline-flex items-center gap-1 transition-colors"
      aria-label="上一页"
      @click="emit('change', page - 1)"
    >
      <ChevronLeft :size="16" />
    </button>
    <button
      v-for="p in pages"
      :key="p"
      class="w-11 h-11 text-sm rounded-lg transition-colors"
      :class="p === page ? 'bg-rocom-primary text-rocom-text-strong font-bold' : 'bg-rocom-control hover:bg-rocom-control-hover text-rocom-text'"
      :aria-current="p === page ? 'page' : undefined"
      :aria-label="`第 ${p} 页`"
      @click="emit('change', p)"
    >
      {{ p }}
    </button>
    <button
      :disabled="page >= totalPages"
      class="h-11 px-3 text-sm rounded-lg bg-rocom-control hover:bg-rocom-control-hover disabled:opacity-40 text-rocom-text inline-flex items-center gap-1 transition-colors"
      aria-label="下一页"
      @click="emit('change', page + 1)"
    >
      <ChevronRight :size="16" />
    </button>
  </nav>
</template>
