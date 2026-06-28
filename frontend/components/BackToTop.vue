<script setup lang="ts">
import { ArrowUp } from 'lucide-vue-next'

const visible = ref(false)
const check = () => { visible.value = window.scrollY > 300 }
const goTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })

onMounted(() => window.addEventListener('scroll', check, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', check))
</script>

<template>
  <Transition name="fade">
    <button
      v-if="visible"
      @click="goTop"
      class="fixed bottom-6 right-6 w-11 h-11 rounded-full bg-rocom-primary text-rocom-text-strong shadow-lg flex items-center justify-center hover:bg-rocom-primary-strong transition-colors z-50"
      aria-label="回到顶部"
    >
      <ArrowUp :size="18" />
    </button>
  </Transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease-out; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
