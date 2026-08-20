<script setup lang="ts">
const api = useApi()
useHead({ title: '标签' })
const { data: tags, status, error } = await useAsyncData('tags', () => api.get('/tags'))
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-rocom-text-strong mb-6">标签</h1>
    <p v-if="status === 'pending'" class="py-12 text-center text-rocom-text-muted">加载中...</p>
    <p v-else-if="error" class="py-12 text-center text-rocom-danger">标签加载失败，请稍后重试。</p>
    <TagCloud v-else-if="tags?.length" :tags="tags" />
    <p v-else class="text-rocom-text-muted">暂无标签</p>
  </div>
</template>
