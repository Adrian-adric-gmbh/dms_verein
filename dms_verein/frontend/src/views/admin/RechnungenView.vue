<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2>Beitragsrechnungen</h2><p class="text-slate-500 mt-1">Rechnungen erstellen, verwalten und als bezahlt markieren</p></div>
      <button @click="showGenerieren = true" class="btn btn-primary"><FilePlus :size="16" /> Rechnungen generieren</button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="card card-body text-center">
        <div class="text-2xl font-bold text-slate-800">{{ stats.total || 0 }}</div>
        <div class="text-xs text-slate-500 mt-1">Gesamt</div>
      </div>
      <div class="card card-body text-center">
        <div class="text-2xl font-bold text-amber-600">{{ stats.offen || 0 }}</div>
        <div class="text-xs text-slate-500 mt-1">Offen</div>
      </div>
      <div class="card card-body text-center">
        <div class="text-2xl font-bold text-green-600">{{ stats.bezahlt || 0 }}</div>
        <div class="text-xs text-slate-500 mt-1">Bezahlt</div>
      </div>
      <div class="card card-body text-center">
        <div class="text-2xl font-bold text-red-600">{{ formatBetrag(stats.summe_offen) }}</div>
        <div class="text-xs text-slate-500 mt-1">Offener Betrag</div>
      </div>
    </div>

    <!-- Filter -->
    <div class="flex flex-wrap gap-3 mb-4">
      <select v-model="filterJahr" @change="load" class="input w-28 text-sm">
        <option value="">Alle Jahre</option>
        <option v-for="y in jahre" :key="y" :value="y">{{ y }}</option>
      </select>
      <select v-model="filterStatus" @change="load" class="input w-36 text-sm">
        <option value="">Alle Status</option>
        <option>Offen</option><option>Bezahlt</option>
        <option>Mahnung 1</option><option>Mahnung 2</option><option>Ausgebucht</option>
      </select>
      <input v-model="search" @input="debounceLoad" placeholder="Mitglied suchen..." class="input w-48 text-sm" />
    </div>

    <!-- Tabelle -->
    <AppSpinner v-if="loading" full-page />
    <div v-else class="card">
      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>Rechnungsnr.</th><th>Mitglied</th><th>Beitragsklasse</th>
              <th>Jahr</th><th>Betrag</th><th>Fällig</th><th>Status</th><th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!rows.length">
              <td colspan="8" class="text-center py-10 text-slate-400">Keine Rechnungen gefunden.</td>
            </tr>
            <tr v-for="r in rows" :key="r.name" class="hover:bg-slate-50">
              <td class="font-mono text-xs">{{ r.rechnungsnummer || r.name }}</td>
              <td>
                <div class="font-medium text-sm">{{ r.mitglied_name || r.parent }}</div>
                <div v-if="r.mitgliedsnummer" class="text-xs text-slate-400">Nr. {{ r.mitgliedsnummer }}</div>
              </td>
              <td class="text-sm text-slate-600">{{ r.mitgliedstyp || '—' }}</td>
              <td class="text-sm">{{ r.jahr }}</td>
              <td class="font-semibold text-sm">{{ formatBetrag(r.betrag) }}</td>
              <td class="text-sm text-slate-500">{{ formatDate(r.faelligkeit) }}</td>
              <td>
                <span :class="statusClass(r.status)" class="badge text-xs">{{ r.status }}</span>
              </td>
              <td>
                <div class="flex gap-1 items-center flex-wrap">
                  <button @click="drucken(r)" class="btn btn-secondary btn-sm p-1.5" title="Drucken / PDF">
                    <Printer :size="13" />
                  </button>
                  <button v-if="r.status !== 'Bezahlt'" @click="markBezahlt(r)"
                    class="btn btn-secondary btn-sm p-1.5 text-green-600 hover:bg-green-50" title="Als bezahlt markieren">
                    <CheckCircle :size="13" />
                  </button>
                  <select class="text-xs border border-slate-200 rounded px-1 py-0.5 bg-white"
                    :value="r.status" @change="changeStatus(r, $event.target.value)">
                    <option>Offen</option><option>Bezahlt</option>
                    <option>Mahnung 1</option><option>Mahnung 2</option><option>Ausgebucht</option>
                  </select>
                  <button @click="deleteRechnung(r)"
                    class="btn btn-secondary btn-sm p-1.5 text-red-500 hover:bg-red-50" title="Löschen">
                    <Trash2 :size="13" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginierung -->
      <div class="p-4 border-t border-slate-100 flex items-center justify-between text-sm text-slate-500">
        <span>{{ stats.total }} Einträge gesamt</span>
        <div class="flex gap-2">
          <button :disabled="offset === 0" @click="prev" class="btn btn-secondary btn-sm">← Zurück</button>
          <button :disabled="rows.length < pageSize" @click="next" class="btn btn-secondary btn-sm">Weiter →</button>
        </div>
      </div>
    </div>

    <!-- Generieren Modal -->
    <AppModal :show="showGenerieren" title="Beitragsrechnungen generieren" size="sm" @close="showGenerieren=false">
      <div class="space-y-4">
        <p class="text-sm text-slate-600">
          Generiert für alle aktiven Mitglieder mit Beitragsklasse eine Jahresrechnung. Mitglieder, die bereits eine Rechnung für dieses Jahr haben, werden übersprungen.
        </p>
        <div class="form-group">
          <label class="label">Jahr</label>
          <select v-model="genJahr" class="input">
            <option v-for="y in jahre" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <AppAlert v-if="genResult" :type="genResult.type" :message="genResult.text" />
      </div>
      <template #footer>
        <button @click="showGenerieren=false" class="btn btn-secondary">Schließen</button>
        <button @click="generieren" :disabled="generierenRunning" class="btn btn-primary">
          <FilePlus :size="14" /> {{ generierenRunning ? 'Generiert...' : 'Jetzt generieren' }}
        </button>
      </template>
    </AppModal>

    <!-- Druckansicht -->
    <div v-if="printHtml" class="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between p-4 border-b border-slate-200">
          <h3 class="font-semibold">Druckvorschau</h3>
          <div class="flex gap-2">
            <button @click="printWindow" class="btn btn-primary btn-sm"><Printer :size="14" /> Drucken</button>
            <button @click="printHtml=null" class="btn btn-secondary btn-sm">Schließen</button>
          </div>
        </div>
        <div class="flex-1 overflow-auto">
          <iframe ref="printFrame" :srcdoc="printHtml" class="w-full h-full min-h-[500px]" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { FilePlus, Printer, CheckCircle, Trash2 } from 'lucide-vue-next'
import { useRealtimeRefresh } from '@/composables/useRealtimeRefresh'

const rows = ref([])
const loading = ref(true)
const stats = ref({ total: 0, offen: 0, bezahlt: 0, summe_offen: 0 })
const filterJahr = ref(new Date().getFullYear())
const filterStatus = ref('')
const search = ref('')
const offset = ref(0)
const pageSize = 50
const showGenerieren = ref(false)
const genJahr = ref(new Date().getFullYear())
const generierenRunning = ref(false)
const genResult = ref(null)
const printHtml = ref(null)
const printFrame = ref(null)

const jahre = computed(() => {
  const y = new Date().getFullYear()
  return [y + 1, y, y - 1, y - 2, y - 3]
})

let debounceTimer = null
function debounceLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(load, 300)
}

onMounted(() => load())
useRealtimeRefresh(['Rechnung'], () => load())

async function load() {
  loading.value = true
  try {
    const r = await api.call('dms_verein.api.verein.get_alle_rechnungen', {
      jahr: filterJahr.value || '',
      status: filterStatus.value,
      search: search.value,
      limit: pageSize,
      offset: offset.value,
    })
    rows.value = r.rows || []
    stats.value.total = r.total || 0
    stats.value.offen = r.offen || 0
    stats.value.bezahlt = rows.value.filter(r => r.status === 'Bezahlt').length
    stats.value.summe_offen = rows.value
      .filter(r => r.status === 'Offen')
      .reduce((s, r) => s + (r.betrag || 0), 0)
  } finally { loading.value = false }
}

function prev() { offset.value = Math.max(0, offset.value - pageSize); load() }
function next() { offset.value += pageSize; load() }

async function markBezahlt(r) {
  await api.call('dms_verein.api.verein.update_rechnung_status', {
    parent: r.parent, row_name: r.name, status: 'Bezahlt'
  })
  r.status = 'Bezahlt'
  r.zahlungsdatum = new Date().toISOString().slice(0, 10)
}

async function changeStatus(r, status) {
  if (status === r.status) return
  await api.call('dms_verein.api.verein.update_rechnung_status', {
    parent: r.parent, row_name: r.name, status
  })
  r.status = status
}

async function deleteRechnung(r) {
  if (!confirm(`Rechnung ${r.rechnungsnummer || r.name} von ${r.mitglied_name} wirklich löschen?`)) return
  await api.call('dms_verein.api.verein.delete_rechnung', {
    parent: r.parent, row_name: r.name,
  })
  rows.value = rows.value.filter(x => x.name !== r.name)
  stats.value.total = Math.max(0, stats.value.total - 1)
}

async function drucken(r) {
  try {
    const html = await api.call('dms_verein.api.verein.get_rechnung_html', {
      parent: r.parent, row_name: r.name
    })
    printHtml.value = html
  } catch (e) { alert('Fehler: ' + e.message) }
}

function printWindow() {
  printFrame.value?.contentWindow?.print()
}

async function generieren() {
  generierenRunning.value = true; genResult.value = null
  try {
    const r = await api.call('dms_verein.api.verein.generiere_beitragsrechnungen', { jahr: genJahr.value })
    genResult.value = { type: 'success', text: `${r.erstellt} Rechnung(en) erstellt, ${r.uebersprungen} übersprungen.` }
    await load()
  } catch (e) { genResult.value = { type: 'error', text: e.message } }
  finally { generierenRunning.value = false }
}

const formatBetrag = (v) => Number(v || 0).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE') : '—'
const statusClass = (s) => ({
  'Offen': 'badge-amber', 'Bezahlt': 'badge-green',
  'Mahnung 1': 'badge-orange', 'Mahnung 2': 'badge-red', 'Ausgebucht': 'badge-gray'
}[s] || 'badge-gray')
</script>
