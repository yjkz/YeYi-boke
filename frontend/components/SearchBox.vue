<script setup lang="ts">
import { Search } from 'lucide-vue-next'

const router = useRouter()
const query = ref('')

const doSearch = () => {
  if (query.value.trim()) {
    router.push({ path: '/search', query: { q: query.value.trim() } })
  }
}
</script>

<template>
  <form @submit.prevent="doSearch" class="relative">
    <input
      v-model="query"
      type="text"
      placeholder="搜索..."
      aria-label="搜索文章"
      class="w-36 h-11 px-3 pr-10 text-sm rounded-pill bg-rocom-control border border-rocom-outline focus:outline-none focus:ring-2 focus:ring-rocom-primary text-rocom-text placeholder:text-rocom-text-disabled"
    />
    <button type="submit" class="absolute right-3 top-1/2 -translate-y-1/2 text-rocom-text-muted hover:text-rocom-primary transition-colors" aria-label="搜索">
      <Search :size="16" />
    </button>
  </form>
</template>
