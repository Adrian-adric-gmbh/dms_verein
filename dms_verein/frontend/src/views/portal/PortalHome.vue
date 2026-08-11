<template>
  <div>
    <div class="mb-6">
      <h2>Willkommen{{ profil ? ', ' + profil.vorname : '' }}!</h2>
      <p class="text-slate-500 mt-1">Ihr persönlicher Mitgliederbereich</p>
    </div>

    <AppSpinner v-if="loading" full-page />

    <template v-else-if="profil">
      <!-- Profil-Card -->
      <div class="card card-body flex items-center gap-4 mb-6">
        <div v-if="profil.foto" class="w-16 h-16 rounded-full overflow-hidden shrink-0 border-2 border-primary-200">
          <img :src="profil.foto" class="w-full h-full object-cover" />
        </div>
        <div v-else class="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center text-2xl font-bold text-primary-600 shrink-0">
          {{ profil.vorname?.[0] }}{{ profil.nachname?.[0] }}
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="text-xl">{{ profil.vorname }} {{ profil.nachname }}</h3>
          <p class="text-slate-500 text-sm">{{ profil.mitgliedsnummer }} · {{ profil.mitgliedstyp }}</p>
          <p class="text-slate-400 text-xs mt-0.5">Mitglied seit {{ formatDate(profil.eintrittsdatum) }}</p>
        </div>
        <span class="badge badge-green shrink-0">{{ profil.status }}</span>
      </div>

      <!-- Quick Links -->
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-6">
        <RouterLink to="/portal/profil" class="card card-body text-center hover:shadow-md transition-all">
          <User class="mx-auto mb-2 text-primary-600" :size="24" />
          <p class="text-sm font-medium">Profil bearbeiten</p>
        </RouterLink>
        <RouterLink to="/portal/beitraege" class="card card-body text-center hover:shadow-md transition-all">
          <CreditCard class="mx-auto mb-2 text-emerald-600" :size="24" />
          <p class="text-sm font-medium">Meine Beiträge</p>
        </RouterLink>
        <RouterLink to="/portal/kalender" class="card card-body text-center hover:shadow-md transition-all">
          <Calendar class="mx-auto mb-2 text-purple-600" :size="24" />
          <p class="text-sm font-medium">Veranstaltungen</p>
        </RouterLink>
        <RouterLink to="/portal/alben" class="card card-body text-center hover:shadow-md transition-all">
          <Image class="mx-auto mb-2 text-amber-600" :size="24" />
          <p class="text-sm font-medium">Fotoalben</p>
        </RouterLink>
        <RouterLink to="/portal/abstimmungen" class="card card-body text-center hover:shadow-md transition-all relative">
          <Vote class="mx-auto mb-2 text-blue-600" :size="24" />
          <p class="text-sm font-medium">Abstimmungen</p>
          <span v-if="offeneAbstimmungen > 0"
            class="absolute top-2 right-2 w-5 h-5 rounded-full bg-blue-600 text-white text-[10px] font-bold flex items-center justify-center">
            {{ offeneAbstimmungen }}
          </span>
        </RouterLink>
      </div>

      <!-- Sparten -->
      <div class="mb-2 flex items-center justify-between">
        <h3 class="text-base font-semibold">Sparten</h3>
        <span class="text-xs text-slate-400">{{ sparten.length }} Sparte{{ sparten.length !== 1 ? 'n' : '' }}</span>
      </div>
      <div v-if="spartenLoading" class="flex justify-center py-8">
        <AppSpinner />
      </div>
      <div v-else-if="sparten.length" class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
        <RouterLink
          v-for="s in sparten" :key="s.name"
          :to="`/portal/sparten/${s.name}`"
          class="card card-body hover:shadow-md transition-all flex items-start gap-3 relative"
        >
          <!-- Icon / Farb-Dot -->
          <div class="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center text-xl"
            :style="s.farbe ? `background:${s.farbe}22; color:${s.farbe}` : 'background:#f1f5f9'">
            {{ s.icon || '🏅' }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-sm text-slate-900 leading-snug">{{ s.name_sparte }}</p>
            <p v-if="s.beschreibung" class="text-xs text-slate-400 mt-0.5 line-clamp-2">{{ s.beschreibung }}</p>
          </div>
          <!-- Mitglied-Badge wenn zugehörig -->
          <span v-if="meineSpartenSet.has(s.name)" class="absolute top-2 right-2 badge badge-blue text-[10px]">
            {{ meineFunktion(s.name) }}
          </span>
          <ChevronRight :size="14" class="text-slate-300 shrink-0 self-center" />
        </RouterLink>
      </div>
      <div v-else class="card card-body text-center text-slate-400 mb-6">
        Keine Sparten vorhanden.
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import { RouterLink } from 'vue-router'
import { User, CreditCard, Calendar, Image, Vote, ChevronRight } from 'lucide-vue-next'

const profil = ref(null)
const loading = ref(true)
const sparten = ref([])
const spartenLoading = ref(true)
const offeneAbstimmungen = ref(0)

const meineSpartenSet = computed(() => {
  const set = new Set()
  for (const s of profil.value?.sparten || []) set.add(s.sparte)
  return set
})

function meineFunktion(sparteName) {
  const row = (profil.value?.sparten || []).find(s => s.sparte === sparteName)
  return row?.funktion || 'Mitglied'
}

onMounted(async () => {
  try { profil.value = await api.getMeinProfil() }
  finally { loading.value = false }

  try {
    const result = await api.call('dms_verein.api.verein.get_sparten').catch(() => [])
    sparten.value = result || []
  } finally { spartenLoading.value = false }

  try {
    const abs = await api.call('dms_verein.api.verein.get_meine_abstimmungen').catch(() => [])
    offeneAbstimmungen.value = (abs || []).filter(a => a.status === 'Aktiv' && !a.bereits_abgestimmt).length
  } catch {}
})

const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE') : '—'
</script>
