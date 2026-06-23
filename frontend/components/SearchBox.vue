<script setup lang="ts">
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
      class="w-36 h-9 px-3 pr-8 text-sm rounded-pill bg-rocom-control border border-rocom-outline focus:outline-none focus:ring-2 focus:ring-rocom-primary text-rocom-text placeholder:text-rocom-text-disabled"
    />
    <button type="submit" class="absolute right-2 top-1/2 -translate-y-1/2 text-rocom-text-muted hover:text-rocom-primary">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </button>
  </form>
</template>
