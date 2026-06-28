<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { User, Lock } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()
const form = ref({ username: '', password: '' })
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    router.push('/')
  } catch {
    ElMessage.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-rocom-bg px-4">
    <div class="w-full max-w-sm bg-rocom-surface-paper rounded-2xl shadow-paper border border-rocom-outline p-8">
      <h1 class="text-2xl font-bold text-center mb-8 text-rocom-text-strong tracking-wider">YeYi 管理后台</h1>
      <el-form @submit.prevent="handleLogin" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" size="large">
            <template #prefix>
              <User :size="16" class="text-rocom-text-disabled" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password size="large">
            <template #prefix>
              <Lock :size="16" class="text-rocom-text-disabled" />
            </template>
          </el-input>
        </el-form-item>
        <el-button type="primary" :loading="loading" class="w-full mt-2" size="large" @click="handleLogin">
          {{ loading ? '登录中...' : '登录' }}
        </el-button>
      </el-form>
    </div>
  </div>
</template>
