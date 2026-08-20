<script setup lang="ts">
import { BarChart3, CalendarDays, FileText, List, MessageCircle } from 'lucide-vue-next'

interface TocItem { id: string; text: string; level: number }
interface PostItem { id: number; title: string; slug: string; published_at?: string | null }
interface PublicStats { today_pv: number; published_posts: number; categories: number; tags: number; approved_comments: number }

const api = useApi()
const route = useRoute()
const activeToc = useState<TocItem[]>('active-post-toc', () => [])
const isPostPage = computed(() => typeof route.params.slug === 'string' && route.path.startsWith('/posts/'))
const tocItems = computed(() => activeToc.value.filter((item) => item.level === 2 || item.level === 3))

const { openRecentPosts } = useRecentPostsModal()

const { data: recentPosts } = await useAsyncData<PostItem[]>('sidebar-recent-posts', async () => {
  const result = await api.get<{ items: PostItem[] }>('/posts', { page: 1, page_size: 5, sort: 'latest' })
  return result.items
})
const { data: stats } = await useAsyncData<PublicStats>('sidebar-public-stats', () => api.get('/stats/summary'))

const formatDate = (value?: string | null) => value ? new Date(value).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }) : ''
</script>

<template>
  <aside class="hidden xl:block xl:sticky xl:top-24 space-y-4" aria-label="站点辅助信息">
    <section v-if="isPostPage && tocItems.length" class="sidebar-widget">
      <div class="sidebar-widget-title"><List :size="15" />文章目录</div>
      <TableOfContents :items="tocItems" />
    </section>

    <template v-else>
      <section v-if="recentPosts?.length" class="sidebar-widget">
        <div class="mb-3 flex items-center justify-between gap-3">
          <div class="sidebar-widget-title mb-0"><FileText :size="15" />最新文章</div>
          <button
            type="button"
            class="shrink-0 text-xs text-rocom-primary-outline transition-colors hover:text-rocom-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rocom-primary"
            @click="openRecentPosts($event.currentTarget)"
          >
            查看全部
          </button>
        </div>
        <nav class="space-y-1" aria-label="最新文章">
          <NuxtLink v-for="post in recentPosts" :key="post.id" :to="`/posts/${post.slug}`" class="group block rounded-md px-2 py-1.5 transition-colors hover:bg-rocom-control">
            <span class="block line-clamp-2 text-sm leading-5 text-rocom-text-secondary group-hover:text-rocom-primary-outline">{{ post.title }}</span>
            <span v-if="post.published_at" class="mt-1 inline-flex items-center gap-1 text-[11px] text-rocom-text-caption"><CalendarDays :size="11" />{{ formatDate(post.published_at) }}</span>
          </NuxtLink>
        </nav>
      </section>

      <section v-if="stats" class="sidebar-widget">
        <div class="sidebar-widget-title"><BarChart3 :size="15" />站点统计</div>
        <div class="grid grid-cols-2 gap-2">
          <div class="sidebar-stat"><span>今日 PV</span><strong>{{ stats.today_pv }}</strong></div>
          <div class="sidebar-stat"><span>文章</span><strong>{{ stats.published_posts }}</strong></div>
          <div class="sidebar-stat"><span>分类</span><strong>{{ stats.categories }}</strong></div>
          <div class="sidebar-stat"><span>标签</span><strong>{{ stats.tags }}</strong></div>
        </div>
        <p class="mt-3 flex items-center gap-1 text-[11px] text-rocom-text-caption"><MessageCircle :size="11" />已通过评论 {{ stats.approved_comments }}</p>
      </section>
    </template>
  </aside>
</template>
