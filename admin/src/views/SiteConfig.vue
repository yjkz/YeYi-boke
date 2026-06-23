<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { configApi, type SiteConfig } from '@/api/config'
import { ElMessage } from 'element-plus'

const form = ref<SiteConfig>({
  site_title: '',
  site_subtitle: '',
  logo_url: '',
  favicon_url: '',
  footer_text: '',
  social_links: {},
  comment_enabled: true,
  comment_need_review: true,
})
const loading = ref(false)

onMounted(async () => {
  const { data } = await configApi.get()
  form.value = data
})

const handleSave = async () => {
  loading.value = true
  try {
    await configApi.update(form.value)
    ElMessage.success('已保存')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl">
    <el-form label-position="top">
      <el-form-item label="站点标题"><el-input v-model="form.site_title" /></el-form-item>
      <el-form-item label="副标题"><el-input v-model="form.site_subtitle" /></el-form-item>
      <el-form-item label="Logo URL"><el-input v-model="form.logo_url" /></el-form-item>
      <el-form-item label="Favicon URL"><el-input v-model="form.favicon_url" /></el-form-item>
      <el-form-item label="页脚文字"><el-input v-model="form.footer_text" /></el-form-item>
      <el-form-item label="开启评论"><el-switch v-model="form.comment_enabled" /></el-form-item>
      <el-form-item label="评论需审核"><el-switch v-model="form.comment_need_review" /></el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
