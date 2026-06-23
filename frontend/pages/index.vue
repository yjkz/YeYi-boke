<script setup lang="ts">
const api = useApi()
const route = useRoute()
const router = useRouter()

const page = computed(() => Number(route.query.page) || 1)

const { data: postsData } = await useAsyncData(
  `posts-${page.value}`,
  () => api.get('/api/v1/posts', { page: page.value, page_size: 10 })
)

const { data: announcement } = await useAsyncData(
  'announcement',
  () => api.get('/api/v1/site/announcement')
)

const totalPages = computed(() =>
  postsData.value ? Math.ceil(postsData.value.total / postsData.value.page_size) : 1
)

const goToPage = (p: number) => {
  router.push({ query: { ...route.query, page: p > 1 ? p : undefined } })
}
</script>

<template>
  <div>
    <AnnouncementBar v-if="announcement?.content" :content="announcement.content" />

    <div class="grid gap-6 sm:grid-cols-2">
      <PostCard v-for="post in postsData?.items" :key="post.id" :post="post" />
    </div>

    <div v-if="postsData?.items?.length === 0" class="text-center py-16 text-rocom-text-muted">
      暂无文章
    </div>

    <Pagination :page="page" :total-pages="totalPages" @change="goToPage" />
  </div>
</template>
