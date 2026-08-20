<script setup lang="ts">
import { Menu, X } from 'lucide-vue-next'

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
    <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-[100] focus:px-4 focus:py-2 focus:bg-rocom-primary focus:text-rocom-text-strong focus:rounded-lg">
      跳到主要内容
    </a>

    <div class="max-w-[1440px] mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
      <NuxtLink to="/" class="min-w-0 flex items-center gap-2 truncate text-xl font-bold text-rocom-text-strong tracking-wider">
        <img v-if="siteConfig?.logo_url" :src="siteConfig.logo_url" :alt="siteConfig.site_title" class="h-8 max-w-32 object-contain" />
        <span>{{ siteConfig?.site_title || 'YeYi 的博客' }}</span>
      </NuxtLink>

      <nav class="hidden md:flex shrink-0 items-center gap-0.5" aria-label="主导航">
        <NuxtLink
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          class="px-2.5 py-2 text-sm font-medium text-rocom-text-secondary hover:text-rocom-primary transition-colors rounded-lg hover:bg-rocom-control"
          :class="{ 'text-rocom-primary bg-rocom-primary-soft': route.path === link.path }"
        >
          {{ link.label }}
        </NuxtLink>
        <SearchBox />
        <DarkToggle />
      </nav>

      <button
        class="md:hidden w-11 h-11 flex items-center justify-center text-rocom-text rounded-lg hover:bg-rocom-control transition-colors"
        @click="mobileMenuOpen = !mobileMenuOpen"
        :aria-label="mobileMenuOpen ? '关闭菜单' : '打开菜单'"
        :aria-expanded="mobileMenuOpen"
      >
        <Menu v-if="!mobileMenuOpen" :size="22" />
        <X v-else :size="22" />
      </button>
    </div>

    <Transition name="slide-down">
      <div v-if="mobileMenuOpen" class="md:hidden border-t border-rocom-outline bg-rocom-surface-paper">
        <nav class="mx-auto flex max-w-[1440px] flex-col gap-1 px-4 py-3 sm:px-6" aria-label="移动端导航">
          <NuxtLink
            v-for="link in navLinks"
            :key="link.path"
            :to="link.path"
            class="px-3 py-3 text-sm font-medium text-rocom-text-secondary hover:text-rocom-primary hover:bg-rocom-control rounded-lg transition-colors"
            :class="{ 'text-rocom-primary bg-rocom-primary-soft': route.path === link.path }"
            @click="mobileMenuOpen = false"
          >
            {{ link.label }}
          </NuxtLink>
          <div class="flex items-center gap-2 pt-2 mt-2 border-t border-rocom-outline">
            <SearchBox />
            <DarkToggle />
          </div>
        </nav>
      </div>
    </Transition>
  </header>
</template>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.2s ease-out;
}
.slide-down-enter-from, .slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
