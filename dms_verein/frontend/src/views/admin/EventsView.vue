<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2>Veranstaltungen</h2><p class="text-slate-500 mt-1">Events verwalten und planen</p></div>
      <button @click="openCreate" class="btn btn-primary"><Plus :size="16" /> Neue Veranstaltung</button>
    </div>
    <AppSpinner v-if="loading" full-page />
    <div v-else class="table-wrapper">
      <table class="table">
        <thead><tr><th>Datum</th><th>Titel</th><th>Kategorie</th><th>Ort</th><th>Status</th><th>Öff.</th><th></th></tr></thead>
        <tbody>
          <tr v-if="!events.length"><td colspan="7" class="text-center py-8 text-slate-400">Keine Veranstaltungen</td></tr>
          <tr v-for="e in events" :key="e.name" class="cursor-pointer hover:bg-slate-50" @click="openDetail(e)">
            <td class="text-sm font-medium whitespace-nowrap">{{ formatDate(e.datum_von) }}</td>
            <td class="font-medium">{{ e.titel }}</td>
            <td><span class="badge badge-blue">{{ e.kategorie }}</span></td>
            <td class="text-sm text-slate-500">{{ e.veranstaltungsort || '—' }}</td>
            <td><StatusBadge :status="e.status" /></td>
            <td><span :class="['badge', e.oeffentlich ? 'badge-green' : 'badge-gray']">{{ e.oeffentlich ? 'Ja' : 'Nein' }}</span></td>
            <td @click.stop>
              <div class="flex gap-1">
                <button @click="openEdit(e)" class="btn btn-secondary btn-sm p-1.5"><Pencil :size="13" /></button>
                <button @click="deleteEvent(e)" class="btn btn-danger btn-sm p-1.5"><Trash2 :size="13" /></button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Detail Modal (view) -->
    <AppModal v-if="selected && !showEdit" :show="!!selected" :title="selected.titel" size="xl" @close="closeDetail">
      <!-- Tabs -->
      <div class="border-b border-slate-200 -mx-6 px-6 mb-4">
        <div class="flex gap-4">
          <button v-for="tab in ['Details', 'Teilnehmer']" :key="tab" @click="activeTab = tab"
            :class="['pb-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab ? 'border-primary-600 text-primary-700' : 'border-transparent text-slate-500 hover:text-slate-700']">
            {{ tab }}
            <span v-if="tab === 'Teilnehmer' && teilnehmer.length"
              class="ml-1 bg-primary-100 text-primary-700 rounded-full text-xs px-1.5 py-0.5">{{ teilnehmer.length }}</span>
          </button>
        </div>
      </div>

      <!-- Tab: Details -->
      <div v-if="activeTab === 'Details'" class="text-sm">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">

          <!-- Linke Spalte: Info -->
          <div class="space-y-2.5">
            <div class="grid grid-cols-2 gap-x-4 gap-y-2.5">
              <div class="flex flex-col gap-0.5">
                <span class="text-xs text-slate-400 uppercase tracking-wide">Datum</span>
                <span class="font-medium">{{ formatDate(selected.datum_von) }}</span>
              </div>
              <div class="flex flex-col gap-0.5">
                <span class="text-xs text-slate-400 uppercase tracking-wide">Uhrzeit</span>
                <span class="font-medium">{{ selected.uhrzeit_von?.slice(0,5) || '—' }}</span>
              </div>
              <div class="flex flex-col gap-0.5">
                <span class="text-xs text-slate-400 uppercase tracking-wide">Kategorie</span>
                <span class="font-medium">{{ selected.kategorie || '—' }}</span>
              </div>
              <div class="flex flex-col gap-0.5">
                <span class="text-xs text-slate-400 uppercase tracking-wide">Status</span>
                <StatusBadge :status="selected.status" />
              </div>
              <div class="col-span-2 flex flex-col gap-0.5">
                <span class="text-xs text-slate-400 uppercase tracking-wide">Veranstaltungsort</span>
                <span class="font-medium">{{ selected.veranstaltungsort || '—' }}</span>
              </div>
              <div v-if="selected.adresse" class="col-span-2 flex flex-col gap-0.5">
                <span class="text-xs text-slate-400 uppercase tracking-wide">Adresse</span>
                <span class="font-medium">{{ selected.adresse }}</span>
              </div>
            </div>

            <!-- Optionale Felder -->
            <div v-if="selected.max_teilnehmer || selected.anmeldeschluss || selected.kosten_mitglieder || selected.kosten_gaeste"
              class="border-t border-slate-100 pt-2.5 grid grid-cols-2 gap-x-4 gap-y-2.5">
              <div v-if="selected.max_teilnehmer" class="flex flex-col gap-0.5">
                <span class="text-xs text-slate-400 uppercase tracking-wide">Max. Teilnehmer</span>
                <span class="font-medium">{{ selected.max_teilnehmer }}</span>
              </div>
              <div v-if="selected.anmeldeschluss" class="flex flex-col gap-0.5">
                <span class="text-xs text-slate-400 uppercase tracking-wide">Anmeldeschluss</span>
                <span class="font-medium">{{ formatDate(selected.anmeldeschluss) }}</span>
              </div>
              <div v-if="selected.kosten_mitglieder" class="flex flex-col gap-0.5">
                <span class="text-xs text-slate-400 uppercase tracking-wide">Kosten Mitglieder</span>
                <span class="font-medium">{{ formatBetrag(selected.kosten_mitglieder) }}</span>
              </div>
              <div v-if="selected.kosten_gaeste" class="flex flex-col gap-0.5">
                <span class="text-xs text-slate-400 uppercase tracking-wide">Kosten Gäste</span>
                <span class="font-medium">{{ formatBetrag(selected.kosten_gaeste) }}</span>
              </div>
            </div>

            <!-- Beschreibung unter Info (mobile: hier, desktop: zentriert) -->
            <div v-if="selected.beschreibung" class="lg:hidden border-t pt-3">
              <p class="text-slate-400 text-xs uppercase tracking-wide mb-1.5">Beschreibung</p>
              <div class="prose prose-sm max-w-none" v-html="selected.beschreibung" />
            </div>
          </div>

          <!-- Rechte Spalte: Karte -->
          <div>
            <MapCard
              v-if="selected.adresse || selected.veranstaltungsort"
              :address="selected.adresse || selected.veranstaltungsort"
              :maps-key="verein.info?.google_maps_key"
              :height="300"
            />
            <div v-else class="h-[300px] rounded-xl border border-dashed border-slate-200 flex items-center justify-center text-slate-300">
              <MapPin :size="32" />
            </div>
          </div>
        </div>

        <!-- Beschreibung full-width (nur Desktop) -->
        <div v-if="selected.beschreibung" class="hidden lg:block border-t border-slate-100 pt-4 mt-4">
          <p class="text-slate-400 text-xs uppercase tracking-wide mb-1.5">Beschreibung</p>
          <div class="prose prose-sm max-w-none" v-html="selected.beschreibung" />
        </div>
      </div>

      <!-- Tab: Teilnehmer -->
      <div v-else-if="activeTab === 'Teilnehmer'">
        <AppSpinner v-if="loadingTeilnehmer" />
        <div v-else>
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm text-slate-500">{{ teilnehmer.length }} Anmeldungen</span>
            <button @click="exportTeilnehmer" class="btn btn-secondary btn-sm flex items-center gap-1.5">
              <Download :size="13" /> CSV Export
            </button>
          </div>
          <div v-if="!teilnehmer.length" class="text-center py-10 text-slate-400 text-sm">Noch keine Anmeldungen.</div>
          <div v-else class="table-wrapper">
            <table class="table text-sm">
              <thead><tr><th>Mitglied</th><th>Nr.</th><th>Status</th><th>Angemeldet</th><th></th></tr></thead>
              <tbody>
                <tr v-for="t in teilnehmer" :key="t.name">
                  <td>
                    <div class="font-medium">{{ t.vollname }}</div>
                    <div v-if="t.email" class="text-xs text-slate-400">{{ t.email }}</div>
                  </td>
                  <td class="text-xs text-slate-400">{{ t.mitgliedsnummer || '—' }}</td>
                  <td>
                    <span :class="['badge text-xs', t.status==='Angemeldet'?'badge-green':t.status==='Warteliste'?'badge-amber':t.status==='Abgesagt'?'badge-gray':'badge-blue']">
                      {{ t.status }}
                    </span>
                  </td>
                  <td class="text-xs text-slate-400">{{ formatDate(t.anmeldedatum) }}</td>
                  <td>
                    <select class="text-xs border border-slate-200 rounded px-1 py-0.5 bg-white"
                      :value="t.status" @change="changeTeilnehmerStatus(t, $event.target.value)">
                      <option>Angemeldet</option><option>Anwesend</option>
                      <option>Warteliste</option><option>Abgesagt</option>
                    </select>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <template #footer>
        <button @click="closeDetail" class="btn btn-secondary">Schließen</button>
        <button @click="openEdit(selected)" class="btn btn-secondary"><Pencil :size="14" /> Bearbeiten</button>
        <button @click="deleteEvent(selected)" class="btn btn-danger"><Trash2 :size="14" /> Löschen</button>
      </template>
    </AppModal>

    <!-- Edit/Create Modal -->
    <AppModal :show="showEdit || showCreate" :title="editTarget ? 'Veranstaltung bearbeiten' : 'Neue Veranstaltung'" size="lg" @close="closeForm">
      <form @submit.prevent="saveForm" class="space-y-4">
        <AppAlert v-if="formError" type="error" :message="formError" />
        <div class="form-group"><label class="label">Titel *</label><input v-model="form.titel" class="input" required /></div>
        <div class="grid grid-cols-2 gap-3">
          <div class="form-group"><label class="label">Kategorie</label>
            <select v-model="form.kategorie" class="input">
              <option>Vereinsveranstaltung</option><option>Hauptversammlung</option><option>Training</option>
              <option>Turnier</option><option>Ausflug</option><option>Fest</option><option>Sonstige</option>
            </select>
          </div>
          <div class="form-group"><label class="label">Status</label>
            <select v-model="form.status" class="input"><option>Geplant</option><option>Bestätigt</option><option>Abgesagt</option></select>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="form-group"><label class="label">Datum *</label><input v-model="form.datum_von" type="date" class="input" required /></div>
          <div class="form-group"><label class="label">Uhrzeit</label><input v-model="form.uhrzeit_von" type="time" class="input" /></div>
        </div>
        <div class="form-group"><label class="label">Veranstaltungsort (Name)</label><input v-model="form.veranstaltungsort" class="input" placeholder="z. B. Sportheim TSV, Vereinsheim" /></div>
        <!-- Adresse mit Google-Suche -->
        <div class="form-group" v-if="verein.info?.google_maps_key">
          <label class="label">Adresse</label>
          <div class="relative">
            <input v-model="adressSuche" @input="onAdressInput" @blur="hideGeoDropdown"
              class="input pr-10" placeholder="Straße, PLZ Ort suchen…" autocomplete="off" />
            <MapPin :size="16" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            <!-- Dropdown -->
            <div v-if="geoResults.length && showGeoDropdown"
              class="absolute z-50 left-0 right-0 bg-white border border-slate-200 rounded-xl shadow-lg mt-1 overflow-hidden">
              <button v-for="r in geoResults" :key="r.formatted_address"
                @mousedown.prevent="selectGeoResult(r)"
                class="w-full text-left px-4 py-2.5 text-sm hover:bg-slate-50 border-b border-slate-100 last:border-0 truncate">
                {{ r.formatted_address }}
              </button>
            </div>
          </div>
          <p v-if="form.adresse" class="text-xs text-slate-400 mt-1">Gespeichert: {{ form.adresse }}</p>
        </div>
        <div class="form-group" v-else>
          <label class="label">Adresse</label>
          <input v-model="form.adresse" class="input" placeholder="Straße, PLZ Ort" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="form-group"><label class="label">Max. Teilnehmer</label><input v-model="form.max_teilnehmer" type="number" class="input" /></div>
          <div class="form-group"><label class="label">Anmeldeschluss</label><input v-model="form.anmeldeschluss" type="date" class="input" /></div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="form-group"><label class="label">Kosten Mitglieder (€)</label><input v-model="form.kosten_mitglieder" type="number" step="0.01" class="input" /></div>
          <div class="form-group"><label class="label">Kosten Gäste (€)</label><input v-model="form.kosten_gaeste" type="number" step="0.01" class="input" /></div>
        </div>
        <div class="form-group"><label class="label">Beschreibung</label><textarea v-model="form.beschreibung" class="input h-24 resize-none" /></div>
        <div class="flex gap-4">
          <label class="flex items-center gap-2 cursor-pointer"><input v-model="form.oeffentlich" type="checkbox" :true-value="1" :false-value="0" class="w-4 h-4" /><span class="text-sm">Öffentlich sichtbar</span></label>
          <label class="flex items-center gap-2 cursor-pointer"><input v-model="form.anmeldung_erforderlich" type="checkbox" :true-value="1" :false-value="0" class="w-4 h-4" /><span class="text-sm">Anmeldung erforderlich</span></label>
        </div>
      </form>
      <template #footer>
        <button @click="closeForm" class="btn btn-secondary">Abbrechen</button>
        <button @click="saveForm" :disabled="saving" class="btn btn-primary"><Save :size="14" /> {{ saving ? 'Speichert...' : 'Speichern' }}</button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import MapCard from '@/components/ui/MapCard.vue'
import { Plus, Pencil, Trash2, Save, Download, MapPin } from 'lucide-vue-next'
import { useRealtimeRefresh } from '@/composables/useRealtimeRefresh'
import { useVereinStore } from '@/stores/verein'

const verein = useVereinStore()

const events = ref([])
const loading = ref(true)
const selected = ref(null)
const editTarget = ref(null)
const showEdit = ref(false)
const showCreate = ref(false)
const saving = ref(false)
const formError = ref('')
const activeTab = ref('Details')
const teilnehmer = ref([])
const loadingTeilnehmer = ref(false)
const adressSuche = ref('')
const geoResults = ref([])
const showGeoDropdown = ref(false)
let geoTimer = null

async function onAdressInput() {
  showGeoDropdown.value = true
  clearTimeout(geoTimer)
  if (adressSuche.value.length < 3) { geoResults.value = []; return }
  geoTimer = setTimeout(async () => {
    try {
      geoResults.value = await api.call('dms_verein.api.verein.geocode_adresse', { query: adressSuche.value }) || []
    } catch { geoResults.value = [] }
  }, 400)
}
function selectGeoResult(r) {
  form.value.adresse = r.formatted_address
  adressSuche.value = r.formatted_address
  geoResults.value = []
  showGeoDropdown.value = false
}
function hideGeoDropdown() { setTimeout(() => { showGeoDropdown.value = false }, 150) }

const blankForm = () => ({ titel: '', kategorie: 'Vereinsveranstaltung', status: 'Geplant', datum_von: '', uhrzeit_von: '', veranstaltungsort: '', adresse: '', beschreibung: '', oeffentlich: 1, anmeldung_erforderlich: 0, max_teilnehmer: null, anmeldeschluss: '', kosten_mitglieder: 0, kosten_gaeste: 0 })
const form = ref(blankForm())

onMounted(() => load())
useRealtimeRefresh(['Veranstaltung'], () => load())

async function load() {
  loading.value = true
  try { events.value = await api.getList('Veranstaltung', { fields: ['name','titel','kategorie','datum_von','uhrzeit_von','veranstaltungsort','adresse','status','oeffentlich','anmeldung_erforderlich','max_teilnehmer','anmeldeschluss','kosten_mitglieder','kosten_gaeste','beschreibung'], order_by: 'datum_von desc', limit_page_length: 100 }) || [] }
  finally { loading.value = false }
}

async function openDetail(e) {
  selected.value = e; showEdit.value = false; activeTab.value = 'Details'
  teilnehmer.value = []; loadingTeilnehmer.value = true
  try {
    teilnehmer.value = await api.call('dms_verein.api.verein.get_veranstaltung_anmeldungen', { veranstaltung_name: e.name })
  } finally { loadingTeilnehmer.value = false }
}
function closeDetail() { selected.value = null; teilnehmer.value = [] }

async function changeTeilnehmerStatus(t, status) {
  if (status === t.status) return
  await api.call('dms_verein.api.verein.update_anmeldung_status', { row_name: t.name, status })
  t.status = status
}

function exportTeilnehmer() {
  const header = ['Name', 'Mitgliedsnr.', 'E-Mail', 'Status', 'Angemeldet am']
  const rows = teilnehmer.value.map(t => [
    t.vollname, t.mitgliedsnummer || '', t.email || '', t.status,
    t.anmeldedatum ? new Date(t.anmeldedatum).toLocaleDateString('de-DE') : ''
  ])
  const csv = [header, ...rows].map(r => r.map(c => `"${String(c).replace(/"/g,'""')}"`).join(';')).join('\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
  a.download = `Teilnehmer_${selected.value?.titel || 'Event'}.csv`; a.click()
}
function openCreate() { editTarget.value = null; form.value = blankForm(); formError.value = ''; showCreate.value = true }
function openEdit(e) {
  editTarget.value = e
  form.value = { titel: e.titel, kategorie: e.kategorie, status: e.status, datum_von: e.datum_von?.split(' ')[0] || '', uhrzeit_von: e.uhrzeit_von || '', veranstaltungsort: e.veranstaltungsort || '', adresse: e.adresse || '', beschreibung: e.beschreibung || '', oeffentlich: e.oeffentlich ?? 1, anmeldung_erforderlich: e.anmeldung_erforderlich ?? 0, max_teilnehmer: e.max_teilnehmer || null, anmeldeschluss: e.anmeldeschluss?.split(' ')[0] || '', kosten_mitglieder: e.kosten_mitglieder || 0, kosten_gaeste: e.kosten_gaeste || 0 }
  adressSuche.value = e.adresse || ''
  formError.value = ''
  selected.value = null
  showEdit.value = true
}
function closeForm() { showEdit.value = false; showCreate.value = false; editTarget.value = null }

async function saveForm() {
  saving.value = true; formError.value = ''
  try {
    if (editTarget.value) {
      await api.updateRecord('Veranstaltung', editTarget.value.name, form.value)
    } else {
      await api.insertDoc({ doctype: 'Veranstaltung', ...form.value })
    }
    closeForm(); await load()
  } catch (e) { formError.value = e.message }
  finally { saving.value = false }
}

async function deleteEvent(e) {
  if (!confirm(`Veranstaltung "${e.titel}" wirklich löschen?`)) return
  try { await api.deleteRecord('Veranstaltung', e.name); selected.value = null; await load() }
  catch (err) { alert('Fehler: ' + err.message) }
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE') : '—'
const formatBetrag = (v) => Number(v || 0).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
</script>
