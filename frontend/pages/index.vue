<script setup lang="ts">
const api = useApi()
const route = useRoute()
const router = useRouter()
const nuxtApp = useNuxtApp()

const page = computed(() => Number(route.query.page) || 1)
const category = computed(() => (route.query.category as string) || '')
const tag = computed(() => (route.query.tag as string) || '')
const hasFilter = computed(() => Boolean(category.value || tag.value))

const { data: postsData, status, error } = await useAsyncData(
  `posts-${page.value}`,
  () => api.get('/posts', { page: page.value, page_size: 10, category: category.value || undefined, tag: tag.value || undefined }),
  { watch: [page, category, tag], getCachedData: () => undefined }
)

const { data: announcement } = await useAsyncData(
  'announcement',
  () => api.get('/site/announcement'),
  { getCachedData: () => undefined }
)

const totalPages = computed(() =>
  postsData.value ? Math.ceil(postsData.value.total / postsData.value.page_size) : 1
)

const goToPage = (p: number) => {
  router.push({ query: { ...route.query, page: p > 1 ? p : undefined } })
}

const clearFilter = () => router.push({ path: '/', query: {} })
</script>

<template>
  <div>
    <AnnouncementBar v-if="announcement?.content" :content="announcement.content" />

    <div v-if="hasFilter" class="mb-5 flex flex-wrap items-center gap-2 text-sm text-rocom-text-secondary">
      <span>当前筛选：</span>
      <span v-if="category" class="rounded-md bg-rocom-primary-soft px-2 py-1">分类：{{ category }}</span>
      <span v-if="tag" class="rounded-md bg-rocom-primary-soft px-2 py-1">标签：{{ tag }}</span>
      <button type="button" class="text-rocom-primary-outline hover:underline" @click="clearFilter">清除筛选</button>
    </div>

    <p v-if="status === 'pending'" class="py-16 text-center text-rocom-text-muted">加载中...</p>
    <p v-else-if="error" class="py-16 text-center text-rocom-danger">文章加载失败，请稍后重试。</p>
    <div v-else class="post-grid" :class="{ 'post-grid--single': postsData?.items?.length === 1 }">
      <PostCard v-for="post in postsData?.items" :key="post.id" :post="post" />
    </div>

    <div v-if="status !== 'pending' && !error && postsData?.items?.length === 0" class="text-center py-16 text-rocom-text-muted">
      暂无文章
    </div>

    <Pagination :page="page" :total-pages="totalPages" @change="goToPage" />
  </div>
</template>
