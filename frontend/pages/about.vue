<script setup lang="ts">
import MarkdownIt from 'markdown-it'

const api = useApi()
const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

useHead({ title: '关于' })

const { data: config } = await useAsyncData(
  'about-config',
  () => api.get('/site/config')
)

const aboutHtml = computed(() => {
  const content = config.value?.about_content
  return content ? md.render(content) : ''
})
</script>

<template>
  <div class="prose max-w-none">
    <h1>关于</h1>
    <div v-if="aboutHtml" v-html="aboutHtml" />
    <p v-else class="text-rocom-text-muted">暂无内容</p>
  </div>
</template>
