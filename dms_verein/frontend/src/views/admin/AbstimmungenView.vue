<template>
  <div>
    <!-- Header -->
    <div class="flex flex-wrap items-start justify-between gap-3 mb-6">
      <div>
        <h2>Abstimmungen</h2>
        <p class="text-slate-500 mt-1">Umfragen und Mitgliederabstimmungen verwalten</p>
      </div>
      <button @click="openNeu" class="btn btn-primary"><Plus :size="16" /> Neue Abstimmung</button>
    </div>

    <AppSpinner v-if="loading" full-page />

    <div v-else>
      <!-- Statistik-Kacheln -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <div class="card text-center p-4">
          <p class="text-2xl font-bold text-blue-600">{{ stats.gesamt }}</p>
          <p class="text-xs text-slate-500 mt-1">Gesamt</p>
        </div>
        <div class="card text-center p-4">
          <p class="text-2xl font-bold text-green-600">{{ stats.aktiv }}</p>
          <p class="text-xs text-slate-500 mt-1">Aktiv</p>
        </div>
        <div class="card text-center p-4">
          <p class="text-2xl font-bold text-slate-600">{{ stats.beendet }}</p>
          <p class="text-xs text-slate-500 mt-1">Beendet</p>
        </div>
        <div class="card text-center p-4">
          <p class="text-2xl font-bold text-amber-600">{{ stats.entwurf }}</p>
          <p class="text-xs text-slate-500 mt-1">Entwurf</p>
        </div>
      </div>

      <!-- Liste -->
      <div class="space-y-3">
        <div v-for="ab in abstimmungen" :key="ab.name"
          class="card hover:shadow-md transition-shadow cursor-pointer"
          @click="openErgebnis(ab)">
          <div class="card-body">
            <div class="flex items-start justify-between gap-3">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <span :class="statusClass(ab.status)" class="badge text-xs font-medium">{{ ab.status }}</span>
                  <span v-if="ab.anonym" class="badge badge-slate text-xs">Anonym</span>
                  <span class="text-xs text-slate-400">{{ ab.sparte_label }}</span>
                </div>
                <h3 class="font-semibold text-slate-900 mt-1 text-base">{{ ab.titel }}</h3>
                <p v-if="ab.beschreibung" class="text-sm text-slate-500 mt-0.5 line-clamp-1">{{ ab.beschreibung }}</p>
                <div class="flex flex-wrap items-center gap-4 mt-2 text-xs text-slate-500">
                  <span class="flex items-center gap-1"><Calendar :size="12" /> {{ formatDate(ab.datum_von) }} – {{ formatDate(ab.datum_bis) }}</span>
                  <span class="flex items-center gap-1"><Users :size="12" /> {{ ab.teilnehmer }} Stimmen</span>
                  <span class="flex items-center gap-1"><MessageSquare :size="12" /> {{ ab.fragen.length }} Frage{{ ab.fragen.length !== 1 ? 'n' : '' }}</span>
                </div>
                <!-- Beteiligung-Bar -->
                <div v-if="ab.status !== 'Entwurf'" class="mt-2">
                  <div class="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div class="h-full bg-blue-500 rounded-full transition-all duration-700"
                      :style="`width:${ab.beteiligung_pct}%`" />
                  </div>
                </div>
              </div>
              <div class="flex gap-2 shrink-0">
                <button @click.stop="openBearbeiten(ab)" class="btn btn-secondary text-xs py-1 px-2"><Pencil :size="13" /></button>
                <button @click.stop="confirmDelete(ab)" class="btn btn-secondary text-xs py-1 px-2 text-red-500 hover:bg-red-50"><Trash2 :size="13" /></button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="!abstimmungen.length" class="card card-body text-center text-slate-400 py-12">
          <Vote :size="40" class="mx-auto mb-3 text-slate-300" />
          <p class="font-medium">Noch keine Abstimmungen</p>
          <p class="text-sm mt-1">Erstelle deine erste Abstimmung.</p>
        </div>
      </div>
    </div>

    <!-- Erstellen/Bearbeiten Modal -->
    <AppModal :show="showForm" :title="editTarget ? 'Abstimmung bearbeiten' : 'Neue Abstimmung'" size="xl" @close="showForm = false">
      <div class="space-y-5">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="sm:col-span-2 form-group">
            <label class="label">Titel *</label>
            <input v-model="form.titel" class="input" placeholder="z.B. Jahreshauptversammlung Datum" />
          </div>
          <div class="sm:col-span-2 form-group">
            <label class="label">Beschreibung</label>
            <textarea v-model="form.beschreibung" class="input" rows="2" placeholder="Kurze Beschreibung..." />
          </div>
          <div class="form-group">
            <label class="label">Von *</label>
            <input v-model="form.datum_von" type="date" class="input" />
          </div>
          <div class="form-group">
            <label class="label">Bis *</label>
            <input v-model="form.datum_bis" type="date" class="input" />
          </div>
          <div class="form-group">
            <label class="label">{{ verein.strukturSingular }} (leer = alle)</label>
            <select v-model="form.sparte" class="input">
              <option value="">Alle Mitglieder</option>
              <option v-for="s in sparten" :key="s.name" :value="s.name">{{ s.name_sparte }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="label">Status</label>
            <select v-model="form.status" class="input">
              <option>Entwurf</option>
              <option>Aktiv</option>
              <option>Beendet</option>
            </select>
          </div>
          <div class="flex items-center gap-3">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.nur_stimmberechtigt" type="checkbox" class="w-4 h-4" />
              <span class="text-sm text-slate-700">Nur Stimmberechtigte</span>
            </label>
          </div>
          <div class="flex items-center gap-3">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.anonym" type="checkbox" class="w-4 h-4" />
              <span class="text-sm text-slate-700">Anonyme Abstimmung</span>
            </label>
          </div>
        </div>

        <!-- Fragen -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h4 class="font-semibold text-slate-800">Fragen</h4>
            <button @click="addFrage" class="btn btn-secondary text-sm py-1"><Plus :size="14" /> Frage hinzufügen</button>
          </div>
          <div class="space-y-4">
            <div v-for="(frage, fi) in form.fragen" :key="fi"
              class="border border-slate-200 rounded-xl p-4 bg-slate-50">
              <div class="flex items-start gap-3 mb-3">
                <div class="flex-1 space-y-2">
                  <input v-model="frage.frage" class="input text-sm" :placeholder="`Frage ${fi+1}`" />
                  <select v-model="frage.typ" class="input text-sm">
                    <option>Einfachauswahl</option>
                    <option>Mehrfachauswahl</option>
                  </select>
                </div>
                <button @click="removeFrage(fi)" class="text-red-400 hover:text-red-600 mt-1"><Trash2 :size="16" /></button>
              </div>
              <!-- Optionen -->
              <div class="space-y-2 ml-2">
                <div v-for="(opt, oi) in frage.optionen" :key="oi" class="flex items-center gap-2">
                  <span class="w-5 h-5 rounded-full bg-blue-100 text-blue-700 text-xs flex items-center justify-center font-bold shrink-0">{{ oi+1 }}</span>
                  <input v-model="frage.optionen[oi]" class="input text-sm flex-1" :placeholder="`Option ${oi+1}`" />
                  <button @click="removeOption(fi, oi)" class="text-slate-300 hover:text-red-400"><X :size="14" /></button>
                </div>
                <button @click="addOption(fi)" class="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1 ml-7">
                  <Plus :size="12" /> Option hinzufügen
                </button>
              </div>
            </div>
            <div v-if="!form.fragen.length" class="text-center text-slate-400 text-sm py-4 border border-dashed border-slate-200 rounded-xl">
              Noch keine Fragen — klicke auf "Frage hinzufügen"
            </div>
          </div>
        </div>

        <AppAlert v-if="formError" type="error" :message="formError" />
      </div>
      <template #footer>
        <button @click="showForm = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="saveAbstimmung" :disabled="saving" class="btn btn-primary">
          <Save :size="15" /> {{ saving ? 'Speichern…' : 'Speichern' }}
        </button>
      </template>
    </AppModal>

    <!-- Ergebnis Modal -->
    <AppModal :show="showErgebnis" :title="ergebnisData?.titel || 'Ergebnisse'" size="xl" @close="showErgebnis = false">
      <div v-if="ergebnisLoading" class="py-12 text-center"><AppSpinner /></div>
      <div v-else-if="ergebnisData" class="space-y-6">
        <!-- Kopf-Stats -->
        <div class="grid grid-cols-3 gap-3">
          <div class="bg-blue-50 rounded-xl p-3 text-center">
            <p class="text-2xl font-bold text-blue-700">{{ ergebnisData.total }}</p>
            <p class="text-xs text-blue-600 mt-0.5">Stimmen</p>
          </div>
          <div class="bg-green-50 rounded-xl p-3 text-center">
            <p class="text-2xl font-bold text-green-700">{{ ergebnisData.wahlberechtigt }}</p>
            <p class="text-xs text-green-600 mt-0.5">Wahlberechtigt</p>
          </div>
          <div class="bg-purple-50 rounded-xl p-3 text-center">
            <p class="text-2xl font-bold text-purple-700">{{ ergebnisData.beteiligung }}%</p>
            <p class="text-xs text-purple-600 mt-0.5">Beteiligung</p>
          </div>
        </div>
        <!-- Beteiligung-Bar -->
        <div>
          <div class="flex justify-between text-xs text-slate-500 mb-1">
            <span>Wahlbeteiligung</span>
            <span>{{ ergebnisData.beteiligung }}%</span>
          </div>
          <div class="h-3 bg-slate-100 rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-1000"
              :style="`width:${ergebnisData.beteiligung}%`" />
          </div>
        </div>

        <!-- Fragen-Ergebnisse -->
        <div v-for="(frage, fi) in ergebnisData.ergebnis" :key="fi" class="bg-slate-50 rounded-xl p-4">
          <div class="flex items-center gap-2 mb-4">
            <span class="w-6 h-6 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold shrink-0">{{ fi+1 }}</span>
            <h4 class="font-semibold text-slate-800">{{ frage.frage }}</h4>
            <span class="badge badge-slate text-xs ml-auto">{{ frage.typ }}</span>
          </div>
          <ChartDonut v-if="frage.typ === 'Einfachauswahl'" :optionen="frage.optionen" />
          <ChartBars v-else :optionen="frage.optionen" />
        </div>

        <!-- Teilnehmerliste (nicht-anonym) -->
        <div v-if="!ergebnisData.anonym && ergebnisData.teilnehmer?.length">
          <h4 class="font-semibold text-slate-700 mb-2">Teilnehmer</h4>
          <div class="flex flex-wrap gap-2">
            <span v-for="t in ergebnisData.teilnehmer" :key="t.mitglied"
              class="badge badge-slate text-xs">{{ t.name }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <button @click="openBearbeiten(ergebnisRaw)" class="btn btn-secondary"><Pencil :size="14" /> Bearbeiten</button>
        <button @click="showErgebnis = false" class="btn btn-primary">Schließen</button>
      </template>
    </AppModal>

    <!-- Löschen Confirm -->
    <AppModal :show="showDelete" title="Abstimmung löschen" size="sm" @close="showDelete = false">
      <p class="text-slate-600">Abstimmung <strong>{{ deleteTarget?.titel }}</strong> und alle abgegebenen Stimmen unwiderruflich löschen?</p>
      <template #footer>
        <button @click="showDelete = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="doDelete" :disabled="deleting" class="btn btn-danger">
          {{ deleting ? 'Löschen…' : 'Ja, löschen' }}
        </button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'
import { useVereinStore } from '@/stores/verein'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import ChartDonut from '@/components/ui/ChartDonut.vue'
import ChartBars from '@/components/ui/ChartBars.vue'
import { Plus, Pencil, Trash2, Save, X, Calendar, Users, MessageSquare, Vote } from 'lucide-vue-next'
import { useRealtimeRefresh } from '@/composables/useRealtimeRefresh'

const abstimmungen = ref([])
const loading = ref(true)
const sparten = ref([])
const verein = useVereinStore()
const showForm = ref(false)
const showErgebnis = ref(false)
const showDelete = ref(false)
const editTarget = ref(null)
const ergebnisData = ref(null)
const ergebnisRaw = ref(null)
const ergebnisLoading = ref(false)
const deleteTarget = ref(null)
const saving = ref(false)
const deleting = ref(false)
const formError = ref('')

const blankForm = () => ({
  titel: '', beschreibung: '', datum_von: '', datum_bis: '',
  sparte: '', status: 'Entwurf', nur_stimmberechtigt: true, anonym: true,
  fragen: [],
})
const form = ref(blankForm())

const stats = computed(() => ({
  gesamt: abstimmungen.value.length,
  aktiv: abstimmungen.value.filter(a => a.status === 'Aktiv').length,
  beendet: abstimmungen.value.filter(a => a.status === 'Beendet').length,
  entwurf: abstimmungen.value.filter(a => a.status === 'Entwurf').length,
}))

function statusClass(s) {
  return s === 'Aktiv' ? 'badge-green' : s === 'Beendet' ? 'badge-slate' : 'badge badge-amber'
}
const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '—'

onMounted(() => load())
useRealtimeRefresh(['Abstimmung'], () => load())

async function load() {
  loading.value = true
  try {
    const [abs, spt] = await Promise.all([
      api.call('dms_verein.api.verein.get_abstimmungen_admin'),
      api.call('dms_verein.api.verein.get_sparten'),
    ])
    abstimmungen.value = (abs || []).map(a => ({
      ...a,
      beteiligung_pct: a.teilnehmer > 0 ? Math.min(100, Math.round(a.teilnehmer / 1 * 5)) : 0,
    }))
    sparten.value = spt || []
  } finally { loading.value = false }
}

function openNeu() {
  editTarget.value = null
  form.value = blankForm()
  formError.value = ''
  showForm.value = true
}

function openBearbeiten(ab) {
  showErgebnis.value = false
  editTarget.value = ab
  form.value = {
    name: ab.name,
    titel: ab.titel,
    beschreibung: ab.beschreibung || '',
    datum_von: ab.datum_von,
    datum_bis: ab.datum_bis,
    sparte: ab.sparte || '',
    status: ab.status,
    nur_stimmberechtigt: !!ab.nur_stimmberechtigt,
    anonym: !!ab.anonym,
    fragen: JSON.parse(JSON.stringify(ab.fragen || [])),
  }
  formError.value = ''
  showForm.value = true
}

async function openErgebnis(ab) {
  ergebnisRaw.value = ab
  ergebnisData.value = null
  showErgebnis.value = true
  ergebnisLoading.value = true
  try {
    ergebnisData.value = await api.call('dms_verein.api.verein.get_abstimmung_ergebnis', { name: ab.name })
  } finally { ergebnisLoading.value = false }
}

function addFrage() {
  form.value.fragen.push({ frage: '', typ: 'Einfachauswahl', optionen: ['', ''] })
}
function removeFrage(fi) { form.value.fragen.splice(fi, 1) }
function addOption(fi) { form.value.fragen[fi].optionen.push('') }
function removeOption(fi, oi) {
  if (form.value.fragen[fi].optionen.length > 2) form.value.fragen[fi].optionen.splice(oi, 1)
}

async function saveAbstimmung() {
  formError.value = ''
  if (!form.value.titel || !form.value.datum_von || !form.value.datum_bis) {
    formError.value = 'Bitte Titel und Zeitraum ausfüllen.'; return
  }
  if (!form.value.fragen.length) { formError.value = 'Mindestens eine Frage erforderlich.'; return }
  for (const f of form.value.fragen) {
    if (!f.frage) { formError.value = 'Alle Fragen müssen einen Text haben.'; return }
    if (f.optionen.filter(o => o.trim()).length < 2) { formError.value = 'Jede Frage braucht mindestens 2 Optionen.'; return }
    f.optionen = f.optionen.filter(o => o.trim())
  }
  saving.value = true
  try {
    await api.call('dms_verein.api.verein.save_abstimmung', { data: JSON.stringify(form.value) })
    showForm.value = false
    await load()
  } catch (e) { formError.value = e.message }
  finally { saving.value = false }
}

function confirmDelete(ab) { deleteTarget.value = ab; showDelete.value = true }
async function doDelete() {
  deleting.value = true
  try {
    await api.call('dms_verein.api.verein.delete_abstimmung', { name: deleteTarget.value.name })
    showDelete.value = false
    await load()
  } finally { deleting.value = false }
}
</script>
