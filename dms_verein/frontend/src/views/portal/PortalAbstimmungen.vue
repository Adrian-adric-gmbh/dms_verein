<template>
  <div>
    <div class="mb-6">
      <h2>Abstimmungen</h2>
      <p class="text-slate-500 mt-1">Aktive Umfragen und Abstimmungen des Vereins</p>
    </div>

    <AppSpinner v-if="loading" full-page />

    <div v-else class="space-y-4">
      <!-- Nicht stimmberechtigt Hinweis -->
      <AppAlert v-if="hatUnzugaengliche" type="info"
        message="Einige Abstimmungen sind nur für stimmberechtigte Mitglieder." />

      <div v-for="ab in abstimmungen" :key="ab.name" class="card overflow-hidden">
        <!-- Card-Header mit Farb-Akzent -->
        <div :class="[ab.status === 'Aktiv' ? 'bg-gradient-to-r from-blue-600 to-indigo-600' : 'bg-gradient-to-r from-slate-500 to-slate-600', 'px-5 py-3 flex items-center justify-between']">
          <div class="flex items-center gap-2">
            <span class="text-white font-semibold text-sm">{{ ab.titel }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="ab.anonym" class="text-xs text-white/70 flex items-center gap-1"><EyeOff :size="12" /> Anonym</span>
            <span :class="ab.status === 'Aktiv' ? 'bg-green-400 text-green-900' : 'bg-slate-300 text-slate-700'"
              class="text-xs font-bold px-2 py-0.5 rounded-full">{{ ab.status }}</span>
          </div>
        </div>

        <div class="card-body space-y-4">
          <div v-if="ab.beschreibung" class="text-sm text-slate-600">{{ ab.beschreibung }}</div>

          <!-- Meta -->
          <div class="flex flex-wrap gap-3 text-xs text-slate-500">
            <span class="flex items-center gap-1"><Calendar :size="12" /> {{ formatDate(ab.datum_von) }} – {{ formatDate(ab.datum_bis) }}</span>
            <span class="flex items-center gap-1"><Users :size="12" /> {{ ab.sparte_label }}</span>
            <span v-if="ab.bereits_abgestimmt" class="flex items-center gap-1 text-green-600 font-medium"><CheckCircle :size="12" /> Du hast abgestimmt</span>
          </div>

          <!-- === ABSTIMMEN === -->
          <div v-if="ab.status === 'Aktiv' && !ab.bereits_abgestimmt && !abstimmungFertig[ab.name]">
            <div v-for="(frage, fi) in ab.fragen" :key="fi" class="mb-5">
              <p class="font-semibold text-slate-800 mb-2 text-sm">
                <span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold mr-1.5">{{ fi+1 }}</span>
                {{ frage.frage }}
                <span class="text-xs text-slate-400 font-normal ml-2">({{ frage.typ }})</span>
              </p>
              <div class="space-y-2 ml-7">
                <label v-for="(opt, oi) in frage.optionen" :key="oi"
                  class="flex items-center gap-3 p-2.5 rounded-lg border cursor-pointer transition-colors"
                  :class="isGewaehlt(ab.name, fi, oi)
                    ? 'border-blue-400 bg-blue-50'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'">
                  <input
                    v-if="frage.typ === 'Einfachauswahl'"
                    type="radio" :name="`frage-${ab.name}-${fi}`"
                    @change="setStimme(ab.name, fi, oi, false)"
                    :checked="isGewaehlt(ab.name, fi, oi)"
                    class="accent-blue-600 w-4 h-4 shrink-0" />
                  <input
                    v-else
                    type="checkbox"
                    @change="setStimme(ab.name, fi, oi, true)"
                    :checked="isGewaehlt(ab.name, fi, oi)"
                    class="accent-blue-600 w-4 h-4 shrink-0" />
                  <span class="text-sm text-slate-700">{{ opt }}</span>
                </label>
              </div>
            </div>
            <AppAlert v-if="fehler[ab.name]" type="error" :message="fehler[ab.name]" class="mb-3" />
            <button @click="doAbstimmen(ab)"
              :disabled="loading_ab[ab.name] || !hatAlleBeantwortet(ab)"
              class="w-full btn btn-primary">
              {{ loading_ab[ab.name] ? 'Wird gespeichert…' : 'Abstimmen' }}
            </button>
            <p v-if="!hatAlleBeantwortet(ab)" class="text-xs text-slate-400 text-center mt-1">Bitte alle Fragen beantworten</p>
          </div>

          <!-- === ERFOLG nach Abstimmen === -->
          <Transition name="slide-up">
            <div v-if="abstimmungFertig[ab.name]" class="text-center py-4">
              <div class="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
                <CheckCircle :size="28" class="text-green-600" />
              </div>
              <p class="font-semibold text-slate-800">Deine Stimme wurde gezählt!</p>
              <p class="text-sm text-slate-500 mt-1">Vielen Dank für deine Teilnahme.</p>
            </div>
          </Transition>

          <!-- === ERGEBNIS === -->
          <div v-if="(ab.bereits_abgestimmt || abstimmungFertig[ab.name] || ab.status === 'Beendet') && ab.ergebnis?.length">
            <div class="border-t border-slate-100 pt-4">
              <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-4">
                {{ ab.status === 'Aktiv' ? 'Zwischenergebnis' : 'Endergebnis' }}
              </p>
              <div v-for="(frage, fi) in ergebnisAnzeige(ab)" :key="fi" class="mb-5">
                <p class="font-semibold text-sm text-slate-700 mb-3 flex items-center gap-2">
                  <span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold">{{ fi+1 }}</span>
                  {{ frage.frage }}
                </p>
                <ChartDonut v-if="frage.typ === 'Einfachauswahl'" :optionen="frage.optionen" :size="120" :stroke="22" />
                <ChartBars v-else :optionen="frage.optionen" />
                <p class="text-xs text-slate-400 mt-2 text-right">{{ frage.total || frage.optionen.reduce((s,o)=>s+(o.count||0),0) }} Stimme{{ frage.total !== 1 ? 'n' : '' }} abgegeben</p>
              </div>
            </div>
          </div>

          <!-- Noch nicht abgestimmt + beendet -->
          <div v-if="ab.status === 'Beendet' && !ab.bereits_abgestimmt && !abstimmungFertig[ab.name] && !ab.ergebnis?.length"
            class="text-center text-slate-400 py-4 text-sm">
            Du hast an dieser Abstimmung nicht teilgenommen.
          </div>
        </div>
      </div>

      <div v-if="!abstimmungen.length" class="card card-body text-center py-14 text-slate-400">
        <Vote :size="44" class="mx-auto mb-3 text-slate-300" />
        <p class="font-medium text-slate-600">Keine aktiven Abstimmungen</p>
        <p class="text-sm mt-1">Aktuell gibt es keine laufenden Umfragen für dich.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import ChartDonut from '@/components/ui/ChartDonut.vue'
import ChartBars from '@/components/ui/ChartBars.vue'
import { Calendar, Users, CheckCircle, EyeOff, Vote } from 'lucide-vue-next'
import { useRealtimeRefresh } from '@/composables/useRealtimeRefresh'

const abstimmungen = ref([])
const loading = ref(true)
const stimmen = ref({})        // { abstimmung_name: { frage_idx: [option_idxs] } }
const loading_ab = ref({})
const fehler = ref({})
const abstimmungFertig = ref({})  // after voting — trigger result show
const lokalErgebnis = ref({})     // ergebnis from server after voting

const hatUnzugaengliche = computed(() =>
  abstimmungen.value.some(a => a.nur_stimmberechtigt && !a.stimmberechtigt)
)

onMounted(() => ladeAbstimmungen())
useRealtimeRefresh(['Abstimmung'], () => ladeAbstimmungen())

async function ladeAbstimmungen() {
  try {
    abstimmungen.value = await api.call('dms_verein.api.verein.get_meine_abstimmungen') || []
  } finally { loading.value = false }
}

function isGewaehlt(abName, fi, oi) {
  return (stimmen.value[abName]?.[fi] || []).includes(oi)
}

function setStimme(abName, fi, oi, mehrfach) {
  if (!stimmen.value[abName]) stimmen.value[abName] = {}
  if (mehrfach) {
    const aktuell = stimmen.value[abName][fi] || []
    if (aktuell.includes(oi)) stimmen.value[abName][fi] = aktuell.filter(x => x !== oi)
    else stimmen.value[abName][fi] = [...aktuell, oi]
  } else {
    stimmen.value[abName][fi] = [oi]
  }
}

function hatAlleBeantwortet(ab) {
  const s = stimmen.value[ab.name] || {}
  return ab.fragen.every((_, fi) => (s[fi] || []).length > 0)
}

async function doAbstimmen(ab) {
  fehler.value[ab.name] = ''
  loading_ab.value[ab.name] = true
  try {
    const result = await api.call('dms_verein.api.verein.abstimmen', {
      abstimmung_name: ab.name,
      stimmen_json: JSON.stringify(stimmen.value[ab.name] || {}),
    })
    abstimmungFertig.value[ab.name] = true
    if (result?.ergebnis) {
      lokalErgebnis.value[ab.name] = result.ergebnis
      ab.ergebnis = result.ergebnis
    }
  } catch (e) {
    fehler.value[ab.name] = e.message
  } finally {
    loading_ab.value[ab.name] = false
  }
}

function ergebnisAnzeige(ab) {
  return lokalErgebnis.value[ab.name] || ab.ergebnis || []
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '—'
</script>

<style scoped>
.slide-up-enter-active { transition: all 0.4s ease-out; }
.slide-up-enter-from { opacity: 0; transform: translateY(12px); }
</style>
