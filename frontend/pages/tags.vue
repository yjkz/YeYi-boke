<script setup lang="ts">
const api = useApi()
useHead({ title: '标签' })
const { data: tags } = await useAsyncData('tags', () => api.get('/tags'))
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-rocom-text-strong mb-6">标签</h1>
    <TagCloud v-if="tags?.length" :tags="tags" />
    <p v-else class="text-rocom-text-muted">暂无标签</p>
  </div>
</template>
