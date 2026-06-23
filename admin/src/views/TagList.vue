<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { tagsApi, type Tag } from '@/api/tags'
import { ElMessage } from 'element-plus'

const tags = ref<Tag[]>([])
const dialogVisible = ref(false)
const form = ref({ name: '', slug: '' })

const fetchTags = async () => {
  const { data } = await tagsApi.list()
  tags.value = data
}

const handleCreate = async () => {
  await tagsApi.create(form.value)
  ElMessage.success('已创建')
  dialogVisible.value = false
  form.value = { name: '', slug: '' }
  fetchTags()
}

onMounted(fetchTags)
</script>

<template>
  <div>
    <div class="mb-4 flex justify-between items-center">
      <h3 class="text-lg font-semibold">标签管理</h3>
      <el-button type="primary" @click="dialogVisible = true">新建标签</el-button>
    </div>

    <el-table :data="tags" stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="slug" label="Slug" />
    </el-table>

    <el-dialog v-model="dialogVisible" title="新建标签" width="400px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="Slug"><el-input v-model="form.slug" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>
