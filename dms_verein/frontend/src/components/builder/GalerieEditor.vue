<template>
  <div class="form-group">
    <label class="label">Galerie-Bilder</label>
    <div class="grid grid-cols-3 sm:grid-cols-4 gap-2 mb-3">
      <div v-for="(img, idx) in bilder" :key="idx"
        class="relative aspect-square rounded-lg overflow-hidden border border-slate-200 bg-slate-100">
        <img :src="img" class="w-full h-full object-cover" />
        <button @click="remove(idx)"
          class="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center
                 hover:bg-red-600 transition-colors shadow text-xs">
          <X :size="10" />
        </button>
      </div>
      <!-- Upload-Slot -->
      <label class="relative aspect-square rounded-lg border-2 border-dashed border-slate-300
                    flex flex-col items-center justify-center cursor-pointer
                    hover:border-primary-400 hover:bg-primary-50 transition-all">
        <Upload :size="20" class="text-slate-400" />
        <span class="text-xs text-slate-400 mt-1">Hinzufügen</span>
        <input type="file" multiple accept="image/*" class="hidden" @change="handleFiles" />
      </label>
    </div>
    <p class="text-xs text-slate-400">{{ bilder.length }} Bild(er) in der Galerie</p>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { X, Upload } from 'lucide-vue-next'
import { useApi } from '@/utils/api'

const props = defineProps({ modelValue: String })
const emit = defineEmits(['update:modelValue'])
const api = useApi()

const bilder = ref([])

watch(() => props.modelValue, (val) => {
  if (val) {
    try { bilder.value = JSON.parse(val) } catch { bilder.value = [] }
  } else {
    bilder.value = []
  }
}, { immediate: true })

function remove(idx) {
  bilder.value.splice(idx, 1)
  emit('update:modelValue', JSON.stringify(bilder.value))
}

async function handleFiles(e) {
  const files = Array.from(e.target.files || [])
  for (const file of files) {
    try {
      const url = await api.uploadFile(file)
      bilder.value.push(url)
    } catch (err) {
      console.error('Upload fehlgeschlagen:', err)
    }
  }
  emit('update:modelValue', JSON.stringify(bilder.value))
  e.target.value = ''
}
</script>
