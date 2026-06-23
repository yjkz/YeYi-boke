<script setup lang="ts">
const api = useApi()
useHead({ title: '归档' })

const { data: postsData } = await useAsyncData('archive', () =>
  api.get('/api/v1/posts', { page_size: 100 })
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
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-rocom-text-strong mb-6">归档</h1>
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
  </div>
</template>
