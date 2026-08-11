<template>
  <div :class="['flex items-center justify-center', fullPage ? 'h-64' : '']">
    <div :class="['animate-spin rounded-full border-2 border-slate-200 border-t-blue-600', sizeClass]" />
    <span v-if="label" class="ml-3 text-sm text-slate-500">{{ label }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  size: { type: String, default: 'md' },
  label: String,
  fullPage: Boolean,
})
const sizeClass = computed(() => ({ sm: 'h-4 w-4', md: 'h-8 w-8', lg: 'h-12 w-12' }[props.size]))
</script>
