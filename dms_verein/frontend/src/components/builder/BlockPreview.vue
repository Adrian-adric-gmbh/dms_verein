<template>
  <div class="text-xs text-slate-500 space-y-0.5">
    <template v-if="sektion.typ === 'Held-Banner'">
      <div v-if="sektion.bild" class="flex items-center gap-1.5">
        <ImageIcon :size="12" class="text-slate-400" />
        <span class="truncate max-w-xs">{{ sektion.bild }}</span>
      </div>
      <div v-if="sektion.titel" class="font-semibold text-slate-700 text-sm">{{ sektion.titel }}</div>
      <div v-if="sektion.untertitel" class="text-slate-400">{{ sektion.untertitel }}</div>
      <div v-if="sektion.cta_text" class="flex items-center gap-1">
        <span class="px-2 py-0.5 bg-primary-100 text-primary-700 rounded text-xs font-medium">{{ sektion.cta_text }}</span>
        <span v-if="sektion.cta_link" class="text-slate-400 truncate max-w-[150px]">→ {{ sektion.cta_link }}</span>
      </div>
    </template>

    <template v-else-if="sektion.typ === 'Text'">
      <div v-if="sektion.titel" class="font-semibold text-slate-700">{{ sektion.titel }}</div>
      <div v-if="sektion.text" class="line-clamp-2 text-slate-400"
        v-html="stripHtml(sektion.text).slice(0, 120) + '…'" />
      <div v-else class="text-slate-300 italic">Kein Text</div>
    </template>

    <template v-else-if="sektion.typ === 'Text & Bild'">
      <div class="flex items-center gap-3">
        <div class="flex-1">
          <div v-if="sektion.titel" class="font-semibold text-slate-700">{{ sektion.titel }}</div>
          <div v-if="sektion.text" class="line-clamp-1 text-slate-400" v-html="stripHtml(sektion.text).slice(0,80)+'…'" />
        </div>
        <div class="flex-none flex items-center gap-1 text-slate-400">
          <ImageIcon :size="12" />
          <span>{{ sektion.bild_ausrichtung || 'Rechts' }}</span>
        </div>
      </div>
    </template>

    <template v-else-if="sektion.typ === 'Bildergalerie'">
      <div class="flex items-center gap-1.5 text-slate-400">
        <ImageIcon :size="12" />
        <span>{{ galerieAnzahl }} Bilder</span>
      </div>
    </template>

    <template v-else-if="sektion.typ === 'Veranstaltungen'">
      <div class="flex items-center gap-1.5 text-blue-500">
        <Calendar :size="12" />
        <span>Nächste Events dieser Sparte werden automatisch angezeigt</span>
      </div>
    </template>

    <template v-else-if="sektion.typ === 'Kontaktkarte'">
      <div class="flex items-center gap-1.5 text-green-600">
        <User :size="12" />
        <span>Spartenleiter-Kontakt wird automatisch angezeigt</span>
      </div>
    </template>

    <template v-else-if="sektion.typ === 'Trenner'">
      <div class="flex items-center gap-2">
        <div class="flex-1 h-px bg-slate-200" />
        <span v-if="sektion.titel" class="text-slate-400">{{ sektion.titel }}</span>
        <div class="flex-1 h-px bg-slate-200" />
      </div>
    </template>

    <template v-else-if="sektion.typ === 'HTML-Block'">
      <div class="flex items-center gap-1.5 text-orange-500">
        <Code :size="12" />
        <span class="font-mono truncate max-w-xs">{{ sektion.html_inhalt?.slice(0, 80) || 'Kein HTML' }}</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Image as ImageIcon, Calendar, User, Code } from 'lucide-vue-next'

const props = defineProps({ sektion: Object })

const galerieAnzahl = computed(() => {
  if (!props.sektion?.galerie_bilder) return 0
  try { return JSON.parse(props.sektion.galerie_bilder).length } catch { return 0 }
})

function stripHtml(html) {
  return html?.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim() || ''
}
</script>
