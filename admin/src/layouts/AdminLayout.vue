<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import {
  LayoutDashboard, FileText, MessageSquare, FolderOpen,
  Tag, Settings, TrendingUp, LogOut, Menu as MenuIcon, X, Lock, Server
} from 'lucide-vue-next'

import { configApi } from '@/api/config'

const auth = useAuthStore()
const router = useRouter()
const sidebarOpen = ref(false)

onMounted(async () => {
  try {
    const { data } = await configApi.get()
    if (data.favicon_url) {
      let link = document.querySelector("link[rel='icon']") as HTMLLinkElement
      if (!link) {
        link = document.createElement('link')
        link.rel = 'icon'
        document.head.appendChild(link)
      }
      link.href = data.favicon_url
    }
    if (data.site_title) {
      document.title = `${data.site_title} - 管理后台`
    }
  } catch {}
})

const logout = async () => {
  try { await auth.logout() } catch {}
  router.push('/login')
}

const menuItems = [
  { path: '/', label: '仪表盘', icon: LayoutDashboard },
  { path: '/posts', label: '文章管理', icon: FileText },
  { path: '/comments', label: '评论管理', icon: MessageSquare },
  { path: '/categories', label: '分类管理', icon: FolderOpen },
  { path: '/tags', label: '标签管理', icon: Tag },
  { path: '/settings', label: '站点配置', icon: Settings },
  { path: '/analytics', label: '访问统计', icon: TrendingUp },
  { path: '/mcp', label: 'MCP 管理', icon: Server },
  { path: '/password', label: '修改密码', icon: Lock },
]
</script>

<template>
  <el-container class="h-screen overflow-hidden">
    <!-- Mobile sidebar overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/40 z-40 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <el-aside
      width="220px"
      class="bg-rocom-bg-parchment border-r border-rocom-outline transition-transform lg:translate-x-0 fixed lg:relative z-50 h-full overflow-y-auto"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
    >
      <div class="h-16 flex items-center justify-between gap-2 px-4">
        <span class="min-w-0 truncate font-bold text-lg text-rocom-text-strong tracking-wider">YeYi 管理后台</span>
        <button class="lg:hidden w-9 h-9 flex items-center justify-center rounded-lg hover:bg-rocom-control transition-colors" @click="sidebarOpen = false" aria-label="关闭侧边栏">
          <X :size="18" class="text-rocom-text-secondary" />
        </button>
      </div>
      <nav aria-label="管理导航">
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
            @click="sidebarOpen = false"
          >
            <component :is="item.icon" :size="18" class="mr-2" />
            <span>{{ item.label }}</span>
          </el-menu-item>
        </el-menu>
      </nav>
    </el-aside>

    <el-container class="min-w-0">
      <el-header class="h-16 shrink-0 flex items-center justify-between border-b border-rocom-outline bg-rocom-surface-paper px-4 sm:px-5 lg:px-6">
        <div class="min-w-0 flex items-center gap-3">
          <button class="lg:hidden w-10 h-10 flex items-center justify-center rounded-lg hover:bg-rocom-control transition-colors" @click="sidebarOpen = true" aria-label="打开菜单">
            <MenuIcon :size="20" class="text-rocom-text" />
          </button>
          <h2 class="truncate text-lg font-semibold text-rocom-text-strong">{{ $route.name }}</h2>
        </div>
        <div class="shrink-0 flex items-center gap-2 sm:gap-4">
          <span class="text-sm text-rocom-text-secondary hidden sm:inline">{{ auth.user?.username }}</span>
          <el-button size="small" @click="logout" aria-label="退出登录">
            <LogOut :size="14" class="mr-1" />
            退出
          </el-button>
        </div>
      </el-header>

      <el-main id="main-content" class="min-w-0 overflow-auto bg-rocom-bg p-4 sm:p-5 lg:p-6">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
