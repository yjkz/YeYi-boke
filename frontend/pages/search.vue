<script setup lang="ts">
const api = useApi()
const route = useRoute()
const router = useRouter()
const query = computed(() => (route.query.q as string) || '')
const page = computed(() => Number(route.query.page) || 1)

useHead({ title: computed(() => query.value ? `搜索: ${query.value}` : '搜索') })

const { data: results } = await useAsyncData(
  `search-${query.value}-${page.value}`,
  () => query.value ? api.get('/search', { q: query.value, page: page.value }) : null,
  { watch: [query, page] }
)

const totalPages = computed(() =>
  results.value ? Math.ceil(results.value.total / results.value.page_size) : 1
)

const goToPage = (p: number) => {
  router.push({ query: { q: query.value, page: p > 1 ? p : undefined } })
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-rocom-text-strong mb-6">
      搜索: <span class="text-rocom-primary">{{ query }}</span>
    </h1>

    <div v-if="results?.items?.length" class="post-grid">
      <PostCard v-for="post in results.items" :key="post.id" :post="post" />
    </div>
    <p v-else-if="query" class="text-rocom-text-muted py-8 text-center">未找到相关文章</p>

    <Pagination :page="page" :total-pages="totalPages" @change="goToPage" />
  </div>
</template>
