<template>
  <div class="max-w-5xl">
    <div class="flex items-center gap-3 mb-6">
      <RouterLink to="/admin/mitglieder" class="btn btn-secondary btn-sm" title="Zurück zu den Mitgliedern">
        <ArrowLeft :size="16" />
      </RouterLink>
      <div>
        <h2>Mitglieder importieren</h2>
        <p class="text-slate-500 mt-1">CSV prüfen und als protokollierten Hintergrundjob importieren</p>
      </div>
    </div>

    <AppAlert v-if="error" type="error" :message="error" class="mb-4" />

    <section class="border border-slate-200 bg-white p-5 mb-5">
      <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h3 class="font-semibold">1. CSV-Datei auswählen</h3>
          <p class="text-sm text-slate-500 mt-1">UTF-8, maximal 2 MB und 5.000 Datensätze pro Durchlauf.</p>
          <p class="text-sm text-slate-500 mt-1">
            Externe ID ist optional. Mehrere {{ verein.strukturPlural }} in <span class="font-mono">{{ structureColumn }}</span> mit <span class="font-mono">|</span> trennen.
          </p>
        </div>
        <button type="button" class="btn btn-secondary btn-sm" @click="downloadTemplate">
          <Download :size="15" /> Vorlage
        </button>
      </div>
      <input type="file" accept=".csv,text/csv" class="input mt-4" @change="selectFile" />
      <div class="mt-4 grid sm:grid-cols-2 gap-3">
        <label class="flex items-start gap-3 text-sm">
          <input v-model="createPortalUsers" type="checkbox" class="mt-1" />
          <span><strong>Portal-Benutzer anlegen</strong><br><span class="text-slate-500">Erfordert eine eindeutige E-Mail-Adresse pro Mitglied.</span></span>
        </label>
        <label class="flex items-start gap-3 text-sm" :class="{ 'opacity-50': !createPortalUsers }">
          <input v-model="sendWelcome" type="checkbox" class="mt-1" :disabled="!createPortalUsers" />
          <span><strong>Willkommensmail senden</strong><br><span class="text-slate-500">Nur für neu angelegte Benutzer.</span></span>
        </label>
      </div>
      <div class="mt-5 flex justify-end">
        <button class="btn btn-primary" :disabled="!file || busy" @click="validateFile">
          <FileCheck :size="16" /> {{ busy ? 'Datei wird geprüft...' : 'Datei prüfen' }}
        </button>
      </div>
    </section>

    <section v-if="report" class="border border-slate-200 bg-white p-5 mb-5">
      <h3 class="font-semibold mb-4">2. Prüfergebnis</h3>
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div v-for="stat in stats" :key="stat.label" class="border border-slate-200 p-3">
          <p class="text-xs text-slate-500">{{ stat.label }}</p>
          <p class="text-xl font-semibold mt-1">{{ stat.value }}</p>
        </div>
      </div>

      <div v-if="report.fehler?.length" class="mt-5">
        <h4 class="font-medium text-red-700 mb-2">Fehler</h4>
        <div class="table-wrapper max-h-72 overflow-auto">
          <table class="table">
            <thead><tr><th>Zeile</th><th>Externe ID</th><th>Meldung</th></tr></thead>
            <tbody>
              <tr v-for="item in report.fehler" :key="`${item.zeile}-${item.meldung}`">
                <td>{{ item.zeile }}</td>
                <td class="font-mono text-xs">{{ item.externe_id }}</td>
                <td>{{ item.meldung }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="mt-5 flex justify-end">
        <button class="btn btn-primary" :disabled="report.fehleranzahl > 0 || importing || report.neu === 0" @click="startImport">
          <Play :size="16" /> {{ importing ? 'Import läuft...' : `${report.neu} Mitglieder importieren` }}
        </button>
      </div>
    </section>

    <section v-if="result" class="border border-emerald-300 bg-emerald-50 p-5">
      <div class="flex items-start gap-3">
        <CircleCheck :size="22" class="text-emerald-700 shrink-0" />
        <div>
          <h3 class="font-semibold text-emerald-900">{{ result.status }}</h3>
          <p class="text-sm text-emerald-800 mt-1">
            {{ result.importiert }} importiert, {{ result.vorhanden }} bereits vorhanden, {{ result.fehleranzahl }} Fehler.
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { api } from '@/utils/api'
import { useVereinStore } from '@/stores/verein'
import AppAlert from '@/components/ui/AppAlert.vue'
import { ArrowLeft, CircleCheck, Download, FileCheck, Play } from 'lucide-vue-next'

const file = ref(null)
const verein = useVereinStore()
const createPortalUsers = ref(false)
const sendWelcome = ref(false)
const busy = ref(false)
const importing = ref(false)
const report = ref(null)
const result = ref(null)
const error = ref('')
let pollTimer = null

const structureColumn = computed(() => verein.strukturSingular.toLowerCase().includes('stamm') ? 'familienstaemme' : 'abteilungen')

watch(createPortalUsers, enabled => {
  if (!enabled) sendWelcome.value = false
})

const stats = computed(() => report.value ? [
  { label: 'Gesamt', value: report.value.gesamt },
  { label: 'Gültig', value: report.value.gueltig },
  { label: 'Neu', value: report.value.neu },
  { label: 'Vorhanden', value: report.value.vorhanden },
  { label: 'Fehler', value: report.value.fehleranzahl },
] : [])

function selectFile(event) {
  file.value = event.target.files?.[0] || null
  report.value = null
  result.value = null
  error.value = ''
}

function downloadTemplate() {
  const header = `externe_id;mitgliedsnummer;anrede;vorname;nachname;geburtsdatum;strasse;hausnummer;plz;ort;land;email;telefon;mobil;mitgliedstyp;eintrittsdatum;status;${structureColumn.value};iban;bic;bank_name\n`
  const example = ';1001;Frau;Erika;Muster;15.04.1980;Musterweg;12;12345;Musterstadt;Deutschland;erika@example.org;;;Aktiv Erwachsene;01.01.2020;Aktiv;Tennis|Turnen;;;\n'
  const url = URL.createObjectURL(new Blob([header + example], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = 'mitglieder-import-vorlage.csv'
  link.click()
  URL.revokeObjectURL(url)
}

async function validateFile() {
  if (!file.value) return
  busy.value = true
  error.value = ''
  report.value = null
  try {
    const fileUrl = await api.uploadPrivateFile(file.value)
    if (!fileUrl) throw new Error('Die private Datei konnte nicht hochgeladen werden.')
    report.value = await api.validateMitgliederImport(fileUrl, createPortalUsers.value, sendWelcome.value)
  } catch (exception) {
    error.value = exception.message
  } finally {
    busy.value = false
  }
}

async function startImport() {
  importing.value = true
  error.value = ''
  try {
    await api.startMitgliederImport(report.value.batch)
    pollTimer = window.setInterval(pollStatus, 1500)
    await pollStatus()
  } catch (exception) {
    importing.value = false
    error.value = exception.message
  }
}

async function pollStatus() {
  try {
    const status = await api.getMitgliederImportStatus(report.value.batch)
    if (['Abgeschlossen', 'Abgeschlossen mit Fehlern', 'Fehlgeschlagen'].includes(status.status)) {
      window.clearInterval(pollTimer)
      pollTimer = null
      importing.value = false
      result.value = status
    }
  } catch (exception) {
    window.clearInterval(pollTimer)
    pollTimer = null
    importing.value = false
    error.value = exception.message
  }
}

onUnmounted(() => {
  if (pollTimer) window.clearInterval(pollTimer)
})
</script>