<script setup lang="ts">
const { siteConfig } = useSiteConfig()
const runtimeConfig = useRuntimeConfig()
const adminLoginUrl = computed(() => `${String(runtimeConfig.public.adminUrl || 'http://localhost:3001').replace(/\/$/, '')}/login`)
</script>

<template>
  <footer class="border-t border-rocom-outline bg-rocom-bg-warm">
    <div class="mx-auto flex max-w-[1440px] items-center justify-between gap-4 px-4 py-5 sm:px-6">
      <p class="text-sm text-rocom-text-caption">
        {{ siteConfig?.footer_text || '© 2026 YeYi' }}
      </p>
      <a
        :href="adminLoginUrl"
        class="shrink-0 text-[11px] text-rocom-text-disabled transition-colors hover:text-rocom-text-muted focus-visible:text-rocom-text-muted focus-visible:outline-none"
        aria-label="管理员登录"
      >
        管理入口
      </a>
    </div>
  </footer>
</template>
