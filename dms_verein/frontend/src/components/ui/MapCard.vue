<template>
  <div v-if="mapsKey && address" class="rounded-xl overflow-hidden border border-slate-200 shadow-sm flex flex-col">
    <iframe
      :src="`https://www.google.com/maps/embed/v1/place?key=${mapsKey}&q=${encodeURIComponent(address)}&language=de`"
      width="100%"
      :height="height"
      style="border: 0; display: block; flex: 1"
      allowfullscreen
      loading="lazy"
      referrerpolicy="no-referrer-when-downgrade"
    />
    <div class="flex items-center justify-between px-3 py-2 bg-slate-50 border-t border-slate-100 shrink-0">
      <span class="text-xs text-slate-500 truncate mr-2">{{ address }}</span>
      <a :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`"
        target="_blank" rel="noopener noreferrer"
        class="text-xs text-blue-600 hover:underline shrink-0 flex items-center gap-1">
        <ExternalLink :size="11" /> In Google Maps öffnen
      </a>
    </div>
  </div>
</template>

<script setup>
import { ExternalLink } from 'lucide-vue-next'
defineProps({
  address: { type: String, default: '' },
  mapsKey: { type: String, default: '' },
  height: { type: [Number, String], default: 220 },
})
</script>
