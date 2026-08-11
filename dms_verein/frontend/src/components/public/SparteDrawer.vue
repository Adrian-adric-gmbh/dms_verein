<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0">
      <div v-if="show" class="fixed inset-0 z-50 flex justify-end">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')" />

        <!-- Panel -->
        <Transition
          enter-active-class="transition-transform duration-300 ease-out"
          enter-from-class="translate-x-full"
          enter-to-class="translate-x-0"
          leave-active-class="transition-transform duration-250 ease-in"
          leave-from-class="translate-x-0"
          leave-to-class="translate-x-full">
          <div v-if="show"
            class="relative w-full sm:w-[620px] lg:w-[760px] xl:w-[900px] h-full bg-white overflow-y-auto shadow-2xl flex flex-col">

            <!-- Schließen -->
            <button @click="$emit('close')"
              class="absolute top-4 right-4 z-10 w-9 h-9 rounded-full bg-white/90 backdrop-blur shadow
                     flex items-center justify-center text-slate-600 hover:text-slate-900 hover:bg-white transition-all">
              <X :size="18" />
            </button>

            <div v-if="loading" class="flex-1 flex items-center justify-center">
              <div class="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
            </div>

            <template v-else-if="sparte">
              <!-- Kopfbereich -->
              <div class="relative min-h-[200px] flex items-end overflow-hidden shrink-0"
                :style="headerStyle">
                <div v-if="sparte.bild" class="absolute inset-0">
                  <img :src="sparte.bild" class="w-full h-full object-cover" />
                  <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                </div>
                <div class="relative z-10 p-6 w-full">
                  <div class="flex items-end gap-3">
                    <span v-if="sparte.icon" class="text-4xl leading-none drop-shadow">{{ sparte.icon }}</span>
                    <div>
                      <h2 class="text-2xl font-bold leading-tight" :class="sparte.bild ? 'text-white' : 'text-slate-900'">
                        {{ sparte.name_sparte }}
                      </h2>
                      <div v-if="sparte.treffpunkt" class="flex items-center gap-1.5 text-sm mt-1"
                        :class="sparte.bild ? 'text-white/80' : 'text-slate-500'">
                        <MapPin :size="13" />{{ sparte.treffpunkt }}
                      </div>
                    </div>
                    <div v-if="sparte.anzahl_mitglieder" class="ml-auto text-right">
                      <div class="text-lg font-bold" :class="sparte.bild ? 'text-white' : 'text-slate-800'">
                        {{ sparte.anzahl_mitglieder }}
                      </div>
                      <div class="text-xs" :class="sparte.bild ? 'text-white/70' : 'text-slate-400'">Mitglieder</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Beitraginfo-Banner (wenn gesetzt) -->
              <div v-if="sparte.beitrag"
                class="flex items-center gap-3 px-5 py-3 bg-primary-50 border-b border-primary-100">
                <Euro :size="16" class="text-primary-600 shrink-0" />
                <div class="text-sm">
                  <span class="font-semibold text-primary-800">
                    {{ formatBetrag(sparte.beitrag) }} {{ sparte.beitrag_intervall || 'Jährlich' }}
                  </span>
                  <span v-if="sparte.beitrag_bezeichnung" class="text-primary-600 ml-1.5">
                    — {{ sparte.beitrag_bezeichnung }}
                  </span>
                  <span v-else class="text-primary-600 ml-1.5">Spartenbeitrag (extra)</span>
                </div>
              </div>

              <!-- Kurzbeschreibung (wenn kein Held-Banner Block) -->
              <div v-if="sparte.beschreibung && !hasHeroBlock"
                class="px-5 py-4 border-b border-slate-100 text-sm text-slate-600 prose prose-sm max-w-none"
                v-html="sparte.beschreibung" />

              <!-- Seiten-Sektionen -->
              <div class="flex-1">
                <template v-for="(sektion, idx) in sparte.sektionen" :key="idx">

                  <!-- HELD-BANNER -->
                  <div v-if="sektion.typ === 'Held-Banner'"
                    class="relative min-h-[220px] flex items-center overflow-hidden"
                    :class="sectionBg(sektion)">
                    <div v-if="sektion.bild" class="absolute inset-0">
                      <img :src="sektion.bild" class="w-full h-full object-cover" />
                      <div class="absolute inset-0 bg-black/50" />
                    </div>
                    <div class="relative z-10 p-6 w-full text-white text-center">
                      <h3 v-if="sektion.titel" class="text-2xl font-bold mb-2">{{ sektion.titel }}</h3>
                      <p v-if="sektion.untertitel" class="opacity-90 mb-4">{{ sektion.untertitel }}</p>
                      <a v-if="sektion.cta_text && sektion.cta_link" :href="sektion.cta_link"
                        class="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-slate-900 font-semibold rounded-xl text-sm hover:bg-slate-100 transition-colors">
                        {{ sektion.cta_text }} <ArrowRight :size="14" />
                      </a>
                    </div>
                  </div>

                  <!-- TEXT -->
                  <div v-else-if="sektion.typ === 'Text'" class="px-5 py-6" :class="sectionBg(sektion)">
                    <h3 v-if="sektion.titel" class="text-lg font-bold mb-3"
                      :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">{{ sektion.titel }}</h3>
                    <div class="prose prose-sm max-w-none"
                      :class="sektion.hintergrund === 'Dunkel' ? 'prose-invert' : ''"
                      v-html="sektion.text" />
                  </div>

                  <!-- TEXT & BILD -->
                  <div v-else-if="sektion.typ === 'Text & Bild'" class="px-5 py-6" :class="sectionBg(sektion)">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-5 items-center">
                      <div :class="sektion.bild_ausrichtung === 'Links' ? 'sm:order-2' : 'sm:order-1'">
                        <h3 v-if="sektion.titel" class="text-lg font-bold mb-3"
                          :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">{{ sektion.titel }}</h3>
                        <div class="prose prose-sm max-w-none"
                          :class="sektion.hintergrund === 'Dunkel' ? 'prose-invert' : ''"
                          v-html="sektion.text" />
                      </div>
                      <div :class="sektion.bild_ausrichtung === 'Links' ? 'sm:order-1' : 'sm:order-2'">
                        <img v-if="sektion.bild" :src="sektion.bild"
                          class="w-full rounded-xl shadow object-cover aspect-video" />
                      </div>
                    </div>
                  </div>

                  <!-- BILDERGALERIE -->
                  <div v-else-if="sektion.typ === 'Bildergalerie'" class="px-5 py-6" :class="sectionBg(sektion)">
                    <h3 v-if="sektion.titel" class="text-lg font-bold mb-4"
                      :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">{{ sektion.titel }}</h3>
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      <div v-for="(img, i) in parsedGalerie(sektion)" :key="i"
                        class="aspect-square rounded-lg overflow-hidden cursor-pointer hover:opacity-90 transition-opacity"
                        @click="lightboxImg = img; lightboxOpen = true">
                        <img :src="img" class="w-full h-full object-cover" />
                      </div>
                    </div>
                  </div>

                  <!-- VERANSTALTUNGEN -->
                  <div v-else-if="sektion.typ === 'Veranstaltungen'" class="px-5 py-6" :class="sectionBg(sektion)">
                    <h3 class="text-lg font-bold mb-4"
                      :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">
                      {{ sektion.titel || 'Nächste Veranstaltungen' }}
                    </h3>
                    <div v-if="sparte.veranstaltungen?.length" class="space-y-2">
                      <div v-for="ev in sparte.veranstaltungen" :key="ev.name"
                        class="flex items-center gap-3 p-3 bg-white rounded-lg border border-slate-200 shadow-sm">
                        <div class="w-10 h-10 rounded-lg bg-primary-50 flex flex-col items-center justify-center shrink-0">
                          <span class="text-sm font-bold text-primary-700 leading-none">{{ new Date(ev.datum_von).getDate() }}</span>
                          <span class="text-xs text-primary-500">{{ new Date(ev.datum_von).toLocaleDateString('de-DE',{month:'short'}) }}</span>
                        </div>
                        <div class="flex-1 min-w-0">
                          <div class="font-medium text-sm truncate">{{ ev.titel }}</div>
                          <div v-if="ev.veranstaltungsort" class="text-xs text-slate-400">{{ ev.veranstaltungsort }}</div>
                        </div>
                      </div>
                    </div>
                    <p v-else class="text-sm text-slate-400">Keine Veranstaltungen geplant.</p>
                  </div>

                  <!-- KONTAKTKARTE -->
                  <div v-else-if="sektion.typ === 'Kontaktkarte'" class="px-5 py-6" :class="sectionBg(sektion)">
                    <h3 class="text-lg font-bold mb-4"
                      :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">
                      {{ sektion.titel || 'Ansprechpartner' }}
                    </h3>
                    <div v-if="sparte.spartenleiter"
                      class="flex items-center gap-4 p-4 bg-white rounded-xl border border-slate-200 shadow-sm">
                      <img v-if="sparte.spartenleiter.foto" :src="sparte.spartenleiter.foto"
                        class="w-14 h-14 rounded-full object-cover border-2 border-primary-200 shrink-0" />
                      <div v-else class="w-14 h-14 rounded-full bg-primary-100 flex items-center justify-center shrink-0">
                        <User :size="24" class="text-primary-600" />
                      </div>
                      <div>
                        <div class="font-semibold">{{ sparte.spartenleiter.vorname }} {{ sparte.spartenleiter.nachname }}</div>
                        <div class="text-sm text-slate-500 mb-1">Spartenleiter</div>
                        <a v-if="sparte.spartenleiter.email" :href="`mailto:${sparte.spartenleiter.email}`"
                          class="text-sm text-primary-600 hover:underline">{{ sparte.spartenleiter.email }}</a>
                      </div>
                    </div>
                  </div>

                  <!-- TRENNER -->
                  <div v-else-if="sektion.typ === 'Trenner'" class="px-5 py-4">
                    <div class="flex items-center gap-3">
                      <div class="flex-1 h-px bg-slate-200" />
                      <span v-if="sektion.titel" class="text-slate-400 text-sm">{{ sektion.titel }}</span>
                      <div class="flex-1 h-px bg-slate-200" />
                    </div>
                  </div>

                  <!-- HTML-BLOCK -->
                  <div v-else-if="sektion.typ === 'HTML-Block'" class="px-5 py-6" :class="sectionBg(sektion)"
                    v-html="sektion.html_inhalt" />

                </template>

                <!-- Footer-Info wenn keine Sektionen -->
                <div v-if="!sparte.sektionen?.length" class="px-5 py-6 space-y-4">
                  <div v-if="sparte.beschreibung" class="prose prose-sm max-w-none text-slate-600"
                    v-html="sparte.beschreibung" />
                  <div class="grid grid-cols-2 gap-4 text-sm text-slate-600 pt-2">
                    <div v-if="sparte.treffpunkt">
                      <div class="font-semibold text-slate-800 mb-1 flex items-center gap-1.5"><MapPin :size="13" /> Treffpunkt</div>
                      <p>{{ sparte.treffpunkt }}</p>
                    </div>
                    <div v-if="sparte.email">
                      <div class="font-semibold text-slate-800 mb-1 flex items-center gap-1.5"><Mail :size="13" /> Kontakt</div>
                      <a :href="`mailto:${sparte.email}`" class="text-primary-600 hover:underline">{{ sparte.email }}</a>
                    </div>
                    <div v-if="sparte.gruendungsjahr">
                      <div class="font-semibold text-slate-800 mb-1">Gegründet</div>
                      <p>{{ sparte.gruendungsjahr }}</p>
                    </div>
                    <div v-if="sparte.spartenleiter">
                      <div class="font-semibold text-slate-800 mb-1 flex items-center gap-1.5"><User :size="13" /> Leitung</div>
                      <p>{{ sparte.spartenleiter.vorname }} {{ sparte.spartenleiter.nachname }}</p>
                    </div>
                  </div>
                </div>

                <!-- Abstand am Ende -->
                <div class="h-10" />
              </div>
            </template>
          </div>
        </Transition>
      </div>
    </Transition>

    <!-- Lightbox -->
    <Transition enter-active-class="transition-opacity duration-150" enter-from-class="opacity-0" enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="lightboxOpen" class="fixed inset-0 z-[60] bg-black/95 flex items-center justify-center p-4"
        @click.self="lightboxOpen = false">
        <img :src="lightboxImg" class="max-w-full max-h-full rounded-xl object-contain" />
        <button @click="lightboxOpen = false"
          class="absolute top-4 right-4 text-white/70 hover:text-white bg-black/30 hover:bg-black/50 rounded-full p-2 transition-colors">
          <X :size="20" />
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useApi } from '@/utils/api'
import { X, MapPin, Mail, User, ArrowRight, Euro } from 'lucide-vue-next'

const props = defineProps({
  show: Boolean,
  sparteName: String,
})
defineEmits(['close'])

const api = useApi()
const sparte = ref(null)
const loading = ref(false)
const lightboxOpen = ref(false)
const lightboxImg = ref('')

const hasHeroBlock = computed(() =>
  sparte.value?.sektionen?.some(s => s.typ === 'Held-Banner')
)

const headerStyle = computed(() => {
  if (!sparte.value) return {}
  if (sparte.value.bild) return {}
  return { backgroundColor: sparte.value.farbe || 'var(--color-primary)' }
})

watch(() => props.sparteName, async (name) => {
  if (!name) return
  loading.value = true
  sparte.value = null
  try {
    sparte.value = await api.call('dms_verein.api.verein.get_sparte_detail', { name })
  } finally {
    loading.value = false
  }
}, { immediate: true })

function sectionBg(sektion) {
  const map = {
    'Hellgrau': 'bg-slate-50',
    'Primärfarbe': 'bg-primary-600 text-white',
    'Dunkel': 'bg-slate-900 text-white',
  }
  return map[sektion.hintergrund] || 'bg-white'
}

function parsedGalerie(sektion) {
  if (!sektion?.galerie_bilder) return []
  try { return JSON.parse(sektion.galerie_bilder) } catch { return [] }
}

function formatBetrag(val) {
  return Number(val).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
}
</script>
