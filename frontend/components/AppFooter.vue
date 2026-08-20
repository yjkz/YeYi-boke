<script setup lang="ts">
const { siteConfig } = useSiteConfig()
const runtimeConfig = useRuntimeConfig()
const adminLoginUrl = computed(() => `${String(runtimeConfig.public.adminUrl || 'http://localhost:3001').replace(/\/$/, '')}/login`)
</script>

<template>
  <footer class="border-t border-rocom-outline bg-rocom-bg-warm">
    <div class="mx-auto flex max-w-[1440px] items-center justify-between gap-4 px-4 py-5 sm:px-6">
      <div class="flex min-w-0 flex-wrap items-center gap-x-4 gap-y-2">
        <p class="text-sm text-rocom-text-caption">
          {{ siteConfig?.footer_text || '© 2026 YeYi' }}
        </p>
        <a
          href="https://beian.mps.gov.cn/#/query/webSearch?code=42110002000435"
          rel="noreferrer"
          target="_blank"
          class="inline-flex items-center gap-1.5 text-xs text-rocom-text-caption transition-colors hover:text-rocom-primary-outline focus-visible:text-rocom-primary-outline focus-visible:outline-none"
        >
          <img src="/备案图标.png" alt="" width="16" height="16" class="h-4 w-4 object-contain" />
          <span>鄂公网安备42110002000435号</span>
        </a>
      </div>
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
