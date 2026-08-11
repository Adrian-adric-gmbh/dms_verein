<template>
  <div>
    <template v-for="(sektion, idx) in sektionen" :key="idx">
      <!-- HELD-BANNER -->
      <section v-if="sektion.typ === 'Held-Banner'"
        class="relative min-h-[40vh] flex items-center overflow-hidden"
        :style="sektion.hintergrund === 'Primärfarbe' ? { backgroundColor: 'var(--color-primary)' } : {}">
        <div v-if="sektion.bild" class="absolute inset-0">
          <img :src="sektion.bild" class="w-full h-full object-cover" />
          <div class="absolute inset-0 bg-black/50" />
        </div>
        <div class="relative z-10 max-w-4xl mx-auto px-6 text-white text-center w-full py-12">
          <h1 v-if="sektion.titel" class="text-3xl sm:text-5xl font-bold mb-4 leading-tight">{{ sektion.titel }}</h1>
          <p v-if="sektion.untertitel" class="text-xl opacity-90 mb-8">{{ sektion.untertitel }}</p>
          <a v-if="sektion.cta_text && sektion.cta_link" :href="sektion.cta_link"
            class="inline-flex items-center gap-2 px-6 py-3 bg-white text-slate-900 font-semibold rounded-xl hover:bg-slate-100 transition-colors shadow-lg">
            {{ sektion.cta_text }}
          </a>
        </div>
      </section>

      <!-- TEXT -->
      <section v-else-if="sektion.typ === 'Text'"
        class="py-10 sm:py-14" :class="sectionBgClass(sektion.hintergrund)">
        <div class="max-w-3xl mx-auto px-4 sm:px-6">
          <h2 v-if="sektion.titel" class="text-2xl sm:text-3xl font-bold mb-6"
            :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">{{ sektion.titel }}</h2>
          <div class="prose prose-lg max-w-none"
            :class="sektion.hintergrund === 'Dunkel' ? 'prose-invert' : ''"
            v-html="sektion.text" />
        </div>
      </section>

      <!-- TEXT & BILD -->
      <section v-else-if="sektion.typ === 'Text & Bild'"
        class="py-10 sm:py-14" :class="sectionBgClass(sektion.hintergrund)">
        <div class="max-w-5xl mx-auto px-4 sm:px-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div :class="sektion.bild_ausrichtung === 'Links' ? 'md:order-2' : 'md:order-1'">
              <h2 v-if="sektion.titel" class="text-2xl font-bold mb-4"
                :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">{{ sektion.titel }}</h2>
              <div class="prose prose-lg max-w-none"
                :class="sektion.hintergrund === 'Dunkel' ? 'prose-invert' : ''"
                v-html="sektion.text" />
            </div>
            <div :class="sektion.bild_ausrichtung === 'Links' ? 'md:order-1' : 'md:order-2'">
              <img v-if="sektion.bild" :src="sektion.bild" class="w-full rounded-2xl shadow-lg object-cover aspect-video" />
            </div>
          </div>
        </div>
      </section>

      <!-- BILDERGALERIE -->
      <section v-else-if="sektion.typ === 'Bildergalerie'"
        class="py-10 sm:py-14" :class="sectionBgClass(sektion.hintergrund)">
        <div class="max-w-6xl mx-auto px-4 sm:px-6">
          <h2 v-if="sektion.titel" class="text-2xl font-bold mb-6 text-center"
            :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">{{ sektion.titel }}</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            <div v-for="(img, i) in parsedBilder(sektion.galerie_bilder)" :key="i"
              class="aspect-square rounded-xl overflow-hidden cursor-pointer hover:opacity-90 transition-opacity"
              @click="lightboxImg = img; lightboxOpen = true">
              <img :src="img" class="w-full h-full object-cover" />
            </div>
          </div>
        </div>
      </section>

      <!-- VERANSTALTUNGEN -->
      <section v-else-if="sektion.typ === 'Veranstaltungen'"
        class="py-10 sm:py-14" :class="sectionBgClass(sektion.hintergrund)">
        <div class="max-w-5xl mx-auto px-4 sm:px-6">
          <h2 class="text-2xl font-bold mb-6"
            :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">
            {{ sektion.titel || 'Nächste Veranstaltungen' }}
          </h2>
          <div v-if="sparte?.veranstaltungen?.length" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="ev in sparte.veranstaltungen" :key="ev.name"
              class="rounded-xl border border-slate-200 bg-white p-4 hover:shadow-md transition-shadow">
              <div class="text-xs text-primary-600 font-medium mb-1">{{ formatDatum(ev.datum_von) }}</div>
              <div class="font-semibold text-slate-800">{{ ev.titel }}</div>
            </div>
          </div>
          <p v-else class="text-slate-400 text-sm">Aktuell keine Veranstaltungen geplant.</p>
        </div>
      </section>

      <!-- KONTAKTKARTE -->
      <section v-else-if="sektion.typ === 'Kontaktkarte'"
        class="py-10 sm:py-14" :class="sectionBgClass(sektion.hintergrund)">
        <div class="max-w-2xl mx-auto px-4 sm:px-6 text-center">
          <h2 class="text-2xl font-bold mb-6"
            :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">
            {{ sektion.titel || 'Ansprechpartner' }}
          </h2>
          <div v-if="sparte?.spartenleiter"
            class="inline-flex flex-col items-center bg-white rounded-2xl shadow-lg p-8 gap-3">
            <div class="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center overflow-hidden">
              <img v-if="sparte.spartenleiter.foto" :src="sparte.spartenleiter.foto" class="w-full h-full object-cover" />
              <span v-else class="text-xl text-primary-600">👤</span>
            </div>
            <div>
              <div class="font-bold text-slate-900">{{ sparte.spartenleiter.vorname }} {{ sparte.spartenleiter.nachname }}</div>
              <div class="text-sm text-slate-500 mb-2">Spartenleiter</div>
              <div v-if="sparte.spartenleiter.email" class="text-sm text-primary-700">{{ sparte.spartenleiter.email }}</div>
            </div>
          </div>
          <p v-else class="text-slate-400 text-sm">Kein Spartenleiter hinterlegt.</p>
        </div>
      </section>

      <!-- TRENNER -->
      <section v-else-if="sektion.typ === 'Trenner'" class="py-6">
        <div class="max-w-4xl mx-auto px-4 sm:px-6">
          <div class="flex items-center gap-4">
            <div class="flex-1 h-px bg-slate-200" />
            <span v-if="sektion.titel" class="text-slate-400 text-sm">{{ sektion.titel }}</span>
            <div class="flex-1 h-px bg-slate-200" />
          </div>
        </div>
      </section>

      <!-- HTML-BLOCK -->
      <section v-else-if="sektion.typ === 'HTML-Block'"
        class="py-8" :class="sectionBgClass(sektion.hintergrund)">
        <div class="max-w-5xl mx-auto px-4 sm:px-6" v-html="sektion.html_inhalt" />
      </section>
    </template>

    <!-- Galerie-Lightbox -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="lightboxOpen" class="fixed inset-0 z-[9999] bg-black/90 flex items-center justify-center p-4"
          @click.self="lightboxOpen = false">
          <img :src="lightboxImg" class="max-w-full max-h-full rounded-xl shadow-2xl object-contain" />
          <button @click="lightboxOpen = false"
            class="absolute top-4 right-4 text-white/70 hover:text-white bg-black/30 rounded-full p-2">✕</button>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  sektionen: { type: Array, default: () => [] },
  sparte: { type: Object, default: null },
})

const lightboxOpen = ref(false)
const lightboxImg = ref('')

function sectionBgClass(hg) {
  const map = {
    'Hellgrau': 'bg-slate-50',
    'Primärfarbe': 'bg-primary-600 text-white',
    'Dunkel': 'bg-slate-900 text-white',
  }
  return map[hg] || 'bg-white'
}

function parsedBilder(json) {
  if (!json) return []
  try { return JSON.parse(json) } catch { return [] }
}

function formatDatum(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: 'long', year: 'numeric' })
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
