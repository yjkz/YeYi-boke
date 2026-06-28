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
      <div class="bg-rocom-surface-paper rounded-2xl shadow-paper border border-rocom-outline p-6">
        <div class="text-sm text-rocom-text-caption">今日 PV</div>
        <div class="text-3xl font-bold text-rocom-primary mt-2">{{ stats?.today_pv ?? '-' }}</div>
      </div>
      <div class="bg-rocom-surface-paper rounded-2xl shadow-paper border border-rocom-outline p-6">
        <div class="text-sm text-rocom-text-caption">文章总数</div>
        <div class="text-3xl font-bold text-rocom-accent-blue mt-2">{{ stats?.total_posts ?? '-' }}</div>
      </div>
      <div class="bg-rocom-surface-paper rounded-2xl shadow-paper border border-rocom-outline p-6">
        <div class="text-sm text-rocom-text-caption">评论总数</div>
        <div class="text-3xl font-bold text-rocom-success mt-2">{{ stats?.total_comments ?? '-' }}</div>
      </div>
    </div>
  </div>
</template>
