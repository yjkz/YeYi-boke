<script setup lang="ts">
interface TocItem { id: string; text: string; level: number }
defineProps<{ items: TocItem[] }>()
</script>

<template>
  <nav v-if="items.length" class="hidden lg:block sticky top-24 w-56 shrink-0">
    <h4 class="text-xs font-bold text-rocom-text-caption uppercase tracking-widest mb-3">目录</h4>
    <ul class="space-y-1.5 text-sm">
      <li v-for="item in items" :key="item.id">
        <a
          :href="`#${item.id}`"
          class="block text-rocom-text-muted hover:text-rocom-primary transition-colors"
          :style="{ paddingLeft: `${(item.level - 2) * 0.75}rem` }"
        >
          {{ item.text }}
        </a>
      </li>
    </ul>
  </nav>
</template>
