import { computed, onBeforeUnmount, ref, watch, type Ref } from 'vue'

export type AutoSaveStatus = 'idle' | 'unsaved' | 'saving' | 'saved' | 'error'

interface AutosaveOptions<T> {
  value: Ref<T>
  enabled: Ref<boolean>
  ready: Ref<boolean>
  serialize: (value: T) => string
  save: (value: T) => Promise<void>
  delay?: number
}

export function usePostDraftAutosave<T>({
  value,
  enabled,
  ready,
  serialize,
  save,
  delay = 2000,
}: AutosaveOptions<T>) {
  const status = ref<AutoSaveStatus>('idle')
  const errorMessage = ref('')
  const savedSnapshot = ref('')
  const timer = ref<ReturnType<typeof setTimeout> | null>(null)
  let saveQueue = Promise.resolve()
  let editVersion = 0

  const dirty = computed(() => ready.value && serialize(value.value) !== savedSnapshot.value)
  const hasPendingWork = computed(() => dirty.value || status.value === 'saving' || status.value === 'error')

  const clearTimer = () => {
    if (timer.value) clearTimeout(timer.value)
    timer.value = null
  }

  const enqueueSave = () => {
    if (!enabled.value || !ready.value || !serialize(value.value).trim()) return
    const payload = structuredClone(value.value)
    const version = editVersion
    status.value = 'saving'
    errorMessage.value = ''
    saveQueue = saveQueue.then(async () => {
      if (version !== editVersion) return
      try {
        await save(payload)
        if (version === editVersion) {
          savedSnapshot.value = serialize(payload)
          status.value = 'saved'
        }
      } catch (error) {
        if (version === editVersion) {
          status.value = 'error'
          const detail = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail
          errorMessage.value = detail || (error instanceof Error ? error.message : '自动保存失败')
        }
      }
    })
  }

  const schedule = () => {
    if (!ready.value) return
    editVersion += 1
    status.value = dirty.value ? 'unsaved' : status.value
    clearTimer()
    if (!enabled.value || !dirty.value || !serialize(value.value).trim()) return
    timer.value = setTimeout(() => {
      timer.value = null
      enqueueSave()
    }, delay)
  }

  const retry = () => {
    clearTimer()
    enqueueSave()
  }

  const markSaved = (snapshot = serialize(value.value), nextStatus: AutoSaveStatus = 'saved') => {
    clearTimer()
    editVersion += 1
    savedSnapshot.value = snapshot
    status.value = nextStatus
    errorMessage.value = ''
  }

  const waitForQueue = () => saveQueue

  const invalidatePending = () => {
    clearTimer()
    editVersion += 1
  }

  watch(value, schedule, { deep: true })

  onBeforeUnmount(clearTimer)

  return {
    status,
    errorMessage,
    dirty,
    hasPendingWork,
    schedule,
    retry,
    markSaved,
    waitForQueue,
    invalidatePending,
    clearTimer,
  }
}
