<template>
  <div v-if="visible" :class="['flex items-start gap-3 p-4 rounded-lg text-sm', typeClass]">
    <component :is="icon" :size="18" class="shrink-0 mt-0.5" />
    <div class="flex-1">
      <p v-if="title" class="font-semibold mb-0.5">{{ title }}</p>
      <p>{{ message }}</p>
    </div>
    <button v-if="dismissible" @click="visible = false" class="shrink-0 opacity-60 hover:opacity-100">
      <X :size="16" />
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from 'lucide-vue-next'

const props = defineProps({
  type: { type: String, default: 'info' },
  title: String,
  message: String,
  dismissible: Boolean,
})

const visible = ref(true)

const typeClass = computed(() => ({
  success: 'bg-emerald-50 text-emerald-800 border border-emerald-200',
  error: 'bg-red-50 text-red-800 border border-red-200',
  warning: 'bg-amber-50 text-amber-800 border border-amber-200',
  info: 'bg-blue-50 text-blue-800 border border-blue-200',
}[props.type]))

const icon = computed(() => ({
  success: CheckCircle2, error: AlertCircle, warning: AlertTriangle, info: Info
}[props.type]))
</script>
