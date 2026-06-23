<script setup lang="ts">
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
  <nav v-if="totalPages > 1" class="flex items-center justify-center gap-1 mt-8">
    <button
      :disabled="page <= 1"
      class="px-3 py-1.5 text-sm rounded-lg bg-rocom-control hover:bg-rocom-control-hover disabled:opacity-40 text-rocom-text"
      @click="emit('change', page - 1)"
    >
      上一页
    </button>
    <button
      v-for="p in pages"
      :key="p"
      class="w-9 h-9 text-sm rounded-lg transition-colors"
      :class="p === page ? 'bg-rocom-primary text-rocom-text-strong font-bold' : 'bg-rocom-control hover:bg-rocom-control-hover text-rocom-text'"
      @click="emit('change', p)"
    >
      {{ p }}
    </button>
    <button
      :disabled="page >= totalPages"
      class="px-3 py-1.5 text-sm rounded-lg bg-rocom-control hover:bg-rocom-control-hover disabled:opacity-40 text-rocom-text"
      @click="emit('change', page + 1)"
    >
      下一页
    </button>
  </nav>
</template>
