<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const logout = async () => {
  try { await auth.logout() } catch {}
  router.push('/login')
}

const menuItems = [
  { path: '/', label: '仪表盘', icon: '📊' },
  { path: '/posts', label: '文章管理', icon: '📝' },
  { path: '/comments', label: '评论管理', icon: '💬' },
  { path: '/categories', label: '分类管理', icon: '📁' },
  { path: '/tags', label: '标签管理', icon: '🏷️' },
  { path: '/settings', label: '站点配置', icon: '⚙️' },
  { path: '/analytics', label: '访问统计', icon: '📈' },
]
</script>

<template>
  <el-container class="h-screen">
    <el-aside width="220px" class="bg-rocom-bg-parchment border-r border-rocom-outline">
      <div class="h-16 flex items-center justify-center font-bold text-lg text-rocom-text-strong tracking-wider">
        YeYi 管理后台
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="transparent"
        text-color="var(--rocom-text-secondary)"
        active-text-color="var(--rocom-primary-outline)"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.path"
          :index="item.path"
          class="hover:bg-rocom-control-hover"
        >
          <span class="mr-2">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="h-16 flex items-center justify-between border-b border-rocom-outline bg-rocom-surface-paper px-6">
        <h2 class="text-lg font-semibold text-rocom-text-strong">{{ $route.name }}</h2>
        <div class="flex items-center gap-4">
          <span class="text-sm text-rocom-text-secondary">{{ auth.user?.username }}</span>
          <el-button size="small" @click="logout">退出</el-button>
        </div>
      </el-header>

      <el-main class="bg-rocom-bg p-6">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
