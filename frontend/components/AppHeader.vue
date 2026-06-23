<script setup lang="ts">
const { siteConfig } = useSiteConfig()
const route = useRoute()
const mobileMenuOpen = ref(false)

const navLinks = [
  { path: '/', label: '首页' },
  { path: '/categories', label: '分类' },
  { path: '/tags', label: '标签' },
  { path: '/archive', label: '归档' },
  { path: '/about', label: '关于' },
]
</script>

<template>
  <header class="sticky top-0 z-50 bg-rocom-nav-surface backdrop-blur-sm border-b border-rocom-outline">
    <div class="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
      <NuxtLink to="/" class="text-xl font-bold text-rocom-text-strong tracking-wider">
        {{ siteConfig?.site_title || 'YeYi 的博客' }}
      </NuxtLink>

      <nav class="hidden md:flex items-center gap-6">
        <NuxtLink
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          class="text-sm font-medium text-rocom-text-secondary hover:text-rocom-primary transition-colors"
          :class="{ 'text-rocom-primary': route.path === link.path }"
        >
          {{ link.label }}
        </NuxtLink>
        <SearchBox />
        <DarkToggle />
      </nav>

      <button class="md:hidden text-rocom-text" @click="mobileMenuOpen = !mobileMenuOpen">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div v-if="mobileMenuOpen" class="md:hidden border-t border-rocom-outline bg-rocom-surface-paper">
      <nav class="flex flex-col p-4 gap-3">
        <NuxtLink
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          class="text-sm font-medium text-rocom-text-secondary hover:text-rocom-primary py-2"
          @click="mobileMenuOpen = false"
        >
          {{ link.label }}
        </NuxtLink>
        <div class="flex items-center gap-3 pt-2 border-t border-rocom-outline">
          <SearchBox />
          <DarkToggle />
        </div>
      </nav>
    </div>
  </header>
</template>
