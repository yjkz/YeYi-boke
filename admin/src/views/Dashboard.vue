<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { statsApi, type StatsOverview } from '@/api/stats'
import { Eye, FileText, MessageSquare } from 'lucide-vue-next'

const stats = ref<StatsOverview | null>(null)
const error = ref('')

onMounted(async () => {
  try { const { data } = await statsApi.getOverview(); stats.value = data } catch { error.value = '统计加载失败，请稍后重试。' }
})
</script>

<template>
  <div class="max-w-6xl">
    <p v-if="error" class="mb-4 text-rocom-danger">{{ error }}</p>
    <div class="grid grid-cols-1 gap-4 md:grid-cols-3 lg:gap-5">
      <div class="flex items-start gap-4 rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 shadow-sm sm:p-5">
        <div class="w-10 h-10 rounded-lg bg-rocom-primary-soft flex items-center justify-center shrink-0">
          <Eye :size="20" class="text-rocom-primary-outline" />
        </div>
        <div>
          <div class="text-sm text-rocom-text-caption">今日 PV</div>
          <div class="text-2xl font-bold text-rocom-text-strong mt-1">{{ stats?.today_pv ?? '-' }}</div>
        </div>
      </div>
      <div class="flex items-start gap-4 rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 shadow-sm sm:p-5">
        <div class="w-10 h-10 rounded-lg bg-rocom-accent-blue/10 flex items-center justify-center shrink-0">
          <FileText :size="20" class="text-rocom-accent-blue" />
        </div>
        <div>
          <div class="text-sm text-rocom-text-caption">文章总数</div>
          <div class="text-2xl font-bold text-rocom-text-strong mt-1">{{ stats?.total_posts ?? '-' }}</div>
        </div>
      </div>
      <div class="flex items-start gap-4 rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 shadow-sm sm:p-5">
        <div class="w-10 h-10 rounded-lg bg-rocom-success/10 flex items-center justify-center shrink-0">
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
