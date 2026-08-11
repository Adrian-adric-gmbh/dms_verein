<template>
  <div class="form-group">
    <label class="label">{{ label }}</label>
    <div class="space-y-2">
      <div v-if="modelValue" class="relative inline-block">
        <img :src="modelValue" class="h-24 w-auto rounded-lg border border-slate-200 object-cover" />
        <button @click="clear"
          class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center
                 hover:bg-red-600 transition-colors shadow">
          <X :size="12" />
        </button>
      </div>
      <div>
        <label class="cursor-pointer">
          <span class="btn btn-sm inline-flex items-center gap-1.5">
            <Upload :size="14" /> Bild auswählen
          </span>
          <input type="file" class="hidden" accept="image/*" @change="handleFile" />
        </label>
        <span v-if="uploading" class="ml-2 text-sm text-slate-400">Wird hochgeladen…</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { X, Upload } from 'lucide-vue-next'
import { useApi } from '@/utils/api'

const props = defineProps({
  modelValue: String,
  label: { type: String, default: 'Bild' },
})
const emit = defineEmits(['update:modelValue'])
const api = useApi()
const uploading = ref(false)

async function handleFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const url = await api.uploadFile(file)
    emit('update:modelValue', url)
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

function clear() {
  emit('update:modelValue', '')
}
</script>
