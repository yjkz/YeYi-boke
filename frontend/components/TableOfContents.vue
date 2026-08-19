<script setup lang="ts">
interface TocItem { id: string; text: string; level: number }
defineProps<{ items: TocItem[] }>()
</script>

<template>
  <nav v-if="items.length" aria-label="文章目录">
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
