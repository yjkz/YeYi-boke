<script setup lang="ts">
defineProps<{ content: string }>()
</script>

<template>
  <div v-if="content" class="bg-rocom-primary-soft border border-rocom-primary/20 rounded-xl px-4 py-3 text-sm text-rocom-text-strong mb-6">
    {{ content }}
  </div>
</template>
