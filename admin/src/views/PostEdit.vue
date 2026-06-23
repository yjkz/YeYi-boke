<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsApi, type PostCreate } from '@/api/posts'
import api from '@/api/index'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const loading = ref(false)

const form = ref<PostCreate>({
  title: '',
  slug: '',
  content_md: '',
  excerpt: '',
  cover_image: '',
  category_id: undefined,
  tag_ids: [],
  is_top: false,
})

onMounted(async () => {
  if (isEdit.value) {
    const { data } = await postsApi.get(route.params.id as string)
    form.value = {
      title: data.title,
      slug: data.slug,
      content_md: data.content_md || '',
      excerpt: data.excerpt || '',
      cover_image: data.cover_image || '',
      category_id: data.category?.id,
      tag_ids: data.tags.map(t => t.id),
      is_top: data.is_top,
    }
  }
})

const handleSave = async () => {
  loading.value = true
  try {
    if (isEdit.value) {
      await postsApi.update(Number(route.params.id), form.value)
      ElMessage.success('已更新')
    } else {
      await postsApi.create(form.value)
      ElMessage.success('已创建')
    }
    router.push('/posts')
  } finally {
    loading.value = false
  }
}

const handleUpload = async (options: any) => {
  const formData = new FormData()
  formData.append('file', options.file)
  const { data } = await api.post('/api/v1/admin/upload', formData)
  form.value.content_md += `\n![${options.file.name}](${data.url})\n`
  ElMessage.success('已上传')
}
</script>

<template>
  <div class="max-w-4xl">
    <el-form label-position="top">
      <el-form-item label="标题">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item label="Slug">
        <el-input v-model="form.slug" />
      </el-form-item>
      <el-form-item label="摘要">
        <el-input v-model="form.excerpt" type="textarea" :rows="2" />
      </el-form-item>
      <el-form-item label="封面图 URL">
        <el-input v-model="form.cover_image" />
      </el-form-item>
      <el-form-item label="内容 (Markdown)">
        <div class="mb-2">
          <el-upload :http-request="handleUpload" :show-file-list="false" accept="image/*">
            <el-button size="small">上传图片</el-button>
          </el-upload>
        </div>
        <el-input v-model="form.content_md" type="textarea" :rows="20" />
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.is_top">置顶</el-checkbox>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
