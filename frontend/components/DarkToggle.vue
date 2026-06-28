<script setup lang="ts">
import { Sun, Moon } from 'lucide-vue-next'

const colorMode = useColorMode()
const toggle = () => {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<template>
  <button
    @click="toggle"
    class="w-11 h-11 rounded-full flex items-center justify-center bg-rocom-control hover:bg-rocom-control-hover transition-colors"
    :aria-label="colorMode.value === 'dark' ? '切换亮色模式' : '切换暗色模式'"
  >
    <Sun v-if="colorMode.value === 'dark'" :size="18" class="text-rocom-text-secondary" />
    <Moon v-else :size="18" class="text-rocom-text-secondary" />
  </button>
</template>
