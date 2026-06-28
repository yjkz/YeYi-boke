<script setup lang="ts">
const { fetchConfig } = useSiteConfig()
const { recordVisit } = useVisit()
const route = useRoute()

await fetchConfig()

watch(() => route.fullPath, () => {
  nextTick(() => recordVisit())
}, { immediate: true })
</script>

<template>
  <div class="min-h-screen flex flex-col bg-rocom-bg">
    <AppHeader />
    <main class="flex-1 w-full max-w-4xl mx-auto px-4 py-8">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>
