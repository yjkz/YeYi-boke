<script setup lang="ts">
defineProps<{
  category?: { name: string; slug: string } | null
  tags?: { name: string; slug: string }[]
  publishedAt?: string | null
  viewCount?: number
}>()
</script>

<template>
  <div class="flex flex-wrap items-center gap-2 text-xs text-rocom-text-caption">
    <time v-if="publishedAt" :datetime="publishedAt">
      {{ new Date(publishedAt).toLocaleDateString('zh-CN') }}
    </time>
    <span v-if="category" class="px-2 py-0.5 rounded-pill bg-rocom-primary-soft text-rocom-primary-outline font-medium">
      {{ category.name }}
    </span>
    <span v-for="tag in tags" :key="tag.slug" class="px-2 py-0.5 rounded-pill bg-rocom-control text-rocom-text-muted">
      {{ tag.name }}
    </span>
    <span v-if="viewCount" class="text-rocom-text-disabled">
      {{ viewCount }} 阅读
    </span>
  </div>
</template>
