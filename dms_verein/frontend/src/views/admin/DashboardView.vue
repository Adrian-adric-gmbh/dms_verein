<template>
  <div>
    <div class="mb-6">
      <h2>Dashboard</h2>
      <p class="text-slate-500 mt-1">Willkommen in der Vereinsverwaltung</p>
    </div>

    <AppSpinner v-if="loading" full-page />

    <template v-else>
      <!-- Stat Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="stat-card">
          <div class="flex items-center justify-between">
            <p class="stat-label">Mitglieder gesamt</p>
            <div class="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
              <Users :size="20" class="text-primary-600" />
            </div>
          </div>
          <p class="stat-value">{{ stats.total_mitglieder ?? '—' }}</p>
        </div>
        <div class="stat-card">
          <div class="flex items-center justify-between">
            <p class="stat-label">Aktive Mitglieder</p>
            <div class="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
              <UserCheck :size="20" class="text-emerald-600" />
            </div>
          </div>
          <p class="stat-value text-emerald-700">{{ stats.aktive_mitglieder ?? '—' }}</p>
        </div>
        <div class="stat-card">
          <div class="flex items-center justify-between">
            <p class="stat-label">Offene Anträge</p>
            <div class="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
              <FileText :size="20" class="text-amber-600" />
            </div>
          </div>
          <p class="stat-value text-amber-700">{{ stats.neue_antraege ?? '—' }}</p>
        </div>
        <div class="stat-card">
          <div class="flex items-center justify-between">
            <p class="stat-label">Nächste Events</p>
            <div class="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center">
              <Calendar :size="20" class="text-purple-600" />
            </div>
          </div>
          <p class="stat-value text-purple-700">{{ stats.naechste_veranstaltungen?.length ?? '—' }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Mitglieder pro Typ -->
        <div class="card">
          <div class="card-header flex items-center gap-2">
            <PieChart :size="18" class="text-slate-400" />
            <h3 class="text-base font-semibold">Mitglieder nach Typ</h3>
          </div>
          <div class="card-body">
            <div v-if="!stats.mitglieder_pro_typ?.length" class="text-slate-400 text-sm text-center py-4">Keine Daten</div>
            <div v-else class="space-y-3">
              <div v-for="typ in stats.mitglieder_pro_typ" :key="typ.bezeichnung"
                   class="flex items-center gap-3">
                <div class="flex-1">
                  <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium">{{ typ.bezeichnung }}</span>
                    <span class="text-slate-500">{{ typ.anzahl }}</span>
                  </div>
                  <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div class="h-full bg-primary-500 rounded-full transition-all"
                         :style="{ width: `${(typ.anzahl / stats.total_mitglieder * 100).toFixed(0)}%` }" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Nächste Veranstaltungen -->
        <div class="card">
          <div class="card-header flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Calendar :size="18" class="text-slate-400" />
              <h3 class="text-base font-semibold">Nächste Veranstaltungen</h3>
            </div>
            <RouterLink to="/admin/veranstaltungen" class="text-sm text-primary-600 hover:underline">Alle</RouterLink>
          </div>
          <div class="divide-y divide-slate-100">
            <div v-if="!stats.naechste_veranstaltungen?.length" class="p-6 text-slate-400 text-sm text-center">
              Keine bevorstehenden Veranstaltungen
            </div>
            <div v-for="ev in stats.naechste_veranstaltungen" :key="ev.name"
                 class="px-6 py-3 flex items-center gap-4">
              <div class="w-12 text-center shrink-0">
                <div class="text-lg font-bold text-primary-600 leading-none">{{ new Date(ev.datum_von).getDate() }}</div>
                <div class="text-xs text-slate-400 uppercase">{{ monthShort(ev.datum_von) }}</div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-sm truncate">{{ ev.titel }}</p>
                <p v-if="ev.veranstaltungsort" class="text-xs text-slate-400 truncate">{{ ev.veranstaltungsort }}</p>
              </div>
              <span v-if="ev.uhrzeit_von" class="text-xs text-slate-500 shrink-0">{{ ev.uhrzeit_von?.slice(0,5) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="mt-6 card card-body">
        <h3 class="text-base font-semibold mb-4">Schnellaktionen</h3>
        <div class="flex flex-wrap gap-3">
          <RouterLink to="/admin/antraege" class="btn btn-secondary">
            <FileText :size="16" /> Anträge bearbeiten
          </RouterLink>
          <RouterLink to="/admin/mitglieder" class="btn btn-secondary">
            <Users :size="16" /> Mitglieder verwalten
          </RouterLink>
          <RouterLink to="/admin/veranstaltungen" class="btn btn-secondary">
            <Calendar :size="16" /> Veranstaltung anlegen
          </RouterLink>
          <RouterLink to="/admin/konfiguration" class="btn btn-secondary">
            <Settings :size="16" /> Vereinseinstellungen
          </RouterLink>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import { Users, UserCheck, FileText, Calendar, PieChart, Settings } from 'lucide-vue-next'
import { useRealtimeRefresh } from '@/composables/useRealtimeRefresh'

const stats = ref({})
const loading = ref(true)

async function loadStats() {
  try { stats.value = await api.getDashboardStats() } catch {}
}

onMounted(async () => {
  try {
    stats.value = await api.getDashboardStats()
  } finally {
    loading.value = false
  }
})
useRealtimeRefresh([], () => loadStats())

const monthShort = (d) => new Date(d).toLocaleDateString('de-DE', { month: 'short' })
</script>
