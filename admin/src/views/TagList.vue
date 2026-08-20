<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { tagsApi, type Tag, type TagInput } from '@/api/tags'
import { ElMessage, ElMessageBox } from 'element-plus'

const tags = ref<Tag[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = ref<TagInput>({ name: '', slug: '' })
const loading = ref(false)

const fetchTags = async () => {
  const { data } = await tagsApi.list()
  tags.value = data
}

const handleCreate = async () => {
  loading.value = true
  try {
    if (editingId.value) await tagsApi.update(editingId.value, form.value)
    else await tagsApi.create(form.value)
    ElMessage.success(editingId.value ? '已更新' : '已创建')
    dialogVisible.value = false
    resetForm()
    await fetchTags()
  } finally { loading.value = false }
}
const resetForm = () => { editingId.value = null; form.value = { name: '', slug: '' } }
const editTag = (tag: Tag) => { editingId.value = tag.id; form.value = { name: tag.name, slug: tag.slug }; dialogVisible.value = true }
const removeTag = async (tag: Tag) => { await ElMessageBox.confirm(`删除标签“${tag.name}”？`, '确认删除', { type: 'warning' }); await tagsApi.delete(tag.id); ElMessage.success('已删除'); await fetchTags() }

onMounted(fetchTags)
</script>

<template>
  <div>
    <div class="mb-4 flex justify-between items-center">
      <h3 class="text-lg font-semibold">标签管理</h3>
      <el-button type="primary" @click="resetForm(); dialogVisible = true">新建标签</el-button>
    </div>

    <el-table :data="tags" stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="slug" label="Slug" />
      <el-table-column label="操作" width="160"><template #default="{ row }"><el-button link type="primary" @click="editTag(row)">编辑</el-button><el-button link type="danger" @click="removeTag(row)">删除</el-button></template></el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑标签' : '新建标签'" width="400px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="Slug"><el-input v-model="form.slug" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleCreate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
