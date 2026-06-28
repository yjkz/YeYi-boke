<script setup lang="ts">
const props = defineProps<{
  post: {
    title: string
    slug: string
    excerpt?: string | null
    cover_image?: string | null
    category?: { name: string; slug: string } | null
    tags?: { name: string; slug: string }[]
    published_at?: string | null
    view_count?: number
  }
}>()

const hasCover = computed(() => {
  const img = props.post.cover_image
  return img && (img.startsWith('/') || img.startsWith('http'))
})
</script>

<template>
  <article class="group bg-rocom-surface-paper rounded-2xl border border-rocom-outline shadow-paper hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 overflow-hidden flex flex-col">
    <NuxtLink :to="`/posts/${post.slug}`" class="flex flex-col flex-1 focus:outline-none focus:ring-2 focus:ring-rocom-primary focus:ring-inset rounded-2xl">
      <!-- 有封面图：图片 + 简介 -->
      <template v-if="hasCover">
        <img
          :src="post.cover_image!"
          :alt="post.title"
          class="w-full h-48 object-cover"
          loading="lazy"
          width="400"
          height="192"
        />
        <div class="p-5 flex flex-col flex-1">
          <h2 class="text-lg font-bold text-rocom-text-strong group-hover:text-rocom-primary transition-colors mb-2 line-clamp-2">
            {{ post.title }}
          </h2>
          <p v-if="post.excerpt" class="text-sm text-rocom-text-secondary line-clamp-2 mb-3">
            {{ post.excerpt }}
          </p>
          <div class="mt-auto pt-3 border-t border-rocom-outline">
            <PostMeta
              :category="post.category"
              :tags="post.tags"
              :published-at="post.published_at"
              :view-count="post.view_count"
            />
          </div>
        </div>
      </template>

      <!-- 无封面图：装饰头部 + 更多文字 -->
      <template v-else>
        <div class="h-2 bg-gradient-to-r from-rocom-primary via-rocom-accent-orange to-rocom-primary" />
        <div class="p-6 flex flex-col flex-1">
          <h2 class="text-xl font-bold text-rocom-text-strong group-hover:text-rocom-primary transition-colors mb-3 leading-tight">
            {{ post.title }}
          </h2>
          <p v-if="post.excerpt" class="text-sm text-rocom-text-secondary line-clamp-4 mb-4 flex-1">
            {{ post.excerpt }}
          </p>
          <div class="pt-3 border-t border-rocom-outline">
            <PostMeta
              :category="post.category"
              :tags="post.tags"
              :published-at="post.published_at"
              :view-count="post.view_count"
            />
          </div>
        </div>
      </template>
    </NuxtLink>
  </article>
</template>
