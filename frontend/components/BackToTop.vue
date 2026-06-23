<script setup lang="ts">
const visible = ref(false)
const check = () => { visible.value = window.scrollY > 300 }
const goTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })

onMounted(() => window.addEventListener('scroll', check))
onUnmounted(() => window.removeEventListener('scroll', check))
</script>

<template>
  <Transition name="fade">
    <button
      v-if="visible"
      @click="goTop"
      class="fixed bottom-6 right-6 w-10 h-10 rounded-full bg-rocom-primary text-rocom-text-strong shadow-lg flex items-center justify-center hover:bg-rocom-primary-strong transition-colors z-50"
    >
      ↑
    </button>
  </Transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
