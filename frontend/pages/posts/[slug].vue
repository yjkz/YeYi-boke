<script setup lang="ts">
const api = useApi()
const route = useRoute()
const slug = route.params.slug as string

const { data: post } = await useAsyncData(
  `post-${slug}`,
  () => api.get(`/posts/${slug}`)
)

if (!post.value) {
  throw createError({ statusCode: 404, message: '文章不存在' })
}

useHead({ title: post.value.title })

const stripTags = (value: string) => value.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim()
const slugifyHeading = (value: string, index: number) => {
  const base = stripTags(value).toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '') || `section-${index + 1}`
  return `section-${base}`
}

const renderedContentHtml = computed(() => {
  if (!post.value?.content_html) return ''
  const usedIds = new Map<string, number>()
  let headingIndex = 0
  return post.value.content_html.replace(/<h([2-3])([^>]*)>(.*?)<\/h\1>/gis, (full, level, attrs, inner) => {
    const baseId = slugifyHeading(inner, headingIndex)
    const count = usedIds.get(baseId) || 0
    usedIds.set(baseId, count + 1)
    const id = count ? `${baseId}-${count + 1}` : baseId
    headingIndex += 1
    const withoutId = String(attrs).replace(/\s+id="[^"]*"/i, '')
    return `<h${level}${withoutId} id="${id}">${inner}</h${level}>`
  })
})

const tocItems = computed(() => {
  const regex = /<h([2-3])[^>]*id="([^"]+)"[^>]*>(.*?)<\/h\1>/gis
  const items: { id: string; text: string; level: number }[] = []
  let match
  while ((match = regex.exec(renderedContentHtml.value)) !== null) {
    items.push({ level: Number(match[1]), id: match[2], text: stripTags(match[3]) })
  }
  return items
})

const activeToc = useState<{ id: string; text: string; level: number }[]>('active-post-toc', () => [])
watch(tocItems, (items) => { activeToc.value = items }, { immediate: true })
</script>

<template>
  <article v-if="post" class="mx-auto max-w-3xl">
    <div class="min-w-0">
      <header class="mb-8">
        <h1 class="text-3xl font-bold text-rocom-text-strong mb-4">{{ post.title }}</h1>
        <PostMeta
          :category="post.category"
          :tags="post.tags"
          :published-at="post.published_at"
          :view-count="post.view_count"
        />
      </header>

      <div class="prose" v-html="renderedContentHtml" />

      <CommentSection :post-slug="slug" />
    </div>
  </article>
</template>
