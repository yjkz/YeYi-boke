<script setup lang="ts">
const api = useApi()
useHead({ title: '分类' })
const { data: categories } = await useAsyncData('categories', () => api.get('/api/v1/categories'))
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-rocom-text-strong mb-6">分类</h1>
    <CategoryList v-if="categories?.length" :categories="categories" />
    <p v-else class="text-rocom-text-muted">暂无分类</p>
  </div>
</template>
