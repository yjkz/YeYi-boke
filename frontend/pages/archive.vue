<script setup lang="ts">
const api = useApi()
const route = useRoute()
const router = useRouter()
useHead({ title: '归档' })

const page = computed(() => Number(route.query.page) || 1)
const { data: postsData, status, error } = await useAsyncData(
  () => `archive-${page.value}`,
  () => api.get('/posts', { page: page.value, page_size: 50 }),
  { watch: [page], getCachedData: () => undefined }
)

const grouped = computed(() => {
  if (!postsData.value?.items) return {}
  const groups: Record<string, any[]> = {}
  for (const post of postsData.value.items) {
    const year = new Date(post.published_at || post.created_at).getFullYear().toString()
    if (!groups[year]) groups[year] = []
    groups[year].push(post)
  }
  return groups
})

const totalPages = computed(() => postsData.value ? Math.ceil(postsData.value.total / postsData.value.page_size) : 1)
const goToPage = (value: number) => router.push({ query: { page: value > 1 ? value : undefined } })
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-rocom-text-strong mb-6">归档</h1>
    <p v-if="status === 'pending'" class="py-12 text-center text-rocom-text-muted">加载中...</p>
    <p v-else-if="error" class="py-12 text-center text-rocom-danger">归档加载失败，请稍后重试。</p>
    <div v-for="(posts, year) in grouped" :key="year" class="mb-8">
      <h2 class="text-lg font-bold text-rocom-primary mb-4">{{ year }}</h2>
      <ul class="space-y-2">
        <li v-for="post in posts" :key="post.id" class="flex items-baseline gap-3">
          <span class="text-xs text-rocom-text-caption shrink-0 w-16">
            {{ new Date(post.published_at || post.created_at).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }) }}
          </span>
          <NuxtLink :to="`/posts/${post.slug}`" class="text-rocom-text hover:text-rocom-primary transition-colors">
            {{ post.title }}
          </NuxtLink>
        </li>
      </ul>
    </div>
    <p v-if="status !== 'pending' && !error && !Object.keys(grouped).length" class="py-12 text-center text-rocom-text-muted">暂无文章</p>
    <Pagination :page="page" :total-pages="totalPages" @change="goToPage" />
  </div>
</template>
