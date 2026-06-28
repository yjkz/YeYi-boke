<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { postsApi, type Post } from '@/api/posts'
import { ElMessage, ElMessageBox } from 'element-plus'

const posts = ref<Post[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)

const fetchPosts = async () => {
  loading.value = true
  try {
    const { data } = await postsApi.list({ page: page.value, page_size: 20 })
    posts.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

const handlePublish = async (post: Post) => {
  await postsApi.publish(post.id)
  ElMessage.success('已发布')
  fetchPosts()
}

const handleDraft = async (post: Post) => {
  await postsApi.draft(post.id)
  ElMessage.success('已下架')
  fetchPosts()
}

const handleDelete = async (post: Post) => {
  await ElMessageBox.confirm('确定删除这篇文章？', '确认')
  await postsApi.delete(post.id)
  ElMessage.success('已删除')
  fetchPosts()
}

onMounted(fetchPosts)
</script>

<template>
  <div>
    <div class="mb-4 flex justify-between items-center">
      <h3 class="text-lg font-semibold">文章列表</h3>
      <el-button type="primary" @click="$router.push('/posts/new')">新建文章</el-button>
    </div>

    <el-table :data="posts" v-loading="loading" stripe>
      <el-table-column prop="title" label="标题" min-width="200">
        <template #default="{ row }">
          <router-link :to="`/posts/${row.id}/edit`" class="text-rocom-accent-blue hover:text-rocom-primary transition-colors">
            {{ row.title }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'published' ? 'success' : 'info'" size="small">
            {{ row.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="view_count" label="阅读" width="80" />
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/posts/${row.id}/edit`)">编辑</el-button>
          <el-button v-if="row.status === 'draft'" size="small" type="success" @click="handlePublish(row)">发布</el-button>
          <el-button v-else size="small" type="warning" @click="handleDraft(row)">下架</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      :total="total"
      :page-size="20"
      layout="prev, pager, next"
      class="mt-4 justify-center"
      @current-change="fetchPosts"
    />
  </div>
</template>
