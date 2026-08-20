<script setup lang="ts">
import { Send } from 'lucide-vue-next'

const props = defineProps<{ postSlug: string; parentId?: number; replyingTo?: string; needReview?: boolean }>()
const emit = defineEmits<{
  (e: 'submitted'): void
  (e: 'cancel-reply'): void
}>()
const api = useApi()

const form = reactive({
  nickname: '',
  email: '',
  website: '',
  content: '',
})
const submitting = ref(false)
const submitted = ref(false)
const error = ref('')

const submit = async () => {
  if (!form.nickname.trim() || !form.content.trim()) {
    error.value = '请填写昵称和评论内容'
    return
  }
  error.value = ''
  submitting.value = true
  try {
    await api.post('/comments', {
      post_slug: props.postSlug,
      parent_id: props.parentId,
      nickname: form.nickname,
      email: form.email || undefined,
      website: form.website || undefined,
      content: form.content,
    })
    submitted.value = true
    form.content = ''
    emit('submitted')
  } catch {
    error.value = '提交失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="bg-rocom-surface-paper rounded-xl border border-rocom-outline p-5">
    <h3 class="text-sm font-bold text-rocom-text-strong mb-4">发表评论</h3>

      <div v-if="submitted" class="text-sm text-rocom-success py-4 text-center" role="status">
      {{ props.needReview === false ? '评论已发布。' : '评论已提交，等待审核后显示。' }}
    </div>

    <form v-else @submit.prevent="submit" class="space-y-4">
      <div v-if="props.replyingTo" class="flex items-center justify-between rounded-md bg-rocom-control px-3 py-2 text-xs text-rocom-text-secondary">
        <span>正在回复：{{ props.replyingTo }}</span>
        <button type="button" class="text-rocom-primary-outline hover:underline" @click="emit('cancel-reply')">取消回复</button>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label for="comment-nickname" class="text-xs text-rocom-text-caption mb-1 block">昵称 *</label>
          <input id="comment-nickname" v-model="form.nickname" required class="input-field" />
        </div>
        <div>
          <label for="comment-email" class="text-xs text-rocom-text-caption mb-1 block">邮箱（可选）</label>
          <input id="comment-email" v-model="form.email" type="email" class="input-field" />
        </div>
        <div>
          <label for="comment-website" class="text-xs text-rocom-text-caption mb-1 block">网站（可选）</label>
          <input id="comment-website" v-model="form.website" class="input-field" />
        </div>
      </div>

      <div>
        <label for="comment-content" class="text-xs text-rocom-text-caption mb-1 block">评论内容 *</label>
        <textarea id="comment-content" v-model="form.content" required rows="4" class="input-field w-full" />
      </div>

      <div v-if="error" class="text-sm text-rocom-danger flex items-center gap-1" role="alert">
        {{ error }}
      </div>

      <button
        type="submit"
        :disabled="submitting"
        class="inline-flex items-center gap-2 px-5 py-2.5 rounded-pill bg-rocom-primary text-rocom-text-strong font-medium text-sm hover:bg-rocom-primary-strong disabled:opacity-50 transition-colors"
      >
        <Send v-if="!submitting" :size="14" />
        <span v-if="submitting" class="w-4 h-4 border-2 border-rocom-text-strong border-t-transparent rounded-full animate-spin" />
        {{ submitting ? '提交中...' : '提交评论' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.input-field {
  @apply px-3 py-2.5 text-sm rounded-lg bg-rocom-control border border-rocom-outline focus:outline-none focus:ring-2 focus:ring-rocom-primary text-rocom-text placeholder:text-rocom-text-disabled transition-shadow;
}
</style>
