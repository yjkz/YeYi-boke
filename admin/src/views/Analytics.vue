<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { statsApi, type TrendPoint } from '@/api/stats'

const trend = ref<TrendPoint[]>([])
const days = ref(7)

const fetchTrend = async () => {
  const { data } = await statsApi.getTrend(days.value)
  trend.value = data.data
}

onMounted(fetchTrend)
</script>

<template>
  <div>
    <div class="mb-4 flex items-center gap-4">
      <el-radio-group v-model="days" @change="fetchTrend">
        <el-radio-button :value="7">7天</el-radio-button>
        <el-radio-button :value="30">30天</el-radio-button>
      </el-radio-group>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold mb-4">访问趋势</h3>
      <el-table :data="trend" stripe>
        <el-table-column prop="date" label="日期" />
        <el-table-column prop="page_views" label="PV" />
        <el-table-column prop="unique_visitors" label="UV" />
      </el-table>
      <p v-if="!trend.length" class="text-gray-400 text-center py-8">暂无数据</p>
    </div>
  </div>
</template>
