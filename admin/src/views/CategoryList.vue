<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { categoriesApi, type Category } from '@/api/categories'
import { ElMessage } from 'element-plus'

const categories = ref<Category[]>([])
const dialogVisible = ref(false)
const form = ref({ name: '', slug: '', description: '' })

const fetchCategories = async () => {
  const { data } = await categoriesApi.list()
  categories.value = data
}

const handleCreate = async () => {
  await categoriesApi.create(form.value)
  ElMessage.success('已创建')
  dialogVisible.value = false
  form.value = { name: '', slug: '', description: '' }
  fetchCategories()
}

onMounted(fetchCategories)
</script>

<template>
  <div>
    <div class="mb-4 flex justify-between items-center">
      <h3 class="text-lg font-semibold">分类管理</h3>
      <el-button type="primary" @click="dialogVisible = true">新建分类</el-button>
    </div>

    <el-table :data="categories" stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="slug" label="Slug" />
      <el-table-column prop="description" label="描述" />
    </el-table>

    <el-dialog v-model="dialogVisible" title="新建分类" width="400px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="Slug"><el-input v-model="form.slug" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>
