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
      href: computed(() => siteConfig.value?.favicon_url || '/favicon.ico'),
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
    <main id="main-content" class="flex-1 w-full max-w-[1440px] mx-auto px-4 py-6 sm:px-6 sm:py-8">
      <div class="xl:grid xl:grid-cols-[224px_minmax(0,1fr)_224px] xl:items-start xl:gap-6">
        <SiteLeftSidebar />
        <div class="min-w-0"><slot /></div>
        <SiteRightSidebar />
      </div>
    </main>
    <AnnouncementModal />
    <AppFooter />
  </div>
</template>
