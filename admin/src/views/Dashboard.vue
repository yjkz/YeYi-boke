<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { statsApi, type StatsOverview } from '@/api/stats'

const stats = ref<StatsOverview | null>(null)

onMounted(async () => {
  const { data } = await statsApi.getOverview()
  stats.value = data
})
</script>

<template>
  <div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">今日 PV</div>
        <div class="text-3xl font-bold text-yellow-500">{{ stats?.today_pv ?? '-' }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">文章总数</div>
        <div class="text-3xl font-bold text-blue-500">{{ stats?.total_posts ?? '-' }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">评论总数</div>
        <div class="text-3xl font-bold text-green-500">{{ stats?.total_comments ?? '-' }}</div>
      </div>
    </div>
  </div>
</template>
