<script setup lang="ts">
const props = defineProps<{ postSlug: string }>()
const emit = defineEmits<{ (e: 'submitted'): void }>()
const api = useApi()

const form = reactive({
  nickname: '',
  email: '',
  website: '',
  content: '',
})
const submitting = ref(false)
const submitted = ref(false)

const submit = async () => {
  if (!form.nickname.trim() || !form.content.trim()) return
  submitting.value = true
  try {
    await api.post('/api/v1/comments', {
      post_slug: props.postSlug,
      nickname: form.nickname,
      email: form.email || undefined,
      website: form.website || undefined,
      content: form.content,
    })
    submitted.value = true
    form.content = ''
    emit('submitted')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="bg-rocom-surface-paper rounded-xl border border-rocom-outline p-5">
    <h3 class="text-sm font-bold text-rocom-text-strong mb-4">发表评论</h3>
    <div v-if="submitted" class="text-sm text-rocom-success py-4 text-center">
      评论已提交，等待审核后显示。
    </div>
    <form v-else @submit.prevent="submit" class="space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <input v-model="form.nickname" placeholder="昵称 *" required class="input-field" />
        <input v-model="form.email" placeholder="邮箱（可选）" type="email" class="input-field" />
        <input v-model="form.website" placeholder="网站（可选）" class="input-field" />
      </div>
      <textarea v-model="form.content" placeholder="写下你的评论..." required rows="4" class="input-field w-full" />
      <button
        type="submit"
        :disabled="submitting"
        class="px-5 py-2 rounded-pill bg-rocom-primary text-rocom-text-strong font-medium text-sm hover:bg-rocom-primary-strong disabled:opacity-50 transition-colors"
      >
        {{ submitting ? '提交中...' : '提交评论' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.input-field {
  @apply px-3 py-2 text-sm rounded-lg bg-rocom-control border border-rocom-outline focus:outline-none focus:ring-2 focus:ring-rocom-primary text-rocom-text placeholder:text-rocom-text-disabled;
}
</style>
