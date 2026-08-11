<template>
  <div class="space-y-0">
    <section v-for="(s, idx) in sektionen" :key="idx"
      :class="bgClass(s.hintergrund)"
      class="w-full">

      <!-- TEXT -->
      <template v-if="s.typ === 'Text'">
        <div class="max-w-3xl mx-auto px-4 sm:px-6 py-10">
          <h2 v-if="s.titel" class="text-2xl font-bold text-slate-900 mb-4">{{ s.titel }}</h2>
          <div class="prose prose-lg max-w-none prose-headings:text-slate-900 prose-a:text-primary-600"
            v-html="s.text" />
        </div>
      </template>

      <!-- BILD -->
      <template v-else-if="s.typ === 'Bild'">
        <div class="max-w-3xl mx-auto px-4 sm:px-6 py-10">
          <figure :class="bildAusrichtungClass(s.bild_ausrichtung)">
            <img :src="s.bild" :alt="s.bildunterschrift || ''"
              class="rounded-xl shadow-sm max-w-full object-cover" />
            <figcaption v-if="s.bildunterschrift"
              class="mt-2 text-sm text-slate-500 text-center">{{ s.bildunterschrift }}</figcaption>
          </figure>
        </div>
      </template>

      <!-- TEXT & BILD -->
      <template v-else-if="s.typ === 'Text & Bild'">
        <div class="max-w-5xl mx-auto px-4 sm:px-6 py-10">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center"
            :class="s.bild_ausrichtung === 'Links' ? 'md:[&>*:first-child]:order-2' : ''">
            <div>
              <h2 v-if="s.titel" class="text-2xl font-bold text-slate-900 mb-4">{{ s.titel }}</h2>
              <div class="prose max-w-none prose-a:text-primary-600" v-html="s.text" />
            </div>
            <img v-if="s.bild" :src="s.bild" :alt="s.titel || ''"
              class="rounded-xl shadow-sm w-full object-cover" />
          </div>
        </div>
      </template>

      <!-- DIASHOW -->
      <template v-else-if="s.typ === 'Diashow'">
        <div class="py-10">
          <h2 v-if="s.titel" class="text-2xl font-bold text-slate-900 mb-6 text-center px-4">{{ s.titel }}</h2>
          <Diashow :bilder="parseBilder(s.bilder)" :autoplay="!!s.autoplay" />
        </div>
      </template>

      <!-- GALERIE -->
      <template v-else-if="s.typ === 'Galerie'">
        <div class="max-w-5xl mx-auto px-4 sm:px-6 py-10">
          <h2 v-if="s.titel" class="text-2xl font-bold text-slate-900 mb-6 text-center">{{ s.titel }}</h2>
          <div class="flex flex-wrap justify-center gap-3">
            <div v-for="(img, i) in parseBilder(s.bilder)" :key="i"
              class="aspect-square rounded-xl overflow-hidden cursor-pointer group flex-none
                     w-[calc(50%-6px)] sm:w-[calc(33.33%-8px)] lg:w-[calc(25%-9px)]"
              @click="lightboxIdx = i; lightboxBilder = parseBilder(s.bilder)">
              <img :src="img" :alt="'Bild ' + (i+1)"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
            </div>
          </div>
        </div>
      </template>

      <!-- VIDEO -->
      <template v-else-if="s.typ === 'Video'">
        <div class="max-w-3xl mx-auto px-4 sm:px-6 py-10">
          <h2 v-if="s.titel" class="text-2xl font-bold text-slate-900 mb-4">{{ s.titel }}</h2>
          <div class="aspect-video rounded-xl overflow-hidden shadow-sm bg-black">
            <iframe v-if="embedUrl(s.video_url)"
              :src="embedUrl(s.video_url)"
              class="w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen />
          </div>
        </div>
      </template>

      <!-- ZITAT -->
      <template v-else-if="s.typ === 'Zitat'">
        <div class="max-w-2xl mx-auto px-4 sm:px-6 py-10">
          <blockquote class="border-l-4 border-primary-400 pl-6 py-2">
            <p class="text-xl italic text-slate-700 leading-relaxed">{{ s.text }}</p>
            <footer v-if="s.zitat_autor" class="mt-3 text-sm text-slate-500 font-medium">
              — {{ s.zitat_autor }}
            </footer>
          </blockquote>
        </div>
      </template>

      <!-- INFO-BOX -->
      <template v-else-if="s.typ === 'Info-Box'">
        <div class="max-w-3xl mx-auto px-4 sm:px-6 py-6">
          <div :class="infoBoxClass(s.info_typ)" class="rounded-xl p-5 border">
            <div v-if="s.titel" class="font-bold mb-1 flex items-center gap-2">
              <span>{{ infoBoxIcon(s.info_typ) }}</span>
              {{ s.titel }}
            </div>
            <p class="text-sm leading-relaxed">{{ s.text }}</p>
          </div>
        </div>
      </template>

      <!-- TRENNER -->
      <template v-else-if="s.typ === 'Trenner'">
        <div class="max-w-3xl mx-auto px-4 sm:px-6 py-6">
          <div class="flex items-center gap-4">
            <div class="flex-1 h-px bg-slate-200" />
            <span v-if="s.titel" class="text-slate-400 text-sm">{{ s.titel }}</span>
            <div class="flex-1 h-px bg-slate-200" />
          </div>
        </div>
      </template>

      <!-- HTML-BLOCK -->
      <template v-else-if="s.typ === 'HTML-Block'">
        <div class="max-w-5xl mx-auto px-4 sm:px-6 py-8" v-html="s.html_inhalt" />
      </template>
    </section>

    <!-- Lightbox für Galerie -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="lightboxIdx !== null"
          class="fixed inset-0 z-[9999] bg-black/95 flex items-center justify-center touch-none"
          @click.self="lightboxIdx = null">
          <button @click="lightboxIdx = null"
            class="absolute top-4 right-4 text-white/70 hover:text-white p-2">✕</button>
          <button v-if="lightboxIdx > 0" @click="lightboxIdx--"
            class="absolute left-4 top-1/2 -translate-y-1/2 text-white/70 hover:text-white p-3 text-2xl">‹</button>
          <button v-if="lightboxIdx < lightboxBilder.length - 1" @click="lightboxIdx++"
            class="absolute right-4 top-1/2 -translate-y-1/2 text-white/70 hover:text-white p-3 text-2xl">›</button>
          <img v-if="lightboxBilder[lightboxIdx]"
            :src="lightboxBilder[lightboxIdx]"
            class="max-w-[92vw] max-h-[88dvh] object-contain pointer-events-none rounded-lg" />
          <div class="absolute bottom-4 text-white/50 text-sm">
            {{ lightboxIdx + 1 }} / {{ lightboxBilder.length }}
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Diashow from '@/components/blog/Diashow.vue'

defineProps({ sektionen: { type: Array, default: () => [] } })

const lightboxIdx = ref(null)
const lightboxBilder = ref([])

function parseBilder(json) {
  if (!json) return []
  try { return JSON.parse(json) } catch { return [] }
}

function bgClass(hg) {
  const map = {
    'Hellgrau': 'bg-slate-50',
    'Primärfarbe': 'bg-primary-50',
    'Dunkel': 'bg-slate-900 text-white [&_h2]:text-white [&_p]:text-slate-200 [&_.prose]:text-slate-200',
  }
  return map[hg] || 'bg-white'
}

function bildAusrichtungClass(ausrichtung) {
  if (ausrichtung === 'Links') return 'text-left'
  if (ausrichtung === 'Rechts') return 'text-right'
  return 'text-center'
}

function embedUrl(url) {
  if (!url) return null
  // YouTube
  const yt = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([A-Za-z0-9_-]+)/)
  if (yt) return `https://www.youtube-nocookie.com/embed/${yt[1]}`
  // Vimeo
  const vi = url.match(/vimeo\.com\/(\d+)/)
  if (vi) return `https://player.vimeo.com/video/${vi[1]}`
  return null
}

function infoBoxClass(typ) {
  const map = {
    'Info': 'bg-blue-50 border-blue-200 text-blue-900',
    'Erfolg': 'bg-green-50 border-green-200 text-green-900',
    'Warnung': 'bg-amber-50 border-amber-200 text-amber-900',
    'Hinweis': 'bg-violet-50 border-violet-200 text-violet-900',
  }
  return map[typ] || 'bg-blue-50 border-blue-200 text-blue-900'
}

function infoBoxIcon(typ) {
  return { 'Info': 'ℹ️', 'Erfolg': '✅', 'Warnung': '⚠️', 'Hinweis': '💡' }[typ] || 'ℹ️'
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
