<script setup lang="ts">
const api = useApi()
useHead({ title: '分类' })
const { data: categories, status, error } = await useAsyncData('categories', () => api.get('/categories'))
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-rocom-text-strong mb-6">分类</h1>
    <p v-if="status === 'pending'" class="py-12 text-center text-rocom-text-muted">加载中...</p>
    <p v-else-if="error" class="py-12 text-center text-rocom-danger">分类加载失败，请稍后重试。</p>
    <CategoryList v-else-if="categories?.length" :categories="categories" />
    <p v-else class="text-rocom-text-muted">暂无分类</p>
  </div>
</template>
