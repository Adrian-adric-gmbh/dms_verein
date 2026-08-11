<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white border-b border-slate-200 px-4 py-4 flex items-center gap-4">
      <RouterLink to="/" class="btn btn-secondary btn-sm"><ArrowLeft :size="14" /> Zurück</RouterLink>
      <h1 class="text-lg font-bold flex-1">Veranstaltungskalender</h1>
    </nav>

    <div class="max-w-6xl mx-auto p-4 lg:p-8">
      <div class="flex flex-wrap gap-3 mb-6">
        <select v-model="filterSparte" @change="load" class="input w-48">
          <option value="">Alle Sparten</option>
          <option v-for="s in sparten" :key="s.name" :value="s.name">{{ s.icon }} {{ s.name_sparte }}</option>
        </select>
      </div>

      <AppSpinner v-if="loading" full-page />

      <div v-else class="space-y-3">
        <div v-if="!events.length" class="card card-body text-center text-slate-400 py-12">
          Keine bevorstehenden Veranstaltungen
        </div>
        <div v-for="ev in events" :key="ev.name"
             class="card hover:shadow-md transition-all cursor-pointer active:scale-[0.99]"
             @click="selected = ev">
          <div class="card-body flex items-start gap-4">
            <!-- Datum -->
            <div class="w-14 shrink-0 text-center">
              <div class="text-2xl font-bold text-primary-600">{{ new Date(ev.datum_von).getDate() }}</div>
              <div class="text-xs text-slate-400 uppercase">{{ monthShort(ev.datum_von) }}</div>
              <div class="text-xs text-slate-400">{{ new Date(ev.datum_von).getFullYear() }}</div>
            </div>
            <!-- Inhalt -->
            <div class="flex-1 min-w-0">
              <h3 class="text-base font-semibold leading-snug mb-1">{{ ev.titel }}</h3>
              <span v-if="ev.kategorie" class="badge badge-blue text-xs mb-2">{{ ev.kategorie }}</span>
              <p class="text-sm text-slate-500 flex items-center gap-1 mt-1">
                <MapPin :size="14" class="shrink-0" />
                {{ ev.veranstaltungsort || 'Ort wird bekanntgegeben' }}
              </p>
              <p v-if="ev.uhrzeit_von" class="text-sm text-slate-500 flex items-center gap-1">
                <Clock :size="14" class="shrink-0" /> {{ ev.uhrzeit_von?.slice(0,5) }} Uhr
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Bottom Sheet: Event Detail ─── -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        leave-active-class="transition-all duration-200 ease-in">
        <div v-if="selected"
          class="fixed inset-0 z-40 flex flex-col justify-end lg:justify-center lg:items-center lg:p-6">
          <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="selected = null" />
          <Transition
            enter-active-class="transition-transform duration-300 ease-out"
            enter-from-class="translate-y-full lg:translate-y-0 lg:scale-95 lg:opacity-0"
            enter-to-class="translate-y-0 lg:scale-100 lg:opacity-100"
            leave-active-class="transition-transform duration-200 ease-in"
            leave-from-class="translate-y-0 lg:scale-100 lg:opacity-100"
            leave-to-class="translate-y-full lg:translate-y-0 lg:scale-95 lg:opacity-0"
            appear>
            <div v-if="selected"
              class="relative bg-white rounded-t-3xl lg:rounded-2xl w-full lg:max-w-xl
                     max-h-[92vh] lg:max-h-[85vh] flex flex-col shadow-2xl z-10">
              <!-- Handle -->
              <div class="lg:hidden flex justify-center pt-3 pb-1 shrink-0">
                <div class="w-10 h-1 rounded-full bg-slate-300" />
              </div>
              <!-- Header -->
              <div class="flex items-start gap-3 px-5 pt-3 pb-4 border-b border-slate-100 shrink-0">
                <div class="flex-1 min-w-0">
                  <span v-if="selected.kategorie" class="badge badge-blue text-xs mb-1">{{ selected.kategorie }}</span>
                  <h2 class="text-xl font-bold text-slate-900 leading-snug">{{ selected.titel }}</h2>
                </div>
                <button @click="selected = null"
                  class="shrink-0 w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center">
                  <X :size="16" class="text-slate-500" />
                </button>
              </div>
              <!-- Content -->
              <div class="flex-1 overflow-y-auto px-5 py-4 space-y-4">
                <img v-if="selected.bild" :src="selected.bild" class="w-full h-44 object-cover rounded-xl" />
                <div class="grid grid-cols-1 gap-2.5 text-sm">
                  <div class="flex items-center gap-2 text-slate-600">
                    <CalendarIcon :size="15" class="text-slate-400 shrink-0" />
                    <span>{{ formatDate(selected.datum_von) }}</span>
                  </div>
                  <div v-if="selected.uhrzeit_von" class="flex items-center gap-2 text-slate-600">
                    <Clock :size="15" class="text-slate-400 shrink-0" />
                    <span>{{ selected.uhrzeit_von?.slice(0,5) }} Uhr</span>
                  </div>
                  <div class="flex items-center gap-2 text-slate-600">
                    <MapPin :size="15" class="text-slate-400 shrink-0" />
                    <span>{{ selected.veranstaltungsort || 'Ort wird bekanntgegeben' }}</span>
                  </div>
                  <div v-if="selected.sparte" class="flex items-center gap-2 text-slate-600">
                    <Users :size="15" class="text-slate-400 shrink-0" />
                    <span>{{ selected.sparte }}</span>
                  </div>
                  <div v-if="selected.max_teilnehmer" class="flex items-center gap-2 text-slate-600">
                    <Users :size="15" class="text-slate-400 shrink-0" />
                    <span>Max. {{ selected.max_teilnehmer }} Teilnehmer</span>
                  </div>
                </div>
                <div v-if="selected.kosten_mitglieder || selected.kosten_gaeste"
                  class="flex flex-wrap gap-4 text-sm p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <div v-if="selected.kosten_mitglieder">
                    <span class="text-slate-500">Mitglieder: </span>
                    <span class="font-semibold">{{ formatCurrency(selected.kosten_mitglieder) }}</span>
                  </div>
                  <div v-if="selected.kosten_gaeste">
                    <span class="text-slate-500">Gäste: </span>
                    <span class="font-semibold">{{ formatCurrency(selected.kosten_gaeste) }}</span>
                  </div>
                </div>
                <div v-if="selected.beschreibung"
                  class="text-sm text-slate-700 border-t border-slate-100 pt-4 prose prose-sm max-w-none"
                  v-html="selected.beschreibung" />
              </div>
              <!-- Footer -->
              <div class="px-5 py-4 shrink-0" style="padding-bottom: max(1rem, env(safe-area-inset-bottom))">
                <button @click="selected = null" class="w-full btn btn-secondary">Schließen</button>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import { ArrowLeft, MapPin, Clock, X, Calendar as CalendarIcon, Users } from 'lucide-vue-next'

const events = ref([])
const sparten = ref([])
const loading = ref(true)
const selected = ref(null)
const filterSparte = ref('')

onMounted(async () => {
  const [, s] = await Promise.all([load(), api.getSparten()])
  sparten.value = s || []
})

async function load() {
  loading.value = true
  try {
    events.value = await api.getVeranstaltungen({ sparte: filterSparte.value, limit: 50 }) || []
  } finally { loading.value = false }
}

const monthShort = (d) => new Date(d).toLocaleDateString('de-DE', { month: 'short' })
const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }) : '—'
const formatCurrency = (v) => v ? `${Number(v).toFixed(2).replace('.', ',')} €` : 'kostenfrei'
</script>
