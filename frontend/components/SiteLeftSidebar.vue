<script setup lang="ts">
import { ExternalLink, Folder, Link, Mail, Tag, UserRound } from 'lucide-vue-next'

interface Category { id: number; name: string; slug: string }
interface SiteTag { id: number; name: string; slug: string }

const api = useApi()
const { siteConfig } = useSiteConfig()
const { openAnnouncement } = useAnnouncementModal()

const { data: categories } = await useAsyncData<Category[]>('sidebar-categories', () => api.get('/categories'))
const { data: tags } = await useAsyncData<SiteTag[]>('sidebar-tags', () => api.get('/tags'))
const { data: announcement } = await useAsyncData<{ content: string }>('sidebar-announcement', () => api.get('/site/announcement'))

const socialLinks = computed(() => Object.entries(siteConfig.value?.social_links || {}).filter(([, url]) => Boolean(url)))
const displayName = computed(() => siteConfig.value?.site_title || 'YeYi')
const avatarFallback = computed(() => displayName.value.trim().slice(0, 1).toUpperCase() || 'Y')
const socialLabel = (key: string) => ({
  email: 'Email',
  github: 'GitHub',
  bilibili: 'Bilibili',
  x: 'X',
  twitter: 'Twitter',
  website: '网站',
  rss: 'RSS',
}[key.toLowerCase()] || key)
const isMailLink = (url: string) => url.startsWith('mailto:')
</script>

<template>
  <aside class="hidden xl:block xl:sticky xl:top-24 space-y-4" aria-label="站点信息">
    <section class="sidebar-widget">
      <div class="sidebar-widget-title"><UserRound :size="15" />关于本站</div>
      <div class="flex items-center gap-3">
        <img v-if="siteConfig?.avatar_url" :src="siteConfig.avatar_url" :alt="displayName" class="h-14 w-14 shrink-0 rounded-full border border-rocom-outline object-cover" />
        <div v-else class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-rocom-outline bg-rocom-primary-soft text-xl font-bold text-rocom-text-strong">{{ avatarFallback }}</div>
        <div class="min-w-0">
          <h2 class="truncate text-base font-bold text-rocom-text-strong">{{ displayName }}</h2>
          <p class="mt-1 text-xs leading-5 text-rocom-text-secondary">{{ siteConfig?.site_subtitle || '记录生活与代码' }}</p>
        </div>
      </div>
      <div v-if="socialLinks.length" class="mt-4 flex flex-wrap gap-1.5 border-t border-rocom-outline pt-3">
        <a v-for="[key, url] in socialLinks" :key="key" :href="url" :target="isMailLink(url) ? undefined : '_blank'" :rel="isMailLink(url) ? undefined : 'noreferrer'" class="inline-flex items-center gap-1 rounded-md bg-rocom-control px-2 py-1 text-xs text-rocom-text-secondary transition-colors hover:bg-rocom-primary-soft hover:text-rocom-primary-outline">
          <Mail v-if="isMailLink(url)" :size="12" />
          <Link v-else :size="12" />
          {{ socialLabel(key) }}
          <ExternalLink v-if="!isMailLink(url)" :size="11" />
        </a>
      </div>
    </section>

    <section v-if="announcement?.content" class="sidebar-widget">
      <div class="sidebar-widget-title"><span class="sidebar-widget-mark" />公告</div>
      <button
        type="button"
        class="group w-full text-left text-sm leading-6 text-rocom-text-secondary transition-colors hover:text-rocom-text-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rocom-primary"
        aria-label="查看完整站点公告"
        @click="openAnnouncement(announcement.content, $event.currentTarget)"
      >
        <span class="line-clamp-4">{{ announcement.content }}</span>
        <span class="mt-2 inline-block text-xs text-rocom-primary-outline opacity-90 group-hover:underline">查看全文</span>
      </button>
    </section>

    <section v-if="categories?.length" class="sidebar-widget">
      <div class="sidebar-widget-title"><Folder :size="15" />分类</div>
      <nav class="space-y-1" aria-label="分类筛选">
        <NuxtLink v-for="category in categories" :key="category.id" :to="{ path: '/', query: { category: category.slug } }" class="flex items-center justify-between rounded-md px-2 py-1.5 text-sm text-rocom-text-secondary transition-colors hover:bg-rocom-control hover:text-rocom-primary-outline">
          <span class="truncate">{{ category.name }}</span>
          <span class="text-[11px] text-rocom-text-caption">›</span>
        </NuxtLink>
      </nav>
    </section>

    <section v-if="tags?.length" class="sidebar-widget">
      <div class="sidebar-widget-title"><Tag :size="15" />标签</div>
      <div class="flex max-h-32 flex-wrap gap-1.5 overflow-y-auto pr-1">
        <NuxtLink v-for="tag in tags" :key="tag.id" :to="{ path: '/', query: { tag: tag.slug } }" class="rounded-md bg-rocom-control px-2 py-1 text-xs text-rocom-text-secondary transition-colors hover:bg-rocom-primary-soft hover:text-rocom-primary-outline">
          {{ tag.name }}
        </NuxtLink>
      </div>
    </section>
  </aside>
</template>
