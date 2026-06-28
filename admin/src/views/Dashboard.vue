<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { statsApi, type StatsOverview } from '@/api/stats'
import { Eye, FileText, MessageSquare } from 'lucide-vue-next'

const stats = ref<StatsOverview | null>(null)

onMounted(async () => {
  const { data } = await statsApi.getOverview()
  stats.value = data
})
</script>

<template>
  <div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6 mb-8">
      <div class="bg-rocom-surface-paper rounded-2xl shadow-paper border border-rocom-outline p-6 flex items-start gap-4">
        <div class="w-10 h-10 rounded-xl bg-rocom-primary-soft flex items-center justify-center shrink-0">
          <Eye :size="20" class="text-rocom-primary-outline" />
        </div>
        <div>
          <div class="text-sm text-rocom-text-caption">今日 PV</div>
          <div class="text-2xl font-bold text-rocom-text-strong mt-1">{{ stats?.today_pv ?? '-' }}</div>
        </div>
      </div>
      <div class="bg-rocom-surface-paper rounded-2xl shadow-paper border border-rocom-outline p-6 flex items-start gap-4">
        <div class="w-10 h-10 rounded-xl bg-rocom-accent-blue/10 flex items-center justify-center shrink-0">
          <FileText :size="20" class="text-rocom-accent-blue" />
        </div>
        <div>
          <div class="text-sm text-rocom-text-caption">文章总数</div>
          <div class="text-2xl font-bold text-rocom-text-strong mt-1">{{ stats?.total_posts ?? '-' }}</div>
        </div>
      </div>
      <div class="bg-rocom-surface-paper rounded-2xl shadow-paper border border-rocom-outline p-6 flex items-start gap-4">
        <div class="w-10 h-10 rounded-xl bg-rocom-success/10 flex items-center justify-center shrink-0">
          <MessageSquare :size="20" class="text-rocom-success" />
        </div>
        <div>
          <div class="text-sm text-rocom-text-caption">评论总数</div>
          <div class="text-2xl font-bold text-rocom-text-strong mt-1">{{ stats?.total_comments ?? '-' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
