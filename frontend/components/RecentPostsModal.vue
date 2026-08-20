<script setup lang="ts">
import { X, CalendarDays } from 'lucide-vue-next'

interface PostItem {
  id: number
  title: string
  slug: string
  published_at?: string | null
}

interface PostListResponse {
  items: PostItem[]
  total: number
  page: number
  page_size: number
}

const api = useApi()
const { recentPostsOpen, closeRecentPosts } = useRecentPostsModal()
const closeButton = ref<HTMLButtonElement | null>(null)
const page = ref(1)
const pageSize = 10
const posts = ref<PostListResponse | null>(null)
const status = ref<'idle' | 'pending' | 'success' | 'error'>('idle')
const errorMessage = ref('')
let previousOverflow = ''

const totalPages = computed(() => posts.value ? Math.ceil(posts.value.total / posts.value.page_size) : 1)

const formatDate = (value?: string | null) => value
  ? new Date(value).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
  : '未发布日期'

const loadPosts = async () => {
  status.value = 'pending'
  errorMessage.value = ''
  try {
    posts.value = await api.get<PostListResponse>('/posts', {
      page: page.value,
      page_size: pageSize,
      sort: 'latest',
    })
    status.value = 'success'
  } catch (error: any) {
    status.value = 'error'
    errorMessage.value = error?.data?.detail || error?.message || '文章加载失败，请稍后重试。'
  }
}

const changePage = (nextPage: number) => {
  if (nextPage < 1 || nextPage > totalPages.value || nextPage === page.value) return
  page.value = nextPage
  loadPosts()
}

const onKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') closeRecentPosts()
}

watch(recentPostsOpen, async (open) => {
  if (import.meta.server) return
  if (open) {
    page.value = 1
    previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', onKeydown)
    await loadPosts()
    await nextTick()
    closeButton.value?.focus()
  } else {
    document.body.style.overflow = previousOverflow
    window.removeEventListener('keydown', onKeydown)
  }
})

onUnmounted(() => {
  if (import.meta.client) {
    document.body.style.overflow = previousOverflow
    window.removeEventListener('keydown', onKeydown)
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition name="announcement-modal" appear>
      <div
        v-if="recentPostsOpen"
        class="fixed inset-0 z-[100] flex items-center justify-center bg-black/35 p-4 sm:p-6"
        role="presentation"
        @click.self="closeRecentPosts"
      >
        <section
          class="announcement-dialog flex max-h-[80vh] w-full max-w-[720px] flex-col overflow-hidden rounded-2xl border border-rocom-outline bg-rocom-surface-strong shadow-float"
          role="dialog"
          aria-modal="true"
          aria-labelledby="recent-posts-dialog-title"
        >
          <header class="flex shrink-0 items-center justify-between gap-4 border-b border-rocom-outline px-5 py-4 sm:px-6">
            <h2 id="recent-posts-dialog-title" class="text-lg font-bold text-rocom-text-strong">全部文章</h2>
            <button
              ref="closeButton"
              type="button"
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-rocom-text-secondary transition-colors hover:bg-rocom-control hover:text-rocom-text-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rocom-primary"
              aria-label="关闭全部文章"
              @click="closeRecentPosts"
            >
              <X :size="18" />
            </button>
          </header>

          <div class="min-h-0 overflow-y-auto px-5 py-5 sm:px-6 sm:py-6">
            <p v-if="status === 'pending'" class="py-12 text-center text-sm text-rocom-text-muted">加载中...</p>
            <p v-else-if="status === 'error'" class="py-12 text-center text-sm text-rocom-danger">{{ errorMessage }}</p>
            <p v-else-if="status === 'success' && !posts?.items.length" class="py-12 text-center text-sm text-rocom-text-muted">暂无文章</p>
            <nav v-else-if="posts" class="space-y-2" aria-label="全部文章">
              <NuxtLink
                v-for="post in posts.items"
                :key="post.id"
                :to="`/posts/${post.slug}`"
                class="group block rounded-xl border border-transparent bg-rocom-control px-4 py-3 transition-colors hover:border-rocom-outline hover:bg-rocom-control-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rocom-primary"
                @click="closeRecentPosts"
              >
                <span class="block text-sm font-semibold leading-6 text-rocom-text-strong group-hover:text-rocom-primary-outline">{{ post.title }}</span>
                <span class="mt-1 inline-flex items-center gap-1 text-xs text-rocom-text-caption"><CalendarDays :size="12" />{{ formatDate(post.published_at) }}</span>
              </NuxtLink>
            </nav>

            <Pagination v-if="status === 'success'" :page="page" :total-pages="totalPages" @change="changePage" />
          </div>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>
