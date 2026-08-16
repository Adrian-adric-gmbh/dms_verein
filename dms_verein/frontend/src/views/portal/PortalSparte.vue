<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <RouterLink to="/portal" class="text-slate-400 hover:text-slate-600 transition-colors">
        <ArrowLeft :size="20" />
      </RouterLink>
      <div>
        <h2 class="flex items-center gap-2">
          <span v-if="sparte?.icon" class="text-2xl">{{ sparte.icon }}</span>
          {{ sparte?.name_sparte || verein.strukturSingular }}
        </h2>
        <p class="text-slate-500 text-sm mt-0.5">Interner Terminkalender</p>
      </div>
    </div>

    <AppSpinner v-if="loading" full-page />
    <div v-else>
      <!-- Leitung -->
      <div v-if="leitung.length" class="card card-body mb-4">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">{{ verein.strukturLeitung }}</p>
        <div class="flex flex-wrap gap-2">
          <span v-for="l in leitung" :key="l.mitglied"
            class="inline-flex items-center gap-1.5 bg-slate-100 rounded-full px-3 py-1 text-xs font-medium">
            <span class="w-5 h-5 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-[10px] font-bold shrink-0">
              {{ (l.nachname || '?')[0].toUpperCase() }}
            </span>
            {{ l.nachname }}, {{ l.vorname }}
            <span class="text-slate-400">· {{ l.funktion }}</span>
          </span>
        </div>
      </div>

      <!-- Termine -->
      <div class="card">
        <div class="card-header flex items-center justify-between">
          <h3 class="text-base font-semibold">Kommende Termine</h3>
          <span v-if="termine.length" class="text-sm text-slate-400">{{ termine.length }} Termin(e)</span>
        </div>

        <div v-if="!termine.length" class="card-body text-center py-10 text-slate-400">
          Keine Termine eingetragen.
        </div>
        <div v-else class="divide-y divide-slate-100">
          <div v-for="(t, idx) in termine" :key="`${t.name}-${idx}`"
            class="px-4 py-3 flex items-start gap-4">
            <!-- Datum-Box -->
            <div class="shrink-0 w-12 text-center">
              <div class="text-xl font-bold leading-none" style="color: var(--color-primary)">
                {{ new Date(t.datum).getDate() }}
              </div>
              <div class="text-xs font-medium text-slate-400">{{ monthShort(t.datum) }}</div>
              <div class="text-[10px] text-slate-300">{{ new Date(t.datum).getFullYear() }}</div>
            </div>
            <!-- Inhalt -->
            <div class="flex-1 min-w-0">
              <p class="font-medium text-sm text-slate-900">{{ t.titel }}</p>
              <div class="flex flex-wrap gap-x-3 gap-y-0.5 mt-1">
                <span v-if="t.uhrzeit_von" class="text-xs text-slate-500 flex items-center gap-1">
                  <Clock :size="11" /> {{ t.uhrzeit_von.slice(0,5) }}{{ t.uhrzeit_bis ? ` – ${t.uhrzeit_bis.slice(0,5)}` : '' }} Uhr
                </span>
                <span v-if="t.treffpunkt" class="text-xs text-slate-500 flex items-center gap-1">
                  <MapPin :size="11" /> {{ t.treffpunkt }}
                </span>
              </div>
              <p v-if="t.beschreibung" class="text-xs text-slate-400 mt-1 leading-snug">{{ t.beschreibung }}</p>
              <div class="flex gap-1 mt-1.5 flex-wrap">
                <span v-if="t.wiederholung && t.wiederholung !== 'Keine'" class="badge badge-blue text-[10px]">
                  🔄 {{ t.wiederholung }}
                </span>
                <span v-if="t.ist_wiederholung" class="badge badge-gray text-[10px]">Serienterm.</span>
              </div>
            </div>
            <!-- Wochentag -->
            <div class="shrink-0 text-xs text-slate-400 text-right">
              {{ wochentag(t.datum) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { RouterLink } from 'vue-router'
import { api } from '@/utils/api'
import { useVereinStore } from '@/stores/verein'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import { ArrowLeft, Clock, MapPin } from 'lucide-vue-next'

const route = useRoute()
const verein = useVereinStore()
const sparteName = route.params.name

const loading  = ref(true)
const sparte   = ref(null)
const termine  = ref([])
const leitung  = ref([])

onMounted(async () => {
  try {
    const [sp, tm, ml] = await Promise.all([
      api.call('frappe.client.get', { doctype: 'Sparte', name: sparteName })
        .catch(() => null),
      api.call('dms_verein.api.verein.get_sparten_termine', { sparte_name: sparteName })
        .catch(() => []),
      api.call('dms_verein.api.verein.get_sparte_mitglieder', { sparte_name: sparteName })
        .catch(() => []),
    ])
    sparte.value  = sp
    termine.value = tm || []
    leitung.value = (ml || []).filter(m => m.aktiv &&
      (m.funktion === 'Spartenleiter' || m.funktion === 'Stv. Spartenleiter'))
  } finally { loading.value = false }
})

const monthShort = (d) => new Date(d).toLocaleDateString('de-DE', { month: 'short' })
const wochentag  = (d) => new Date(d).toLocaleDateString('de-DE', { weekday: 'short' })
</script>
