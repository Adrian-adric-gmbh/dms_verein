<template>
  <div>
    <div class="mb-6"><h2>Finanzen & Beiträge</h2><p class="text-slate-500 mt-1">Beitragsrechnungen und SEPA-Mandate</p></div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <div class="card card-body">
        <h3 class="text-base font-semibold mb-4">Beitragsrechnungen generieren</h3>
        <p class="text-sm text-slate-500 mb-4">Erzeugt für alle aktiven Mitglieder eine Beitragsrechnung für das gewählte Jahr.</p>
        <div class="flex gap-3">
          <select v-model="beitragsjahr" class="input w-32">
            <option v-for="y in jahre" :key="y" :value="y">{{ y }}</option>
          </select>
          <button @click="generiereRechnungen" :disabled="generieren" class="btn btn-primary">
            {{ generieren ? 'Wird generiert...' : 'Rechnungen generieren' }}
          </button>
        </div>
        <AppAlert v-if="genMsg" :type="genMsg.type" :message="genMsg.text" class="mt-4" />
      </div>
      <div class="card card-body">
        <h3 class="text-base font-semibold mb-4">SEPA-Sammelexport</h3>
        <p class="text-sm text-slate-500 mb-4">Exportiert alle offenen Lastschriften als SEPA XML (pain.008) für den Bankeinzug.</p>
        <button @click="sepaExport" class="btn btn-secondary">SEPA XML exportieren</button>
      </div>
    </div>
    <div class="card">
      <div class="card-header"><h3 class="text-base font-semibold">SEPA-Mandate</h3></div>
      <AppSpinner v-if="loading" class="p-6" />
      <div v-else class="table-wrapper">
        <table class="table">
          <thead><tr><th>Referenz</th><th>Mitglied</th><th>IBAN</th><th>Erteilt am</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-if="!mandate.length"><td colspan="5" class="text-center py-8 text-slate-400">Keine SEPA-Mandate</td></tr>
            <tr v-for="m in mandate" :key="m.name">
              <td class="font-mono text-sm">{{ m.name }}</td>
              <td>{{ m.mitglied }}</td>
              <td class="font-mono text-sm">{{ m.iban ? m.iban.slice(0,4) + ' **** ' + m.iban.slice(-4) : '—' }}</td>
              <td class="text-sm">{{ formatDate(m.erteilungsdatum) }}</td>
              <td><StatusBadge :status="m.status" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const mandate = ref([])
const loading = ref(true)
const generieren = ref(false)
const genMsg = ref(null)
const currentYear = new Date().getFullYear()
const beitragsjahr = ref(currentYear)
const jahre = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i)

onMounted(() => load())
async function load() {
  loading.value = true
  try { mandate.value = await api.getList('SEPA Mandat', { fields: ['name','mitglied','iban','erteilungsdatum','status'], order_by: 'erteilungsdatum desc', limit_page_length: 100 }) || [] }
  finally { loading.value = false }
}

async function generiereRechnungen() {
  if (!confirm(`Beitragsrechnungen für ${beitragsjahr.value} generieren?`)) return
  generieren.value = true; genMsg.value = null
  try {
    await api.call('dms_verein.api.verein.generiere_beitragsrechnungen', { jahr: beitragsjahr.value })
    genMsg.value = { type: 'success', text: `Rechnungen für ${beitragsjahr.value} wurden erstellt.` }
  } catch (e) { genMsg.value = { type: 'error', text: e.message } }
  finally { generieren.value = false }
}

function sepaExport() { alert('SEPA XML Export — wird in Phase 3 implementiert.') }
const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE') : '—'
</script>
