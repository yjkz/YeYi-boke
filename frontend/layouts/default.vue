<script setup lang="ts">
const { siteConfig, fetchConfig } = useSiteConfig()
const { recordVisit } = useVisit()
const route = useRoute()

await fetchConfig()

useHead({
  title: siteConfig.value?.site_title || 'YeYi 的博客',
  link: [
    {
      rel: 'icon',
      type: 'image/png',
      href: computed(() => {
        const url = siteConfig.value?.favicon_url || '/favicon.ico'
        return url ? `${url}?v=${Date.now()}` : '/favicon.ico'
      }),
    },
  ],
})

watch(() => route.fullPath, () => {
  nextTick(() => recordVisit())
}, { immediate: true })
</script>

<template>
  <div class="min-h-screen flex flex-col bg-rocom-bg">
    <AppHeader />
    <main id="main-content" class="flex-1 w-full max-w-4xl mx-auto px-4 py-8">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>
