<script setup lang="ts">
const props = defineProps<{ postSlug: string }>()
const api = useApi()

const { data: comments, refresh } = await useAsyncData(
  `comments-${props.postSlug}`,
  () => api.get(`/api/v1/posts/${props.postSlug}/comments`)
)
</script>

<template>
  <section class="mt-12 border-t border-rocom-outline pt-8">
    <h2 class="text-lg font-bold text-rocom-text-strong mb-6">评论</h2>

    <div v-if="comments?.length" class="divide-y divide-rocom-outline">
      <CommentItem v-for="c in comments" :key="c.id" :comment="c" />
    </div>
    <p v-else class="text-sm text-rocom-text-muted py-4">暂无评论，来抢沙发吧！</p>

    <div class="mt-8">
      <CommentForm :post-slug="postSlug" @submitted="refresh()" />
    </div>
  </section>
</template>
