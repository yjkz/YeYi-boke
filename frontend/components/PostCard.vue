<script setup lang="ts">
defineProps<{
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
</script>

<template>
  <article class="group bg-rocom-surface-paper rounded-2xl border border-rocom-outline shadow-paper hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 overflow-hidden">
    <NuxtLink :to="`/posts/${post.slug}`" class="block">
      <img v-if="post.cover_image" :src="post.cover_image" :alt="post.title" class="w-full h-48 object-cover" />
      <div class="p-5">
        <h2 class="text-lg font-bold text-rocom-text-strong group-hover:text-rocom-primary transition-colors mb-2 line-clamp-2">
          {{ post.title }}
        </h2>
        <p v-if="post.excerpt" class="text-sm text-rocom-text-secondary line-clamp-3 mb-3">
          {{ post.excerpt }}
        </p>
        <PostMeta
          :category="post.category"
          :tags="post.tags"
          :published-at="post.published_at"
          :view-count="post.view_count"
        />
      </div>
    </NuxtLink>
  </article>
</template>
