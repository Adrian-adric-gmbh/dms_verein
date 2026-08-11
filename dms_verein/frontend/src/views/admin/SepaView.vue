<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2>SEPA Lastschrift</h2>
        <p class="text-slate-500 mt-1">Mandate verwalten und Lastschrift-Dateien erstellen</p>
      </div>
      <button @click="showNeu = true" class="btn btn-primary">
        <Plus :size="16" /> Neues Mandat
      </button>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 mb-6 bg-slate-100 p-1 rounded-xl w-fit">
      <button v-for="t in tabs" :key="t.id" @click="activeTab = t.id"
        :class="['px-4 py-1.5 rounded-lg text-sm font-medium transition-all',
                 activeTab === t.id ? 'bg-white shadow text-slate-900' : 'text-slate-500 hover:text-slate-700']">
        {{ t.label }}
        <span v-if="t.count" class="ml-1.5 text-xs bg-slate-200 text-slate-600 rounded-full px-1.5 py-0.5">{{ t.count }}</span>
      </button>
    </div>

    <!-- Tab: Mandate -->
    <div v-if="activeTab === 'mandate'">
      <div class="flex flex-wrap gap-3 mb-4">
        <select v-model="filterStatus" @change="loadMandate" class="input w-36 text-sm">
          <option value="">Alle Status</option>
          <option>Aktiv</option>
          <option>Widerrufen</option>
          <option>Abgelaufen</option>
        </select>
        <input v-model="mandatSearch" @input="debounceLoad" placeholder="Mitglied suchen..." class="input w-48 text-sm" />
      </div>
      <AppSpinner v-if="loadingMandate" full-page />
      <div v-else class="card">
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Referenz</th><th>Mitglied</th><th>Kontoinhaber</th>
                <th>IBAN</th><th>Erteilt am</th><th>Einzüge</th><th>Status</th><th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!mandate.length">
                <td colspan="8" class="text-center py-10 text-slate-400">Keine Mandate gefunden.</td>
              </tr>
              <tr v-for="m in mandate" :key="m.name" class="hover:bg-slate-50">
                <td class="font-mono text-xs">{{ m.mandatsreferenz }}</td>
                <td>
                  <div class="font-medium text-sm">{{ m.mitglied_name }}</div>
                  <div class="text-xs text-slate-400">Nr. {{ m.mitgliedsnummer }}</div>
                </td>
                <td class="text-sm">{{ m.kontoinhaber }}</td>
                <td class="font-mono text-xs">{{ ibanFormatted(m.iban) }}</td>
                <td class="text-sm text-slate-500">{{ formatDate(m.erteilungsdatum) }}</td>
                <td class="text-sm text-center">
                  {{ m.anzahl_einzuege || 0 }}
                  <span v-if="m.letzter_einzug" class="block text-xs text-slate-400">
                    zuletzt {{ formatDate(m.letzter_einzug) }}
                  </span>
                </td>
                <td>
                  <span :class="['badge text-xs', m.status === 'Aktiv' ? 'badge-green' : 'badge-gray']">
                    {{ m.status }}
                  </span>
                </td>
                <td>
                  <button v-if="m.status === 'Aktiv'" @click="openWiderruf(m)"
                    class="btn btn-secondary btn-sm text-red-600 hover:bg-red-50 p-1.5" title="Widerrufen">
                    <X :size="13" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Tab: Einzug starten -->
    <div v-if="activeTab === 'einzug'" class="space-y-6">
      <!-- Info-Karten -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="card card-body text-center">
          <div class="text-2xl font-bold text-slate-800">{{ einzugInfo.anzahl }}</div>
          <div class="text-xs text-slate-500 mt-1">Rechnungen</div>
        </div>
        <div class="card card-body text-center">
          <div class="text-2xl font-bold text-indigo-600">{{ formatBetrag(einzugInfo.summe) }}</div>
          <div class="text-xs text-slate-500 mt-1">Gesamtbetrag</div>
        </div>
        <div class="card card-body text-center">
          <div class="text-lg font-bold text-slate-800">
            <span class="text-green-600">{{ einzugInfo.frst }}</span>
            <span class="text-slate-400 text-sm"> / </span>
            <span class="text-blue-600">{{ einzugInfo.rcur }}</span>
          </div>
          <div class="text-xs text-slate-500 mt-1">Ersteinzug / Wiederkehrend</div>
        </div>
      </div>

      <!-- Einzug-Formular -->
      <div class="card card-body space-y-4">
        <h3 class="font-semibold text-slate-800">SEPA-Datei erstellen</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="form-group">
            <label class="label">Jahr</label>
            <select v-model="einzugJahr" class="input" @change="ladeEinzugInfo">
              <option value="">Alle offenen</option>
              <option v-for="y in jahre" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="label">Einzugsdatum (frühestens 5 Werktage in der Zukunft)</label>
            <input type="date" v-model="einzugsdatum" class="input" :min="minEinzugsdatum" />
          </div>
        </div>
        <AppAlert v-if="einzugError" type="error" :message="einzugError" />
        <div class="flex gap-3 pt-2">
          <button @click="xmlGenerieren" :disabled="generierenRunning || !einzugsdatum"
            class="btn btn-primary">
            <Download :size="15" />
            {{ generierenRunning ? 'Wird erstellt...' : 'XML-Datei herunterladen' }}
          </button>
        </div>
        <p class="text-xs text-slate-400">
          Die SEPA-XML-Datei (pain.008.003.02) lädst du in deine Online-Banking-Software hoch.
          Danach klickst du auf "Als eingezogen markieren" um alle Rechnungen als bezahlt zu setzen.
        </p>
      </div>

      <!-- Letzter Einzug bestätigen -->
      <div v-if="letzterEinzug" class="card card-body space-y-3 border-l-4 border-amber-400">
        <h3 class="font-semibold text-slate-800">Letzten Einzug bestätigen</h3>
        <p class="text-sm text-slate-600">
          Du hast am {{ formatDate(letzterEinzug.datum) }} eine XML-Datei mit
          <strong>{{ letzterEinzug.anzahl }} Rechnungen</strong>
          ({{ formatBetrag(letzterEinzug.summe) }}) erstellt.
          Sobald die Bank den Einzug durchgeführt hat, hier bestätigen:
        </p>
        <div class="flex gap-3">
          <button @click="bestaetigeEinzug" :disabled="bestaetigenRunning"
            class="btn btn-primary btn-sm">
            <CheckCircle :size="14" />
            {{ bestaetigenRunning ? 'Wird markiert...' : 'Als eingezogen markieren' }}
          </button>
          <button @click="letzterEinzug = null" class="btn btn-secondary btn-sm">
            Verwerfen
          </button>
        </div>
      </div>
    </div>

    <!-- Tab: Ohne Mandat -->
    <div v-if="activeTab === 'ohnemandat'">
      <p class="text-sm text-slate-500 mb-4">
        Aktive Mitglieder mit hinterlegter IBAN, aber noch ohne aktives SEPA-Mandat.
        Du kannst direkt ein Mandat anlegen.
      </p>
      <AppSpinner v-if="loadingOhne" full-page />
      <div v-else class="card">
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr><th>Mitglied</th><th>IBAN</th><th>Kreditinstitut</th><th></th></tr>
            </thead>
            <tbody>
              <tr v-if="!ohneMandat.length">
                <td colspan="4" class="text-center py-10 text-slate-400">
                  Alle Mitglieder mit IBAN haben bereits ein aktives Mandat.
                </td>
              </tr>
              <tr v-for="m in ohneMandat" :key="m.name" class="hover:bg-slate-50">
                <td>
                  <div class="font-medium text-sm">{{ m.mitglied_name }}</div>
                  <div class="text-xs text-slate-400">Nr. {{ m.mitgliedsnummer }}</div>
                </td>
                <td class="font-mono text-xs">{{ ibanFormatted(m.iban) }}</td>
                <td class="text-sm text-slate-500">{{ m.bank_name || '—' }}</td>
                <td>
                  <button @click="prefillNeu(m)" class="btn btn-secondary btn-sm">
                    <Plus :size="13" /> Mandat anlegen
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal: Neues Mandat -->
    <AppModal :show="showNeu" title="Neues SEPA-Mandat" size="md" @close="closeNeu">
      <div class="space-y-4">
        <div class="form-group">
          <label class="label">Mitglied *</label>
          <select v-model="neuForm.mitglied" class="input" @change="onMitgliedChange">
            <option value="">— Mitglied wählen —</option>
            <option v-for="m in alleMitglieder" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
        </div>
        <div class="form-group">
          <label class="label">Kontoinhaber *</label>
          <input v-model="neuForm.kontoinhaber" class="input" placeholder="Max Mustermann" />
        </div>
        <div class="form-group">
          <label class="label">IBAN *</label>
          <input v-model="neuForm.iban" class="input font-mono" placeholder="DE12 3456 7890 1234 5678 90" @input="formatIban" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="form-group">
            <label class="label">BIC</label>
            <input v-model="neuForm.bic" class="input font-mono uppercase" placeholder="DEUTDEDB" />
          </div>
          <div class="form-group">
            <label class="label">Kreditinstitut</label>
            <input v-model="neuForm.bank_name" class="input" placeholder="Deutsche Bank" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="form-group">
            <label class="label">Mandatserteilungsdatum *</label>
            <input type="date" v-model="neuForm.erteilungsdatum" class="input" />
          </div>
          <div class="form-group">
            <label class="label">Mandatsart</label>
            <select v-model="neuForm.art" class="input">
              <option value="CORE (Basis)">CORE (Basis)</option>
              <option value="COR1 (Einzel-SEPA)">COR1 (Einzel-SEPA)</option>
            </select>
          </div>
        </div>
        <AppAlert v-if="neuError" type="error" :message="neuError" />
      </div>
      <template #footer>
        <button @click="closeNeu" class="btn btn-secondary">Abbrechen</button>
        <button @click="speichernMandat" :disabled="neuRunning" class="btn btn-primary">
          {{ neuRunning ? 'Speichert...' : 'Mandat anlegen' }}
        </button>
      </template>
    </AppModal>

    <!-- Modal: Widerruf -->
    <AppModal :show="showWiderruf" title="Mandat widerrufen" size="sm" @close="showWiderruf = false">
      <div class="space-y-4">
        <p class="text-sm text-slate-600">
          Mandat <strong class="font-mono">{{ widerrufMandat?.mandatsreferenz }}</strong> von
          <strong>{{ widerrufMandat?.mitglied_name }}</strong> widerrufen?
        </p>
        <div class="form-group">
          <label class="label">Widerrufsgrund (optional)</label>
          <input v-model="widerrufGrund" class="input" placeholder="z.B. Kontoänderung, Austritt, ..." />
        </div>
      </div>
      <template #footer>
        <button @click="showWiderruf = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="widerrufen" :disabled="widerrufRunning" class="btn btn-danger">
          {{ widerrufRunning ? 'Wird widerrufen...' : 'Mandat widerrufen' }}
        </button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { Plus, X, Download, CheckCircle } from 'lucide-vue-next'

// ─── State ────────────────────────────────────────────────────────────────────

const activeTab = ref('mandate')
const mandate = ref([])
const ohneMandat = ref([])
const loadingMandate = ref(true)
const loadingOhne = ref(false)
const filterStatus = ref('Aktiv')
const mandatSearch = ref('')

// Einzug
const einzugJahr = ref(new Date().getFullYear())
const einzugsdatum = ref('')
const einzugInfo = ref({ anzahl: 0, summe: 0, frst: 0, rcur: 0 })
const einzugError = ref('')
const generierenRunning = ref(false)
const letzterEinzug = ref(null)
const bestaetigenRunning = ref(false)

// Neues Mandat
const showNeu = ref(false)
const neuForm = ref({ mitglied: '', kontoinhaber: '', iban: '', bic: '', bank_name: '', erteilungsdatum: '', art: 'CORE (Basis)' })
const neuError = ref('')
const neuRunning = ref(false)
const alleMitglieder = ref([])

// Widerruf
const showWiderruf = ref(false)
const widerrufMandat = ref(null)
const widerrufGrund = ref('')
const widerrufRunning = ref(false)

// ─── Computed ─────────────────────────────────────────────────────────────────

const jahre = computed(() => {
  const y = new Date().getFullYear()
  return [y, y - 1, y - 2]
})

const minEinzugsdatum = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() + 5)
  return d.toISOString().slice(0, 10)
})

const tabs = computed(() => [
  { id: 'mandate',    label: 'Mandate',          count: mandate.value.filter(m => m.status === 'Aktiv').length },
  { id: 'einzug',    label: 'Einzug starten',    count: null },
  { id: 'ohnemandat',label: 'Ohne Mandat',       count: ohneMandat.value.length || null },
])

// ─── Lifecycle ────────────────────────────────────────────────────────────────

function onSepaMandatUpdate() {
  loadMandate()
  loadOhneMandat()
}

onMounted(async () => {
  await Promise.all([loadMandate(), loadOhneMandat(), ladeMitglieder(), ladeEinzugInfo()])
  // Standard Einzugsdatum: 5 Werktage in Zukunft
  const d = new Date()
  d.setDate(d.getDate() + 7)
  einzugsdatum.value = d.toISOString().slice(0, 10)
  window.addEventListener('frappe:sepa_mandat_update', onSepaMandatUpdate)
})

onUnmounted(() => {
  window.removeEventListener('frappe:sepa_mandat_update', onSepaMandatUpdate)
})

// ─── Mandate ─────────────────────────────────────────────────────────────────

async function loadMandate() {
  loadingMandate.value = true
  try {
    mandate.value = await api.call('dms_verein.api.verein.get_sepa_mandate', {
      status: filterStatus.value, search: mandatSearch.value,
    })
  } finally { loadingMandate.value = false }
}

async function loadOhneMandat() {
  loadingOhne.value = true
  try {
    ohneMandat.value = await api.call('dms_verein.api.verein.get_mitglieder_ohne_mandat')
  } finally { loadingOhne.value = false }
}

let debounceTimer = null
function debounceLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadMandate, 300)
}

// ─── Einzug ──────────────────────────────────────────────────────────────────

async function ladeEinzugInfo() {
  try {
    // Nur Vorschau — zählen ohne XML zu generieren
    einzugInfo.value = await api.call('dms_verein.api.verein.get_sepa_vorschau',
      { jahr: einzugJahr.value || '' })
  } catch { /* ignore */ }
}

async function xmlGenerieren() {
  if (!einzugsdatum.value) return
  einzugError.value = ''
  generierenRunning.value = true
  try {
    const result = await api.call('dms_verein.api.verein.generate_sepa_xml', {
      einzugsdatum: einzugsdatum.value,
      jahr: einzugJahr.value || '',
    })
    // Download triggern
    const blob = new Blob([result.xml], { type: 'application/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = result.dateiname; a.click()
    URL.revokeObjectURL(url)
    // Einzug merken für Bestätigung
    letzterEinzug.value = {
      datum: new Date().toISOString().slice(0, 10),
      anzahl: result.anzahl,
      summe: result.summe,
      mandate_ids: result.mandate_ids,
      rechnungen: result.rechnungen,
    }
    einzugInfo.value = { anzahl: result.anzahl, summe: result.summe, frst: result.frst, rcur: result.rcur }
  } catch (e) {
    einzugError.value = e.message
  } finally { generierenRunning.value = false }
}

async function bestaetigeEinzug() {
  if (!letzterEinzug.value) return
  bestaetigenRunning.value = true
  try {
    await api.call('dms_verein.api.verein.sepa_einzug_bestaetigen', {
      mandat_ids: JSON.stringify(letzterEinzug.value.mandate_ids),
      rechnung_infos: JSON.stringify(letzterEinzug.value.rechnungen),
    })
    letzterEinzug.value = null
    await Promise.all([loadMandate(), ladeEinzugInfo()])
  } catch (e) { einzugError.value = e.message }
  finally { bestaetigenRunning.value = false }
}

// ─── Neues Mandat ─────────────────────────────────────────────────────────────

async function ladeMitglieder() {
  const rows = await api.call('dms_verein.api.verein.get_mitglieder_liste_einfach').catch(() => [])
  alleMitglieder.value = rows
}

function prefillNeu(m) {
  neuForm.value = {
    mitglied: m.name,
    kontoinhaber: m.mitglied_name,
    iban: m.iban,
    bic: m.bic || '',
    bank_name: m.bank_name || '',
    erteilungsdatum: new Date().toISOString().slice(0, 10),
    art: 'CORE (Basis)',
  }
  showNeu.value = true
}

async function onMitgliedChange() {
  const m = ohneMandat.value.find(x => x.name === neuForm.value.mitglied)
  if (m) {
    neuForm.value.kontoinhaber = m.mitglied_name
    neuForm.value.iban = m.iban
    neuForm.value.bic = m.bic || ''
    neuForm.value.bank_name = m.bank_name || ''
  }
}

function formatIban() {
  const raw = neuForm.value.iban.replace(/\s/g, '').toUpperCase()
  neuForm.value.iban = raw.match(/.{1,4}/g)?.join(' ') || raw
}

async function speichernMandat() {
  neuError.value = ''
  if (!neuForm.value.mitglied || !neuForm.value.iban || !neuForm.value.kontoinhaber || !neuForm.value.erteilungsdatum) {
    neuError.value = 'Bitte alle Pflichtfelder ausfüllen.'
    return
  }
  neuRunning.value = true
  try {
    await api.call('dms_verein.api.verein.create_sepa_mandat', { ...neuForm.value })
    closeNeu()
    await Promise.all([loadMandate(), loadOhneMandat()])
  } catch (e) { neuError.value = e.message }
  finally { neuRunning.value = false }
}

function closeNeu() {
  showNeu.value = false
  neuError.value = ''
  neuForm.value = { mitglied: '', kontoinhaber: '', iban: '', bic: '', bank_name: '', erteilungsdatum: '', art: 'CORE (Basis)' }
}

// ─── Widerruf ─────────────────────────────────────────────────────────────────

function openWiderruf(m) {
  widerrufMandat.value = m
  widerrufGrund.value = ''
  showWiderruf.value = true
}

async function widerrufen() {
  widerrufRunning.value = true
  try {
    await api.call('dms_verein.api.verein.widerruf_sepa_mandat', {
      mandat_name: widerrufMandat.value.name,
      grund: widerrufGrund.value,
    })
    showWiderruf.value = false
    await loadMandate()
  } catch (e) { alert(e.message) }
  finally { widerrufRunning.value = false }
}

// ─── Helfer ───────────────────────────────────────────────────────────────────

const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE') : '—'
const formatBetrag = (v) => Number(v || 0).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
const ibanFormatted = (iban) => (iban || '').replace(/\s/g, '').match(/.{1,4}/g)?.join(' ') || iban || '—'
</script>
