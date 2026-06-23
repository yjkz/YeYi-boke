<script setup lang="ts">
const api = useApi()
const route = useRoute()
const slug = route.params.slug as string

const { data: post } = await useAsyncData(
  `post-${slug}`,
  () => api.get(`/api/v1/posts/${slug}`)
)

if (!post.value) {
  throw createError({ statusCode: 404, message: '文章不存在' })
}

useHead({ title: post.value.title })

const tocItems = computed(() => {
  if (!post.value?.content_html) return []
  const regex = /<h([2-4])\s+id="([^"]*)"[^>]*>(.*?)<\/h[2-4]>/g
  const items: { id: string; text: string; level: number }[] = []
  let match
  while ((match = regex.exec(post.value.content_html)) !== null) {
    items.push({ level: Number(match[1]), id: match[2], text: match[3].replace(/<[^>]+>/g, '') })
  }
  return items
})
</script>

<template>
  <article v-if="post" class="flex gap-8">
    <div class="flex-1 min-w-0">
      <header class="mb-8">
        <h1 class="text-3xl font-bold text-rocom-text-strong mb-4">{{ post.title }}</h1>
        <PostMeta
          :category="post.category"
          :tags="post.tags"
          :published-at="post.published_at"
          :view-count="post.view_count"
        />
      </header>

      <div class="prose" v-html="post.content_html" />

      <CommentSection :post-slug="slug" />
    </div>

    <TableOfContents :items="tocItems" />
  </article>
</template>
