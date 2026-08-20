<script setup lang="ts">
interface TocItem { id: string; text: string; level: number }
defineProps<{ items: TocItem[] }>()
</script>

<template>
  <nav v-if="items.length" class="toc-scroll" aria-label="文章目录">
    <ul class="space-y-1.5 text-sm">
      <li v-for="item in items" :key="item.id">
        <a
          :href="`#${item.id}`"
          class="block rounded-md py-1 text-rocom-text-secondary transition-colors hover:bg-rocom-control hover:text-rocom-primary-outline"
          :style="{ paddingLeft: `${(item.level - 2) * 0.75}rem` }"
        >
          {{ item.text }}
        </a>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.toc-scroll {
  --toc-scrollbar-thumb: rgba(110, 94, 78, 0.28);
  --toc-scrollbar-thumb-hover: rgba(110, 94, 78, 0.58);
  max-height: calc(100vh - 10rem);
  max-height: calc(100dvh - 10rem);
  overflow-y: auto;
  overscroll-behavior: contain;
  scrollbar-color: var(--toc-scrollbar-thumb) transparent;
  scrollbar-width: thin;
}

.dark .toc-scroll {
  --toc-scrollbar-thumb: rgba(220, 203, 179, 0.24);
  --toc-scrollbar-thumb-hover: rgba(220, 203, 179, 0.5);
}

.toc-scroll::-webkit-scrollbar {
  width: 0.25rem;
  height: 0.25rem;
}

.toc-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.toc-scroll::-webkit-scrollbar-button {
  display: none;
  width: 0;
  height: 0;
}

.toc-scroll::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: var(--toc-scrollbar-thumb);
  transition: background-color 160ms ease;
}

.toc-scroll:hover {
  scrollbar-color: var(--toc-scrollbar-thumb-hover) transparent;
}

.toc-scroll:hover::-webkit-scrollbar-thumb {
  background: var(--toc-scrollbar-thumb-hover);
}
</style>
