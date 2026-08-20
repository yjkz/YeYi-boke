<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { categoriesApi, type Category, type CategoryInput } from '@/api/categories'
import { ElMessage, ElMessageBox } from 'element-plus'

const categories = ref<Category[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = ref<CategoryInput>({ name: '', slug: '', description: '', sort_order: 0 })
const loading = ref(false)

const fetchCategories = async () => {
  const { data } = await categoriesApi.list()
  categories.value = data
}

const handleCreate = async () => {
  loading.value = true
  try {
    if (editingId.value) await categoriesApi.update(editingId.value, form.value)
    else await categoriesApi.create(form.value)
    ElMessage.success(editingId.value ? '已更新' : '已创建')
    dialogVisible.value = false
    resetForm()
    await fetchCategories()
  } finally { loading.value = false }
}

const resetForm = () => { editingId.value = null; form.value = { name: '', slug: '', description: '', sort_order: 0 } }
const editCategory = (category: Category) => { editingId.value = category.id; form.value = { name: category.name, slug: category.slug, description: category.description || '', sort_order: category.sort_order }; dialogVisible.value = true }
const removeCategory = async (category: Category) => { await ElMessageBox.confirm(`删除分类“${category.name}”？文章会保留但分类会被清空。`, '确认删除', { type: 'warning' }); await categoriesApi.delete(category.id); ElMessage.success('已删除'); await fetchCategories() }

onMounted(fetchCategories)
</script>

<template>
  <div>
    <div class="mb-4 flex justify-between items-center">
      <h3 class="text-lg font-semibold">分类管理</h3>
      <el-button type="primary" @click="resetForm(); dialogVisible = true">新建分类</el-button>
    </div>

    <el-table :data="categories" stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="slug" label="Slug" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column label="操作" width="160"><template #default="{ row }"><el-button link type="primary" @click="editCategory(row)">编辑</el-button><el-button link type="danger" @click="removeCategory(row)">删除</el-button></template></el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑分类' : '新建分类'" width="400px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="Slug"><el-input v-model="form.slug" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" :max="9999" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleCreate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
