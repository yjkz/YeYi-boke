<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave, onBeforeRouteUpdate, useRoute, useRouter } from 'vue-router'
import {
  Bold,
  Code2,
  Heading2,
  Image as ImageIcon,
  Italic,
  Link,
  List,
  ListOrdered,
  Minus,
  Quote,
  Strikethrough,
} from 'lucide-vue-next'
import { ElMessage, ElMessageBox, type UploadRequestOptions } from 'element-plus'
import katex from 'katex'
import { postsApi, type Post, type PostCreate } from '@/api/posts'
import { categoriesApi, type Category } from '@/api/categories'
import { tagsApi, type Tag } from '@/api/tags'
import api from '@/api/index'
import { renderMarkdown } from '@/utils/markdown'
import { usePostDraftAutosave } from '@/composables/usePostDraftAutosave'

type EditorForm = PostCreate & { tag_ids: number[] }

const route = useRoute()
const router = useRouter()
const postId = ref<number | null>(route.params.id ? Number(route.params.id) : null)
const postStatus = ref<'draft' | 'published'>('draft')
const loading = ref(true)
const saving = ref(false)
const loadError = ref('')
const ready = ref(false)
const activePane = ref<'edit' | 'preview'>('edit')
const categoryOptions = ref<Category[]>([])
const tagOptions = ref<Tag[]>([])
const contentEditor = ref<{ $el?: HTMLElement } | null>(null)
const previewRoot = ref<HTMLElement | null>(null)
const allowRouteChange = ref(false)
let disposed = false

const form = ref<EditorForm>({
  title: '',
  slug: '',
  content_md: '',
  excerpt: '',
  cover_image: '',
  category_id: undefined,
  tag_ids: [],
  is_top: false,
})

const isEdit = computed(() => postId.value !== null)
const isPublished = computed(() => postStatus.value === 'published')
const autosaveEnabled = computed(() => !isPublished.value && Boolean(form.value.title.trim()))
const previewHtml = computed(() => renderMarkdown(form.value.content_md))
const statusText = computed(() => ({
  idle: '未保存',
  unsaved: '未保存',
  saving: '保存中...',
  saved: '已保存',
  error: '保存失败',
} as const)[autosave.status.value])

const serialize = (value: EditorForm) => JSON.stringify({
  title: value.title,
  slug: value.slug || '',
  content_md: value.content_md,
  excerpt: value.excerpt || '',
  cover_image: value.cover_image || '',
  category_id: value.category_id || null,
  tag_ids: [...(value.tag_ids || [])].sort((a, b) => a - b),
  is_top: Boolean(value.is_top),
})

const toPayload = (value: EditorForm): PostCreate => ({
  title: value.title.trim(),
  slug: value.slug?.trim() || undefined,
  content_md: value.content_md,
  excerpt: value.excerpt?.trim() || undefined,
  cover_image: value.cover_image?.trim() || undefined,
  category_id: value.category_id,
  tag_ids: value.tag_ids,
  is_top: value.is_top,
})

const saveDraft = async (snapshot: EditorForm) => {
  if (!snapshot.title.trim() || isPublished.value) return
  const payload = toPayload(snapshot)
  if (postId.value === null) {
    const { data } = await postsApi.create(payload)
    if (disposed) return
    postId.value = data.id
    postStatus.value = 'draft'
    allowRouteChange.value = true
    try {
      await router.replace({ name: 'PostEdit', params: { id: data.id } })
    } finally {
      allowRouteChange.value = false
    }
  } else {
    await postsApi.update(postId.value, payload)
  }
}

const autosave = usePostDraftAutosave({
  value: form,
  enabled: autosaveEnabled,
  ready,
  serialize,
  save: saveDraft,
})

const applyPost = (data: Post) => {
  postId.value = data.id
  form.value = {
    title: data.title,
    slug: data.slug,
    content_md: data.content_md || '',
    excerpt: data.excerpt || '',
    cover_image: data.cover_image || '',
    category_id: data.category?.id,
    tag_ids: data.tags.map(tag => tag.id),
    is_top: data.is_top,
  }
  postStatus.value = data.status as 'draft' | 'published'
  autosave.markSaved(serialize(form.value), 'saved')
}

const resetPost = () => {
  postId.value = null
  postStatus.value = 'draft'
  form.value = {
    title: '',
    slug: '',
    content_md: '',
    excerpt: '',
    cover_image: '',
    category_id: undefined,
    tag_ids: [],
    is_top: false,
  }
  autosave.markSaved(serialize(form.value), 'idle')
}

const loadPost = async (id: number) => {
  const { data } = await postsApi.getById(id)
  applyPost(data)
}

const errorMessage = (error: unknown, fallback: string) => {
  const responseMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail
  return responseMessage || (error instanceof Error ? error.message : fallback)
}

const handleSave = async () => {
  if (!form.value.title.trim()) {
    ElMessage.warning('请先填写标题')
    return
  }
  const creating = postId.value === null
  saving.value = true
  autosave.invalidatePending()
  try {
    await autosave.waitForQueue()
    const payload = toPayload(form.value)
    const response = postId.value === null
      ? await postsApi.create(payload)
      : await postsApi.update(postId.value, payload)
    postId.value = response.data.id
    postStatus.value = response.data.status as 'draft' | 'published'
    autosave.markSaved(serialize(form.value), postId.value === null ? 'idle' : 'saved')
    ElMessage.success(creating ? '已创建' : '已保存')
    await router.push('/posts')
  } catch (error) {
    ElMessage.error(errorMessage(error, '保存失败，请重试'))
  } finally {
    saving.value = false
  }
}

const getTextarea = () => contentEditor.value?.$el?.querySelector('textarea') as HTMLTextAreaElement | null

const replaceSelection = (before: string, after = before) => {
  const textarea = getTextarea()
  if (!textarea) return
  const value = form.value.content_md
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selected = value.slice(start, end)
  const replacement = `${before}${selected || '文本'}${after}`
  form.value.content_md = `${value.slice(0, start)}${replacement}${value.slice(end)}`
  nextTick(() => {
    textarea.focus()
    const selectionStart = start + before.length
    textarea.setSelectionRange(selectionStart, selectionStart + (selected || '文本').length)
  })
}

const prefixLines = (prefix: string) => {
  const textarea = getTextarea()
  if (!textarea) return
  const value = form.value.content_md
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const lineStart = value.lastIndexOf('\n', Math.max(0, start - 1)) + 1
  const lineEndIndex = value.indexOf('\n', end)
  const lineEnd = lineEndIndex === -1 ? value.length : lineEndIndex
  const selectedLines = value.slice(lineStart, lineEnd)
  const replacement = selectedLines.split('\n').map(line => `${prefix}${line}`).join('\n')
  form.value.content_md = `${value.slice(0, lineStart)}${replacement}${value.slice(lineEnd)}`
  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(lineStart, lineStart + replacement.length)
  })
}

const insertBlock = (value: string) => {
  const textarea = getTextarea()
  if (!textarea) return
  const content = form.value.content_md
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  form.value.content_md = `${content.slice(0, start)}${value}${content.slice(end)}`
  nextTick(() => {
    textarea.focus()
    const cursor = start + value.length
    textarea.setSelectionRange(cursor, cursor)
  })
}

const applyLink = () => {
  const textarea = getTextarea()
  if (!textarea) return
  const value = form.value.content_md
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selected = value.slice(start, end) || '链接文字'
  const replacement = `[${selected}](https://)`
  form.value.content_md = `${value.slice(0, start)}${replacement}${value.slice(end)}`
  nextTick(() => {
    textarea.focus()
    const urlStart = start + selected.length + 3
    textarea.setSelectionRange(urlStart, urlStart + 8)
  })
}

const handleUpload = async (options: UploadRequestOptions) => {
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    const { data } = await api.post<{ url: string }>('/api/v1/admin/upload', formData)
    insertBlock(`\n![${options.file.name}](${data.url})\n`)
    ElMessage.success('图片已插入')
  } catch (error) {
    ElMessage.error(errorMessage(error, '图片上传失败'))
  }
}

const handleCoverUpload = async (options: UploadRequestOptions) => {
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    const { data } = await api.post<{ url: string }>('/api/v1/admin/upload', formData)
    form.value.cover_image = data.url
    ElMessage.success('封面已上传')
  } catch (error) {
    ElMessage.error(errorMessage(error, '封面上传失败'))
  }
}

const confirmLeave = async () => {
  try {
    await ElMessageBox.confirm('当前内容尚未成功保存，确定离开吗？', '离开编辑器', {
      confirmButtonText: '离开',
      cancelButtonText: '继续编辑',
      type: 'warning',
    })
    return true
  } catch {
    return false
  }
}

const handleBeforeUnload = (event: BeforeUnloadEvent) => {
  if (!autosave.hasPendingWork.value) return
  event.preventDefault()
  event.returnValue = ''
}

const enhancePreview = () => {
  previewRoot.value?.querySelectorAll<HTMLElement>('[data-tex]').forEach((element) => {
    const tex = element.dataset.tex
    if (!tex) return
    katex.render(tex, element, {
      displayMode: element.dataset.display === 'true',
      throwOnError: false,
      output: 'htmlAndMathml',
    })
  })
}

onBeforeRouteLeave(async () => {
  if (allowRouteChange.value) return true
  if (!autosave.hasPendingWork.value) return true
  return confirmLeave()
})

onBeforeRouteUpdate(async (to) => {
  const nextId = to.params.id ? Number(to.params.id) : null
  if (nextId === postId.value) return true
  if (autosave.hasPendingWork.value && !(await confirmLeave())) return false
  loading.value = true
  ready.value = false
  loadError.value = ''
  try {
    if (nextId === null) resetPost()
    else await loadPost(nextId)
    ready.value = true
    return true
  } catch (error) {
    loadError.value = errorMessage(error, '文章加载失败，请稍后重试')
    return false
  } finally {
    loading.value = false
  }
})

onMounted(async () => {
  window.addEventListener('beforeunload', handleBeforeUnload)
  try {
    const [catRes, tagRes] = await Promise.all([categoriesApi.list(), tagsApi.list()])
    categoryOptions.value = catRes.data
    tagOptions.value = tagRes.data

    if (postId.value !== null) await loadPost(postId.value)
    else resetPost()
    ready.value = true
  } catch (error) {
    loadError.value = errorMessage(error, '文章加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
  await nextTick()
  enhancePreview()
})

watch(previewHtml, async () => {
  await nextTick()
  enhancePreview()
})

onBeforeUnmount(() => {
  disposed = true
  window.removeEventListener('beforeunload', handleBeforeUnload)
})
</script>

<template>
  <div class="max-w-7xl">
    <div class="mb-5 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-semibold text-rocom-text-strong">{{ isEdit ? '编辑文章' : '新建文章' }}</h1>
        <p class="mt-1 text-sm text-rocom-text-muted">{{ isPublished ? '已发布文章需点击保存更新' : `自动保存：${statusText}` }}</p>
      </div>
      <div class="flex items-center gap-2">
        <el-button v-if="autosave.status.value === 'error'" type="warning" plain @click="autosave.retry">重试保存</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存并返回</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </div>
    </div>

    <el-alert v-if="loadError" :title="loadError" type="error" show-icon :closable="false" class="mb-4" />
    <el-alert v-if="autosave.errorMessage.value" :title="autosave.errorMessage.value" type="warning" show-icon class="mb-4" />
    <el-skeleton v-if="loading" :rows="12" animated />

    <el-form v-else-if="!loadError" label-position="top">
      <el-form-item label="标题">
        <el-input v-model="form.title" placeholder="输入文章标题" />
      </el-form-item>
      <el-form-item label="Slug（可选）">
        <el-input v-model="form.slug" placeholder="留空则从标题自动生成" />
      </el-form-item>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
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
        <div class="flex w-full flex-wrap items-center gap-3">
          <el-upload :http-request="handleCoverUpload" :show-file-list="false" accept="image/*">
            <el-button size="small">上传封面</el-button>
          </el-upload>
          <el-input v-model="form.cover_image" placeholder="或输入图片 URL" class="min-w-[240px] flex-1" />
        </div>
        <img v-if="form.cover_image" :src="form.cover_image" class="mt-2 max-h-40 rounded-lg object-cover" alt="封面预览" />
      </el-form-item>

      <div class="mb-2 flex items-center justify-between gap-3">
        <span class="text-sm font-medium text-rocom-text-strong">正文 Markdown</span>
        <el-segmented v-model="activePane" :options="[{ label: '编辑', value: 'edit' }, { label: '预览', value: 'preview' }]" class="lg:hidden" />
      </div>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <section :class="[activePane === 'edit' ? '' : 'hidden lg:block']" class="min-w-0">
          <div class="mb-2 flex flex-wrap items-center gap-1 rounded-lg border border-rocom-outline bg-rocom-control p-1">
            <el-tooltip content="标题">
              <el-button text circle aria-label="插入标题" @click="prefixLines('## ')"><Heading2 :size="16" /></el-button>
            </el-tooltip>
            <el-tooltip content="粗体">
              <el-button text circle aria-label="粗体" @click="replaceSelection('**')"><Bold :size="16" /></el-button>
            </el-tooltip>
            <el-tooltip content="斜体">
              <el-button text circle aria-label="斜体" @click="replaceSelection('*')"><Italic :size="16" /></el-button>
            </el-tooltip>
            <el-tooltip content="删除线">
              <el-button text circle aria-label="删除线" @click="replaceSelection('~~')"><Strikethrough :size="16" /></el-button>
            </el-tooltip>
            <el-tooltip content="链接">
              <el-button text circle aria-label="插入链接" @click="applyLink"><Link :size="16" /></el-button>
            </el-tooltip>
            <el-tooltip content="引用">
              <el-button text circle aria-label="插入引用" @click="prefixLines('> ')"><Quote :size="16" /></el-button>
            </el-tooltip>
            <el-tooltip content="无序列表">
              <el-button text circle aria-label="无序列表" @click="prefixLines('- ')"><List :size="16" /></el-button>
            </el-tooltip>
            <el-tooltip content="有序列表">
              <el-button text circle aria-label="有序列表" @click="prefixLines('1. ')"><ListOrdered :size="16" /></el-button>
            </el-tooltip>
            <el-tooltip content="代码块">
              <el-button text circle aria-label="代码块" @click="replaceSelection('```\n', '\n```')"><Code2 :size="16" /></el-button>
            </el-tooltip>
            <el-tooltip content="分隔线">
              <el-button text circle aria-label="分隔线" @click="insertBlock('\n---\n')"><Minus :size="16" /></el-button>
            </el-tooltip>
            <el-upload :http-request="handleUpload" :show-file-list="false" accept="image/*">
              <el-tooltip content="上传图片">
                <el-button text circle aria-label="上传图片"><ImageIcon :size="16" /></el-button>
              </el-tooltip>
            </el-upload>
          </div>
          <el-input
            ref="contentEditor"
            v-model="form.content_md"
            type="textarea"
            :rows="28"
            resize="none"
            placeholder="使用 Markdown 编写正文..."
            input-style="font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; line-height: 1.65;"
          />
        </section>

        <section :class="[activePane === 'preview' ? '' : 'hidden lg:block']" class="min-w-0">
          <div ref="previewRoot" class="markdown-preview prose min-h-[590px] max-w-none overflow-auto rounded-lg border border-rocom-outline bg-rocom-surface-paper p-5" v-html="previewHtml" />
          <p v-if="!form.content_md.trim()" class="-mt-[575px] px-5 text-sm text-rocom-text-muted">暂无内容</p>
        </section>
      </div>

      <el-form-item class="mt-5">
        <el-checkbox v-model="form.is_top">置顶</el-checkbox>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.markdown-preview :deep(h1),
.markdown-preview :deep(h2),
.markdown-preview :deep(h3),
.markdown-preview :deep(h4) {
  color: var(--rocom-text-strong);
  font-weight: 700;
  margin: 1.25em 0 0.5em;
}

.markdown-preview :deep(p),
.markdown-preview :deep(ul),
.markdown-preview :deep(ol),
.markdown-preview :deep(blockquote),
.markdown-preview :deep(table) {
  color: var(--rocom-text);
  margin: 0.8em 0;
}

.markdown-preview :deep(a) { color: var(--rocom-accent-blue); text-decoration: underline; }
.markdown-preview :deep(pre) { overflow-x: auto; border-radius: 8px; padding: 1rem; background: var(--rocom-bg-paper); }
.markdown-preview :deep(code) { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.markdown-preview :deep(img) { max-width: 100%; border-radius: 8px; }
.markdown-preview :deep(blockquote) { border-left: 3px solid var(--rocom-primary); padding-left: 1rem; }
.markdown-preview :deep(table) { width: 100%; border-collapse: collapse; }
.markdown-preview :deep(th), .markdown-preview :deep(td) { border: 1px solid var(--rocom-outline); padding: 0.45rem 0.6rem; }
</style>
