<script setup lang="ts">
import { Calendar, Eye } from 'lucide-vue-next'

defineProps<{
  category?: { name: string; slug: string } | null
  tags?: { name: string; slug: string }[]
  publishedAt?: string | null
  viewCount?: number
}>()
</script>

<template>
  <div class="flex flex-wrap items-center gap-2 text-xs text-rocom-text-caption">
    <time v-if="publishedAt" :datetime="publishedAt" class="inline-flex items-center gap-1">
      <Calendar :size="12" />
      {{ new Date(publishedAt).toLocaleDateString('zh-CN') }}
    </time>
    <NuxtLink
      v-if="category"
      :to="{ path: '/', query: { category: category.slug } }"
      class="px-2 py-0.5 rounded-pill bg-rocom-primary-soft text-rocom-primary-outline font-medium hover:bg-rocom-primary transition-colors"
    >
      {{ category.name }}
    </NuxtLink>
    <NuxtLink
      v-for="tag in tags"
      :key="tag.slug"
      :to="{ path: '/', query: { tag: tag.slug } }"
      class="px-2 py-0.5 rounded-pill bg-rocom-control text-rocom-text-muted hover:bg-rocom-primary-soft hover:text-rocom-primary-outline transition-colors"
    >
      {{ tag.name }}
    </NuxtLink>
    <span v-if="viewCount" class="inline-flex items-center gap-1 text-rocom-text-disabled">
      <Eye :size="12" />
      {{ viewCount }}
    </span>
  </div>
</template>
