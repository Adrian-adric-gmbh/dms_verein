<template>
  <div>
    <div class="mb-6">
      <h2>Meine Beiträge</h2>
      <p class="text-slate-500 mt-1">Übersicht Ihrer Beitragsrechnungen</p>
    </div>

    <AppSpinner v-if="loading" full-page />
    <template v-else>
      <div v-if="!rechnungen.length" class="card card-body text-center py-12 text-slate-400">
        Keine Beitragsrechnungen vorhanden.
      </div>
      <template v-else>
        <!-- Mobile/Tablet Cards (< lg) -->
        <div class="lg:hidden space-y-3">
          <div v-for="r in rechnungen" :key="r.name" class="card p-4 flex items-start justify-between gap-3">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-bold text-slate-900">{{ r.jahr }}</span>
                <StatusBadge :status="r.status" />
              </div>
              <p class="text-sm text-slate-500">{{ r.mitgliedstyp }}</p>
              <p class="text-xs text-slate-400 mt-0.5">Fälligkeit: {{ formatDate(r.faelligkeit) }}</p>
            </div>
            <span class="text-base font-bold text-slate-900 shrink-0">{{ formatCurrency(r.betrag) }}</span>
          </div>
        </div>
        <!-- Desktop Tabelle (≥ lg) -->
        <div class="hidden lg:block table-wrapper">
          <table class="table">
            <thead>
              <tr><th>Jahr</th><th>Mitgliedstyp</th><th>Betrag</th><th>Fälligkeit</th><th>Status</th></tr>
            </thead>
            <tbody>
              <tr v-for="r in rechnungen" :key="r.name">
                <td class="font-medium">{{ r.jahr }}</td>
                <td>{{ r.mitgliedstyp }}</td>
                <td class="font-medium">{{ formatCurrency(r.betrag) }}</td>
                <td>{{ formatDate(r.faelligkeit) }}</td>
                <td><StatusBadge :status="r.status" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const rechnungen = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const profil = await api.getMeinProfil()
    rechnungen.value = profil?.beitragsrechnungen || []
  } finally { loading.value = false }
})

const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE') : '—'
const formatCurrency = (v) => v ? `${Number(v).toFixed(2).replace('.', ',')} €` : '—'
</script>
