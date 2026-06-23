<script setup lang="ts">
const colorMode = useColorMode()
const toggle = () => {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<template>
  <button
    @click="toggle"
    class="w-9 h-9 rounded-full flex items-center justify-center bg-rocom-control hover:bg-rocom-control-hover transition-colors"
    :title="colorMode.value === 'dark' ? '切换亮色' : '切换暗色'"
  >
    <span v-if="colorMode.value === 'dark'" class="text-lg">☀️</span>
    <span v-else class="text-lg">🌙</span>
  </button>
</template>
