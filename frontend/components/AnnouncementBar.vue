<script setup lang="ts">
import { Megaphone } from 'lucide-vue-next'

defineProps<{ content: string }>()
</script>

<template>
  <div v-if="content" class="bg-rocom-primary-soft border border-rocom-outline rounded-xl px-4 py-3 text-sm text-rocom-text-strong mb-6 flex items-start gap-2" role="alert">
    <Megaphone :size="16" class="text-rocom-primary mt-0.5 shrink-0" />
    <span>{{ content }}</span>
  </div>
</template>
