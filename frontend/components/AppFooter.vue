<script setup lang="ts">
const { siteConfig } = useSiteConfig()
</script>

<template>
  <footer class="border-t border-rocom-outline bg-rocom-bg-warm py-8 text-center">
    <p class="text-sm text-rocom-text-caption">
      {{ siteConfig?.footer_text || '© 2026 YeYi' }}
    </p>
  </footer>
</template>
