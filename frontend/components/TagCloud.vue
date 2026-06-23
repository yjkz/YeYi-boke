<script setup lang="ts">
defineProps<{ tags: { id: number; name: string; slug: string }[] }>()
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <NuxtLink
      v-for="tag in tags"
      :key="tag.id"
      :to="{ path: '/', query: { tag: tag.slug } }"
      class="px-3 py-1.5 rounded-pill bg-rocom-control text-sm text-rocom-text-secondary hover:bg-rocom-primary-soft hover:text-rocom-primary-outline transition-colors"
    >
      {{ tag.name }}
    </NuxtLink>
  </div>
</template>
