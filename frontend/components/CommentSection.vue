<script setup lang="ts">
const props = defineProps<{ postSlug: string }>()
const api = useApi()
const { siteConfig, fetchConfig } = useSiteConfig()
await fetchConfig()
const replyingTo = ref<{ id: number; nickname: string } | null>(null)

const { data: comments, refresh } = await useAsyncData(
  `comments-${props.postSlug}`,
  () => api.get(`/posts/${props.postSlug}/comments`)
)
</script>

<template>
  <section class="mt-12 border-t border-rocom-outline pt-8" aria-label="评论区">
    <h2 class="text-lg font-bold text-rocom-text-strong mb-6">评论 ({{ comments?.length || 0 }})</h2>

    <div v-if="comments?.length" class="divide-y divide-rocom-outline">
      <CommentItem v-for="c in comments" :key="c.id" :comment="c" @reply="replyingTo = $event" />
    </div>
    <p v-else class="text-sm text-rocom-text-muted py-4">暂无评论，来抢沙发吧！</p>

    <div v-if="siteConfig?.comment_enabled !== false" class="mt-8">
      <CommentForm :post-slug="postSlug" :parent-id="replyingTo?.id" :replying-to="replyingTo?.nickname" :need-review="siteConfig?.comment_need_review !== false" @cancel-reply="replyingTo = null" @submitted="replyingTo = null; refresh()" />
    </div>
    <p v-else class="mt-8 rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 text-sm text-rocom-text-muted">评论功能已关闭。</p>
  </section>
</template>
