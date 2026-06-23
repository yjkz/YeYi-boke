<script setup lang="ts">
defineProps<{ categories: { id: number; name: string; slug: string; description?: string | null }[] }>()
</script>

<template>
  <div class="grid gap-4 sm:grid-cols-2">
    <NuxtLink
      v-for="cat in categories"
      :key="cat.id"
      :to="{ path: '/', query: { category: cat.slug } }"
      class="bg-rocom-surface-paper rounded-xl border border-rocom-outline p-4 hover:shadow-paper hover:-translate-y-0.5 transition-all"
    >
      <h3 class="font-bold text-rocom-text-strong">{{ cat.name }}</h3>
      <p v-if="cat.description" class="text-sm text-rocom-text-secondary mt-1">{{ cat.description }}</p>
    </NuxtLink>
  </div>
</template>
