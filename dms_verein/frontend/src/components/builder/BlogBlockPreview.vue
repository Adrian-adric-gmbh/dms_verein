<template>
  <div class="text-xs text-slate-500 space-y-0.5">
    <template v-if="sektion.typ === 'Text'">
      <div v-if="sektion.titel" class="font-semibold text-slate-700">{{ sektion.titel }}</div>
      <div v-if="sektion.text" class="line-clamp-2 text-slate-400"
        v-html="stripHtml(sektion.text).slice(0, 120) + '…'" />
      <div v-else class="text-slate-300 italic">Kein Text</div>
    </template>

    <template v-else-if="sektion.typ === 'Bild'">
      <div class="flex items-center gap-2">
        <ImageIcon :size="12" class="text-slate-400" />
        <span class="truncate max-w-xs">{{ sektion.bild || 'Kein Bild gewählt' }}</span>
        <span v-if="sektion.bildunterschrift" class="text-slate-400">— {{ sektion.bildunterschrift }}</span>
      </div>
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

    <template v-else-if="sektion.typ === 'Diashow'">
      <div class="flex items-center gap-1.5 text-violet-600">
        <PlayCircle :size="12" />
        <span>{{ bildAnzahl }} Bilder{{ sektion.autoplay ? ' · Autoplay' : '' }}</span>
        <span v-if="sektion.titel" class="text-slate-400">— {{ sektion.titel }}</span>
      </div>
    </template>

    <template v-else-if="sektion.typ === 'Galerie'">
      <div class="flex items-center gap-1.5 text-blue-500">
        <ImageIcon :size="12" />
        <span>{{ bildAnzahl }} Bilder</span>
        <span v-if="sektion.titel" class="text-slate-400">— {{ sektion.titel }}</span>
      </div>
    </template>

    <template v-else-if="sektion.typ === 'Video'">
      <div class="flex items-center gap-1.5 text-red-500">
        <Video :size="12" />
        <span class="truncate max-w-xs">{{ sektion.video_url || 'Keine URL' }}</span>
      </div>
    </template>

    <template v-else-if="sektion.typ === 'Zitat'">
      <div class="flex items-center gap-1.5 text-slate-600 italic">
        <Quote :size="12" />
        <span class="line-clamp-1">{{ stripHtml(sektion.text || '').slice(0,80) || 'Kein Text' }}</span>
        <span v-if="sektion.zitat_autor" class="not-italic text-slate-400">— {{ sektion.zitat_autor }}</span>
      </div>
    </template>

    <template v-else-if="sektion.typ === 'Info-Box'">
      <div class="flex items-center gap-1.5" :class="infoColor">
        <Info :size="12" />
        <span v-if="sektion.titel" class="font-semibold">{{ sektion.titel }}</span>
        <span class="text-xs">{{ sektion.info_typ || 'Info' }}</span>
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
      <div class="flex items-center gap-1.5 text-amber-600">
        <Code :size="12" />
        <span class="font-mono truncate max-w-xs">{{ sektion.html_inhalt?.slice(0, 80) || 'Kein HTML' }}</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Image as ImageIcon, PlayCircle, Video, Quote, Info, Code } from 'lucide-vue-next'

const props = defineProps({ sektion: Object })

const bildAnzahl = computed(() => {
  if (!props.sektion?.bilder) return 0
  try { return JSON.parse(props.sektion.bilder).length } catch { return 0 }
})

const infoColor = computed(() => ({
  'Info': 'text-blue-600',
  'Erfolg': 'text-green-600',
  'Warnung': 'text-amber-600',
  'Hinweis': 'text-violet-600',
}[props.sektion?.info_typ] || 'text-blue-600'))

function stripHtml(html) {
  return html?.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim() || ''
}
</script>
