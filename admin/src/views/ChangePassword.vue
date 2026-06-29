<script setup lang="ts">
import { ref } from 'vue'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'
import { Lock } from 'lucide-vue-next'

const form = ref({
  current_password: '',
  new_password: '',
  confirm_password: '',
})
const loading = ref(false)

const handleChangePassword = async () => {
  if (!form.value.current_password || !form.value.new_password) {
    ElMessage.error('请填写所有字段')
    return
  }
  if (form.value.new_password.length < 6) {
    ElMessage.error('新密码至少 6 位')
    return
  }
  if (form.value.new_password !== form.value.confirm_password) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    await authApi.changePassword({
      current_password: form.value.current_password,
      new_password: form.value.new_password,
    })
    ElMessage.success('密码已修改')
    form.value = { current_password: '', new_password: '', confirm_password: '' }
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '修改失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-md">
    <div class="bg-rocom-surface-paper rounded-2xl shadow-paper border border-rocom-outline p-6">
      <div class="flex items-center gap-2 mb-6">
        <Lock :size="20" class="text-rocom-primary" />
        <h3 class="text-lg font-semibold text-rocom-text-strong">修改密码</h3>
      </div>

      <el-form label-position="top" @submit.prevent="handleChangePassword">
        <el-form-item label="当前密码">
          <el-input v-model="form.current_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="form.new_password" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="form.confirm_password" type="password" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" class="w-full" @click="handleChangePassword">
          修改密码
        </el-button>
      </el-form>
    </div>
  </div>
</template>
