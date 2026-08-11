<template>
  <div class="min-h-screen bg-white">
    <!-- Public-Navbar -->
    <PublicNav />

    <div v-if="loading" class="flex items-center justify-center py-24">
      <div class="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <template v-else-if="sparte">
      <!-- Standardheader wenn kein Held-Banner Block vorhanden -->
      <div v-if="!hasHeroBlock"
        class="py-12 sm:py-16 text-white"
        :style="{ backgroundColor: sparte.farbe || 'var(--color-primary)' }">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 text-center">
          <div v-if="sparte.icon" class="text-5xl mb-4">{{ sparte.icon }}</div>
          <h1 class="text-3xl sm:text-5xl font-bold mb-3">{{ sparte.name_sparte }}</h1>
          <p v-if="sparte.beschreibung" class="text-lg opacity-90 max-w-2xl mx-auto"
            v-html="sparte.beschreibung" />
          <div v-if="sparte.treffpunkt" class="mt-4 flex items-center justify-center gap-2 text-sm opacity-80">
            <MapPin :size="15" />{{ sparte.treffpunkt }}
          </div>
        </div>
      </div>

      <!-- Seiten-Sektionen -->
      <template v-for="(sektion, idx) in sparte.sektionen" :key="idx">
        <!-- HELD-BANNER -->
        <section v-if="sektion.typ === 'Held-Banner'"
          class="relative min-h-[50vh] sm:min-h-[65vh] flex items-center overflow-hidden"
          :style="sectionStyle(sektion)">
          <div v-if="sektion.bild" class="absolute inset-0">
            <img :src="sektion.bild" class="w-full h-full object-cover" />
            <div class="absolute inset-0 bg-black/50" />
          </div>
          <div class="relative z-10 max-w-4xl mx-auto px-6 text-white text-center w-full">
            <h1 v-if="sektion.titel" class="text-4xl sm:text-6xl font-bold mb-4 leading-tight">{{ sektion.titel }}</h1>
            <p v-if="sektion.untertitel" class="text-xl sm:text-2xl opacity-90 mb-8">{{ sektion.untertitel }}</p>
            <a v-if="sektion.cta_text && sektion.cta_link"
              :href="sektion.cta_link"
              class="inline-flex items-center gap-2 px-6 py-3 bg-white text-slate-900 font-semibold rounded-xl
                     hover:bg-slate-100 transition-colors shadow-lg">
              {{ sektion.cta_text }}
              <ArrowRight :size="18" />
            </a>
          </div>
        </section>

        <!-- TEXT -->
        <section v-else-if="sektion.typ === 'Text'"
          class="py-12 sm:py-16" :class="sectionBgClass(sektion.hintergrund)">
          <div class="max-w-3xl mx-auto px-4 sm:px-6">
            <h2 v-if="sektion.titel" class="text-2xl sm:text-3xl font-bold mb-6"
              :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">
              {{ sektion.titel }}
            </h2>
            <div class="prose prose-lg max-w-none"
              :class="sektion.hintergrund === 'Dunkel' ? 'prose-invert' : ''"
              v-html="sektion.text" />
          </div>
        </section>

        <!-- TEXT & BILD -->
        <section v-else-if="sektion.typ === 'Text & Bild'"
          class="py-12 sm:py-16" :class="sectionBgClass(sektion.hintergrund)">
          <div class="max-w-5xl mx-auto px-4 sm:px-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 sm:gap-12 items-center"
              :class="sektion.bild_ausrichtung === 'Links' ? 'md:flex-row-reverse' : ''">
              <div :class="sektion.bild_ausrichtung === 'Links' ? 'md:order-2' : 'md:order-1'">
                <h2 v-if="sektion.titel" class="text-2xl sm:text-3xl font-bold mb-4"
                  :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">
                  {{ sektion.titel }}
                </h2>
                <div class="prose prose-lg max-w-none"
                  :class="sektion.hintergrund === 'Dunkel' ? 'prose-invert' : ''"
                  v-html="sektion.text" />
              </div>
              <div :class="sektion.bild_ausrichtung === 'Links' ? 'md:order-1' : 'md:order-2'">
                <img v-if="sektion.bild" :src="sektion.bild"
                  class="w-full rounded-2xl shadow-lg object-cover aspect-video" />
              </div>
            </div>
          </div>
        </section>

        <!-- BILDERGALERIE -->
        <section v-else-if="sektion.typ === 'Bildergalerie'"
          class="py-12 sm:py-16" :class="sectionBgClass(sektion.hintergrund)">
          <div class="max-w-6xl mx-auto px-4 sm:px-6">
            <h2 v-if="sektion.titel" class="text-2xl sm:text-3xl font-bold mb-8 text-center"
              :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">
              {{ sektion.titel }}
            </h2>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              <div v-for="(img, i) in parsedGalerie(sektion)" :key="i"
                class="aspect-square rounded-xl overflow-hidden cursor-pointer hover:opacity-90 transition-opacity shadow"
                @click="lightboxImg = img; lightboxOpen = true">
                <img :src="img" class="w-full h-full object-cover" />
              </div>
            </div>
          </div>
        </section>

        <!-- VERANSTALTUNGEN -->
        <section v-else-if="sektion.typ === 'Veranstaltungen'"
          class="py-12 sm:py-16" :class="sectionBgClass(sektion.hintergrund)">
          <div class="max-w-5xl mx-auto px-4 sm:px-6">
            <h2 class="text-2xl sm:text-3xl font-bold mb-8"
              :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">
              {{ sektion.titel || 'Nächste Veranstaltungen' }}
            </h2>
            <div v-if="sparte.veranstaltungen?.length" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div v-for="ev in sparte.veranstaltungen" :key="ev.name"
                class="rounded-xl border border-slate-200 bg-white p-4 hover:shadow-md transition-shadow">
                <div class="text-xs text-primary-600 font-medium mb-1 flex items-center gap-1">
                  <Calendar :size="12" />{{ formatDatum(ev.datum_von) }}
                </div>
                <div class="font-semibold text-slate-800">{{ ev.titel }}</div>
                <div v-if="ev.veranstaltungsort" class="text-sm text-slate-400 mt-1 flex items-center gap-1">
                  <MapPin :size="12" />{{ ev.veranstaltungsort }}
                </div>
              </div>
            </div>
            <p v-else class="text-slate-400 text-sm">Aktuell keine Veranstaltungen geplant.</p>
          </div>
        </section>

        <!-- KONTAKTKARTE -->
        <section v-else-if="sektion.typ === 'Kontaktkarte'"
          class="py-12 sm:py-16" :class="sectionBgClass(sektion.hintergrund)">
          <div class="max-w-2xl mx-auto px-4 sm:px-6 text-center">
            <h2 class="text-2xl font-bold mb-8"
              :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">
              {{ sektion.titel || 'Ansprechpartner' }}
            </h2>
            <div v-if="sparte.spartenleiter"
              class="inline-flex flex-col items-center bg-white rounded-2xl shadow-lg p-8 gap-4">
              <img v-if="sparte.spartenleiter.foto" :src="sparte.spartenleiter.foto"
                class="w-20 h-20 rounded-full object-cover border-2 border-primary-200" />
              <div v-else class="w-20 h-20 rounded-full bg-primary-100 flex items-center justify-center">
                <User :size="32" class="text-primary-600" />
              </div>
              <div>
                <div class="text-lg font-bold text-slate-900">
                  {{ sparte.spartenleiter.vorname }} {{ sparte.spartenleiter.nachname }}
                </div>
                <div class="text-sm text-slate-500 mb-3">Spartenleiter</div>
                <div v-if="sparte.spartenleiter.email" class="flex items-center gap-2 text-sm text-primary-700">
                  <Mail :size="14" />
                  <a :href="`mailto:${sparte.spartenleiter.email}`">{{ sparte.spartenleiter.email }}</a>
                </div>
                <div v-if="sparte.spartenleiter.telefon" class="flex items-center gap-2 text-sm text-slate-600 mt-1">
                  <Phone :size="14" />{{ sparte.spartenleiter.telefon }}
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- TRENNER -->
        <section v-else-if="sektion.typ === 'Trenner'" class="py-6 sm:py-8">
          <div class="max-w-4xl mx-auto px-4 sm:px-6">
            <div class="flex items-center gap-4">
              <div class="flex-1 h-px bg-slate-200" />
              <span v-if="sektion.titel" class="text-slate-400 text-sm px-2">{{ sektion.titel }}</span>
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

      <!-- Footer-Infos -->
      <section class="bg-slate-50 border-t border-slate-200 py-12">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 grid sm:grid-cols-3 gap-6 text-sm text-slate-600">
          <div v-if="sparte.treffpunkt">
            <div class="font-semibold text-slate-800 mb-1 flex items-center gap-1.5">
              <MapPin :size="14" /> Treffpunkt
            </div>
            <p>{{ sparte.treffpunkt }}</p>
          </div>
          <div v-if="sparte.email || sparte.telefon">
            <div class="font-semibold text-slate-800 mb-1 flex items-center gap-1.5">
              <Mail :size="14" /> Kontakt
            </div>
            <p v-if="sparte.email"><a :href="`mailto:${sparte.email}`" class="text-primary-600 hover:underline">{{ sparte.email }}</a></p>
            <p v-if="sparte.telefon">{{ sparte.telefon }}</p>
          </div>
          <div v-if="sparte.gruendungsjahr">
            <div class="font-semibold text-slate-800 mb-1 flex items-center gap-1.5">
              <Users :size="14" /> Über uns
            </div>
            <p>Gegründet {{ sparte.gruendungsjahr }}</p>
            <p>{{ sparte.anzahl_mitglieder }} Mitglieder</p>
          </div>
        </div>
      </section>
    </template>

    <!-- Nicht gefunden -->
    <div v-else class="max-w-xl mx-auto px-4 py-20 text-center">
      <div class="text-5xl mb-4">🔍</div>
      <h2 class="text-2xl font-bold text-slate-800 mb-2">Sparte nicht gefunden</h2>
      <p class="text-slate-500 mb-6">Diese Sparte existiert nicht oder ist nicht öffentlich.</p>
      <RouterLink to="/" class="btn btn-primary">Zur Startseite</RouterLink>
    </div>

    <!-- Lightbox -->
    <Teleport to="body">
      <Transition enter-active-class="transition-opacity duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150" leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="lightboxOpen" class="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          @click.self="lightboxOpen = false">
          <img :src="lightboxImg" class="max-w-full max-h-full rounded-xl shadow-2xl object-contain" />
          <button @click="lightboxOpen = false"
            class="absolute top-4 right-4 text-white/70 hover:text-white bg-black/30 hover:bg-black/50 rounded-full p-2 transition-colors">
            <X :size="24" />
          </button>
        </div>
      </Transition>
    </Teleport>

    <PublicFooter />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useApi } from '@/utils/api'
import { useVereinStore } from '@/stores/verein'
import { MapPin, Mail, Phone, User, Calendar, Users, ArrowRight, X } from 'lucide-vue-next'
import PublicNav from '@/components/public/PublicNav.vue'
import PublicFooter from '@/components/public/PublicFooter.vue'

const route = useRoute()
const api = useApi()
const verein = useVereinStore()

const sparte = ref(null)
const loading = ref(true)
const lightboxOpen = ref(false)
const lightboxImg = ref('')

const hasHeroBlock = computed(() =>
  sparte.value?.sektionen?.some(s => s.typ === 'Held-Banner')
)

async function load() {
  loading.value = true
  try {
    sparte.value = await api.call('dms_verein.api.verein.get_sparte_detail', {
      name: route.params.name,
    })
  } catch {
    sparte.value = null
  } finally {
    loading.value = false
  }
}

function parsedGalerie(sektion) {
  if (!sektion?.galerie_bilder) return []
  try { return JSON.parse(sektion.galerie_bilder) } catch { return [] }
}

function sectionBgClass(hg) {
  const map = {
    'Hellgrau': 'bg-slate-50',
    'Primärfarbe': 'bg-primary-600 text-white',
    'Dunkel': 'bg-slate-900 text-white',
  }
  return map[hg] || 'bg-white'
}

function sectionStyle(sektion) {
  return sektion.hintergrund === 'Primärfarbe'
    ? { backgroundColor: 'var(--color-primary)' }
    : {}
}

function formatDatum(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: 'long', year: 'numeric' })
}

onMounted(load)
</script>
