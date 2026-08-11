<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2>Mitgliedsanträge</h2>
        <p class="text-slate-500 mt-1">Eingegangene Beitrittsanträge</p>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="flex gap-1 mb-4">
      <button v-for="s in statusFilters" :key="s.value"
        @click="filterStatus = s.value; loadAntraege()"
        :class="['px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                 filterStatus === s.value ? 'bg-primary-600 text-white' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50']">
        {{ s.label }}
        <span v-if="s.count !== undefined" class="ml-1.5 badge" :class="filterStatus === s.value ? 'bg-primary-500 text-white' : 'badge-gray'">{{ s.count }}</span>
      </button>
    </div>

    <div class="table-wrapper">
      <table class="table">
        <thead>
          <tr>
            <th>Eingang</th>
            <th>Name</th>
            <th>Gewünschter Typ</th>
            <th>E-Mail</th>
            <th>Ort</th>
            <th>Status</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="text-center py-8"><AppSpinner /></td>
          </tr>
          <tr v-else-if="!antraege.length">
            <td colspan="7" class="text-center py-8 text-slate-400">Keine Anträge</td>
          </tr>
          <tr v-for="a in antraege" :key="a.name" class="cursor-pointer" @click="selected = a">
            <td class="text-sm text-slate-500 whitespace-nowrap">{{ formatDatetime(a.eingangsdatum) }}</td>
            <td class="font-medium">{{ a.vorname }} {{ a.nachname }}</td>
            <td><span class="badge badge-blue">{{ a.gewuenschter_mitgliedstyp }}</span></td>
            <td class="text-sm text-slate-500">{{ a.email }}</td>
            <td class="text-sm text-slate-500">{{ a.plz }} {{ a.ort }}</td>
            <td><StatusBadge :status="a.status" /></td>
            <td @click.stop class="whitespace-nowrap">
              <template v-if="a.status === 'Neu' || a.status === 'In Prüfung'">
                <button @click="annehmen(a)" class="btn btn-success btn-sm mr-1">
                  <Check :size="14" /> Annehmen
                </button>
                <button @click="openAblehnen(a)" class="btn btn-danger btn-sm">
                  <X :size="14" />
                </button>
              </template>
              <span v-else class="text-slate-400 text-xs">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Detail Modal -->
    <AppModal v-if="selected" :show="!!selected" :title="`Antrag von ${selected.vorname} ${selected.nachname}`" size="lg" @close="selected = null">
      <div class="space-y-3 text-sm">
        <div class="grid grid-cols-2 gap-4">
          <div><span class="text-slate-500">Typ:</span> <strong>{{ selected.gewuenschter_mitgliedstyp }}</strong></div>
          <div><span class="text-slate-500">Sparte:</span> {{ selected.sparte_wunsch || '—' }}</div>
          <div><span class="text-slate-500">Anrede:</span> {{ selected.anrede }}</div>
          <div><span class="text-slate-500">Geburtsdatum:</span> {{ formatDate(selected.geburtsdatum) }}</div>
          <div class="col-span-2"><span class="text-slate-500">Adresse:</span> {{ selected.strasse }}, {{ selected.plz }} {{ selected.ort }}</div>
          <div><span class="text-slate-500">E-Mail:</span> {{ selected.email }}</div>
          <div><span class="text-slate-500">Telefon:</span> {{ selected.telefon || selected.mobil || '—' }}</div>
        </div>
        <div v-if="selected.sepa_gewuenscht" class="p-3 bg-primary-50 rounded-lg">
          <p class="font-medium mb-1">SEPA gewünscht</p>
          <p>{{ selected.kontoinhaber }} · IBAN: {{ selected.iban }}</p>
        </div>
        <div class="flex gap-2 pt-2 border-t border-slate-100">
          <span class="badge" :class="selected.datenschutz_akzeptiert ? 'badge-green' : 'badge-red'">Datenschutz</span>
          <span class="badge" :class="selected.satzung_akzeptiert ? 'badge-green' : 'badge-red'">Satzung</span>
          <span class="badge" :class="selected.beitragsordnung_akzeptiert ? 'badge-green' : 'badge-red'">Beitragsordnung</span>
        </div>
      </div>
      <template #footer>
        <template v-if="selected.status === 'Neu' || selected.status === 'In Prüfung'">
          <button @click="openAblehnen(selected)" class="btn btn-danger">Ablehnen</button>
          <button @click="annehmen(selected)" class="btn btn-success">Annehmen & Mitglied erstellen</button>
        </template>
        <button @click="selected = null" class="btn btn-secondary">Schließen</button>
      </template>
    </AppModal>

    <!-- Ablehnen Modal -->
    <AppModal :show="showAblehnen" title="Antrag ablehnen" @close="showAblehnen = false">
      <div class="form-group">
        <label class="label">Ablehnungsgrund (optional)</label>
        <textarea v-model="ablehnungsGrund" class="input h-24 resize-none" placeholder="Wird intern gespeichert..." />
      </div>
      <template #footer>
        <button @click="showAblehnen = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="ablehnen" class="btn btn-danger">Ablehnen</button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppModal from '@/components/ui/AppModal.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { Check, X } from 'lucide-vue-next'
import { useRealtimeRefresh } from '@/composables/useRealtimeRefresh'

const antraege = ref([])
const loading = ref(true)
const filterStatus = ref('')
const selected = ref(null)
const showAblehnen = ref(false)
const ablehnungsGrund = ref('')
const toAblehnen = ref(null)

const statusFilters = [
  { label: 'Alle', value: '' },
  { label: 'Neu', value: 'Neu' },
  { label: 'In Prüfung', value: 'In Prüfung' },
  { label: 'Angenommen', value: 'Angenommen' },
  { label: 'Abgelehnt', value: 'Abgelehnt' },
]

onMounted(() => loadAntraege())
useRealtimeRefresh(['Mitgliedsantrag'], () => loadAntraege())

async function loadAntraege() {
  loading.value = true
  try {
    const filters = filterStatus.value ? { status: filterStatus.value } : {}
    const res = await api.getList('Mitgliedsantrag', {
      filters,
      fields: ['name', 'vorname', 'nachname', 'eingangsdatum', 'email',
               'gewuenschter_mitgliedstyp', 'sparte_wunsch', 'status',
               'strasse', 'plz', 'ort', 'telefon', 'mobil', 'anrede',
               'geburtsdatum', 'sepa_gewuenscht', 'kontoinhaber', 'iban',
               'datenschutz_akzeptiert', 'satzung_akzeptiert', 'beitragsordnung_akzeptiert'],
      order_by: 'eingangsdatum desc',
      limit_page_length: 50,
    })
    antraege.value = res || []
  } finally {
    loading.value = false
  }
}

async function annehmen(a) {
  if (!confirm(`Antrag von ${a.vorname} ${a.nachname} annehmen und Mitglied erstellen?`)) return
  try {
    await api.annehmenAntrag(a.name)
    selected.value = null
    await loadAntraege()
  } catch (e) { alert(e.message) }
}

function openAblehnen(a) {
  toAblehnen.value = a
  ablehnungsGrund.value = ''
  showAblehnen.value = true
}

async function ablehnen() {
  try {
    await api.ablehnenAntrag(toAblehnen.value.name, ablehnungsGrund.value)
    showAblehnen.value = false
    selected.value = null
    await loadAntraege()
  } catch (e) { alert(e.message) }
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE') : '—'
const formatDatetime = (d) => d ? new Date(d).toLocaleString('de-DE', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' }) : '—'
</script>
