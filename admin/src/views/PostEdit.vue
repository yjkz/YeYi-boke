<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsApi, type PostCreate } from '@/api/posts'
import { categoriesApi, type Category } from '@/api/categories'
import { tagsApi, type Tag } from '@/api/tags'
import api from '@/api/index'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const loading = ref(false)
const categoryOptions = ref<Category[]>([])
const tagOptions = ref<Tag[]>([])

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
  const [catRes, tagRes] = await Promise.all([
    categoriesApi.list(),
    tagsApi.list(),
  ])
  categoryOptions.value = catRes.data
  tagOptions.value = tagRes.data

  if (isEdit.value) {
    const { data } = await postsApi.getById(Number(route.params.id))
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

const handleCoverUpload = async (options: any) => {
  const formData = new FormData()
  formData.append('file', options.file)
  const { data } = await api.post('/api/v1/admin/upload', formData)
  form.value.cover_image = data.url
  ElMessage.success('封面已上传')
}
</script>

<template>
  <div class="max-w-4xl">
    <el-form label-position="top">
      <el-form-item label="标题">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item label="Slug（可选）">
        <el-input v-model="form.slug" placeholder="留空则从标题自动生成" />
        <div class="text-xs text-gray-400 mt-1">文章的 URL 标识，如 my-first-post。留空会根据标题自动生成拼音格式。</div>
      </el-form-item>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" clearable class="w-full">
            <el-option v-for="cat in categoryOptions" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="form.tag_ids" placeholder="选择标签" multiple clearable class="w-full">
            <el-option v-for="tag in tagOptions" :key="tag.id" :label="tag.name" :value="tag.id" />
          </el-select>
        </el-form-item>
      </div>
      <el-form-item label="摘要">
        <el-input v-model="form.excerpt" type="textarea" :rows="2" />
      </el-form-item>
      <el-form-item label="封面图">
        <div class="flex items-center gap-3 w-full">
          <el-upload :http-request="handleCoverUpload" :show-file-list="false" accept="image/*">
            <el-button size="small">上传封面</el-button>
          </el-upload>
          <el-input v-model="form.cover_image" placeholder="或输入图片 URL" class="flex-1" />
        </div>
        <img v-if="form.cover_image" :src="form.cover_image" class="mt-2 max-h-40 rounded-lg object-cover" />
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
