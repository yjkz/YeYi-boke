<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { configApi, type SiteConfig } from '@/api/config'
import api from '@/api/index'
import { ElMessage } from 'element-plus'

const form = ref<SiteConfig>({
  site_title: '',
  site_subtitle: '',
  logo_url: '',
  avatar_url: '',
  favicon_url: '',
  about_content: '',
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

const handleLogoUpload = async (options: any) => {
  const formData = new FormData()
  formData.append('file', options.file)
  const { data } = await api.post('/api/v1/admin/upload', formData)
  form.value.logo_url = data.url
  ElMessage.success('Logo 已上传')
}

const handleFaviconUpload = async (options: any) => {
  const formData = new FormData()
  formData.append('file', options.file)
  const { data } = await api.post('/api/v1/admin/upload', formData)
  form.value.favicon_url = data.url
  ElMessage.success('Favicon 已上传')
}

const handleAvatarUpload = async (options: any) => {
  const formData = new FormData()
  formData.append('file', options.file)
  const { data } = await api.post('/api/v1/admin/upload', formData)
  form.value.avatar_url = data.url
  ElMessage.success('头像已上传')
}
</script>

<template>
  <div class="max-w-2xl">
    <el-form label-position="top">
      <el-form-item label="站点标题"><el-input v-model="form.site_title" /></el-form-item>
      <el-form-item label="副标题"><el-input v-model="form.site_subtitle" /></el-form-item>

      <el-form-item label="侧栏头像">
        <div class="flex items-center gap-3 w-full">
          <el-upload :http-request="handleAvatarUpload" :show-file-list="false" accept="image/*">
            <el-button size="small">上传头像</el-button>
          </el-upload>
          <el-input v-model="form.avatar_url" placeholder="或输入图片 URL" class="flex-1" />
        </div>
        <img v-if="form.avatar_url" :src="form.avatar_url" class="mt-2 h-16 w-16 rounded-full object-cover" />
      </el-form-item>

      <el-form-item label="Logo">
        <div class="flex items-center gap-3 w-full">
          <el-upload :http-request="handleLogoUpload" :show-file-list="false" accept="image/*">
            <el-button size="small">上传 Logo</el-button>
          </el-upload>
          <el-input v-model="form.logo_url" placeholder="或输入图片 URL" class="flex-1" />
        </div>
        <img v-if="form.logo_url" :src="form.logo_url" class="mt-2 h-10 object-contain rounded" />
      </el-form-item>

      <el-form-item label="Favicon">
        <div class="flex items-center gap-3 w-full">
          <el-upload :http-request="handleFaviconUpload" :show-file-list="false" accept="image/*">
            <el-button size="small">上传 Favicon</el-button>
          </el-upload>
          <el-input v-model="form.favicon_url" placeholder="或输入图片 URL" class="flex-1" />
        </div>
        <img v-if="form.favicon_url" :src="form.favicon_url" class="mt-2 w-8 h-8 object-contain rounded" />
      </el-form-item>

      <el-form-item label="关于页面内容">
        <el-input v-model="form.about_content" type="textarea" :rows="8" placeholder="支持 Markdown 格式" />
        <div class="text-xs text-gray-400 mt-1">支持 Markdown 格式，会渲染为 HTML 显示在前端关于页面。</div>
      </el-form-item>

      <el-form-item label="页脚文字"><el-input v-model="form.footer_text" /></el-form-item>
      <el-form-item label="开启评论"><el-switch v-model="form.comment_enabled" /></el-form-item>
      <el-form-item label="评论需审核"><el-switch v-model="form.comment_need_review" /></el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
