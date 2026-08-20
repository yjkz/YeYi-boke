<script setup lang="ts">
defineProps<{
  comment: {
    id: number
    nickname: string
    website?: string | null
    content: string
    created_at: string
    replies?: any[]
  }
  depth?: number
}>()
const emit = defineEmits<{ (e: 'reply', value: { id: number; nickname: string }): void }>()

const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN')
</script>

<template>
  <div class="py-4" :class="{ 'ml-8 border-l-2 border-rocom-outline pl-4': depth }">
    <div class="flex items-center gap-2 mb-2">
      <span class="font-semibold text-sm text-rocom-text-strong">{{ comment.nickname }}</span>
      <span class="text-xs text-rocom-text-caption">{{ formatDate(comment.created_at) }}</span>
    </div>
    <p class="text-sm text-rocom-text-secondary whitespace-pre-wrap">{{ comment.content }}</p>
    <button type="button" class="mt-2 text-xs text-rocom-primary-outline hover:underline" @click="emit('reply', { id: comment.id, nickname: comment.nickname })">回复</button>
    <CommentItem
      v-for="reply in comment.replies"
      :key="reply.id"
      :comment="reply"
      :depth="(depth || 0) + 1"
      @reply="emit('reply', $event)"
    />
  </div>
</template>
