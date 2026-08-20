<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import { sanitizeContentHtml } from '~/composables/useContentEnhancements'

const api = useApi()
const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

useHead({ title: '关于' })

const { data: config, status, error } = await useAsyncData(
  'about-config',
  () => api.get('/site/config')
)

const aboutHtml = computed(() => {
  const content = config.value?.about_content
  return content ? sanitizeContentHtml(md.render(content)) : ''
})
</script>

<template>
  <div class="prose max-w-none">
    <h1>关于</h1>
    <p v-if="status === 'pending'" class="text-rocom-text-muted">加载中...</p>
    <p v-else-if="error" class="text-rocom-danger">内容加载失败，请稍后重试。</p>
    <div v-if="aboutHtml" v-html="aboutHtml" />
    <p v-else-if="status !== 'pending' && !error" class="text-rocom-text-muted">暂无内容</p>
  </div>
</template>
