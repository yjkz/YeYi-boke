<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { commentsApi, type Comment } from '@/api/comments'
import { ElMessage, ElMessageBox } from 'element-plus'

const comments = ref<Comment[]>([])
const total = ref(0)
const page = ref(1)
const statusFilter = ref('')
const postTitleFilter = ref('')
const loading = ref(false)

const statusMap: Record<string, string> = { pending: 'warning', approved: 'success', rejected: 'danger' }

const fetchComments = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: 20 }
    if (statusFilter.value) params.status = statusFilter.value
    if (postTitleFilter.value.trim()) params.post_title = postTitleFilter.value.trim()
    const { data } = await commentsApi.list(params)
    comments.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

const handleApprove = async (comment: Comment) => {
  await commentsApi.updateStatus(comment.id, 'approved')
  ElMessage.success('已通过')
  fetchComments()
}

const handleReject = async (comment: Comment) => {
  await commentsApi.updateStatus(comment.id, 'rejected')
  ElMessage.success('已拒绝')
  fetchComments()
}

const handleDelete = async (comment: Comment) => {
  await ElMessageBox.confirm('确定删除这条评论？', '确认')
  await commentsApi.delete(comment.id)
  ElMessage.success('已删除')
  fetchComments()
}

const statusLabel = (s: string) => ({ pending: '待审核', approved: '已通过', rejected: '已拒绝' })[s] || s

onMounted(fetchComments)
</script>

<template>
  <div>
    <div class="mb-4 flex flex-wrap items-center gap-3">
      <el-select v-model="statusFilter" placeholder="筛选状态" clearable @change="fetchComments">
        <el-option label="待审核" value="pending" />
        <el-option label="已通过" value="approved" />
        <el-option label="已拒绝" value="rejected" />
      </el-select>
      <el-input v-model="postTitleFilter" clearable placeholder="文章标题" class="w-52" @keyup.enter="page = 1; fetchComments" @clear="page = 1; fetchComments" />
      <el-button @click="page = 1; fetchComments">筛选</el-button>
      <el-button @click="statusFilter = ''; postTitleFilter = ''; page = 1; fetchComments">重置</el-button>
    </div>

    <el-table :data="comments" v-loading="loading" stripe>
      <el-table-column prop="nickname" label="昵称" width="120" />
      <el-table-column label="文章" min-width="180"><template #default="{ row }"><a :href="`/posts/${row.post_slug}`" target="_blank" class="text-rocom-accent-blue hover:underline">{{ row.post_title }}</a></template></el-table-column>
      <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="(statusMap[row.status as keyof typeof statusMap] ?? 'info') as any" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="180">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleString('zh-CN') }}</template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <el-button v-if="row.status !== 'approved'" size="small" type="success" @click="handleApprove(row)">通过</el-button>
          <el-button v-if="row.status !== 'rejected'" size="small" type="warning" @click="handleReject(row)">拒绝</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <p v-if="!loading && !comments.length" class="py-8 text-center text-rocom-text-muted">暂无评论</p>

    <el-pagination
      v-model:current-page="page"
      :total="total"
      :page-size="20"
      layout="prev, pager, next"
      class="mt-4 justify-center"
      @current-change="fetchComments"
    />
  </div>
</template>
