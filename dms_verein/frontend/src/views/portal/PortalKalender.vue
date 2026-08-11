<template>
  <div>
    <div class="mb-6"><h2>Veranstaltungen</h2><p class="text-slate-500 mt-1">Nächste Events des Vereins</p></div>

    <!-- Meine Anmeldungen -->
    <div v-if="meineAnmeldungen.length || listError" class="mb-6">
      <h3 class="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
        <CheckCircle :size="15" class="text-green-500" /> Meine Anmeldungen
      </h3>
      <AppAlert v-if="listError" type="error" :message="listError" class="mb-2" />
      <div class="space-y-2">
        <div v-for="a in meineAnmeldungen" :key="a.name"
          class="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-xl text-sm">
          <div class="flex-1 min-w-0">
            <span class="font-medium">{{ a.titel }}</span>
            <span class="text-slate-500 ml-2">{{ formatDate(a.datum_von) }}</span>
          </div>
          <span :class="['badge text-xs', a.anmeldung_status === 'Warteliste' ? 'badge-amber' : 'badge-green']">{{ a.anmeldung_status }}</span>
          <button @click="openAbmeldenConfirm(a.veranstaltung)"
            class="text-xs text-red-500 hover:text-red-700 hover:underline shrink-0">Abmelden</button>
        </div>
      </div>
    </div>

    <AppSpinner v-if="loading" full-page />
    <div v-else class="space-y-3">
      <div v-if="!events.length" class="card card-body text-center py-12 text-slate-400">Keine bevorstehenden Veranstaltungen.</div>
      <div v-for="ev in events" :key="ev.name"
        class="card hover:shadow-md transition-all cursor-pointer active:scale-[0.99]"
        @click="openDetail(ev)">
        <div class="p-4">
          <div class="flex items-start gap-3 mb-2">
            <!-- Datum-Box -->
            <div class="w-14 h-14 rounded-xl flex flex-col items-center justify-center shrink-0"
              style="background: color-mix(in srgb, var(--color-primary) 12%, transparent)">
              <span class="text-2xl font-bold leading-none" style="color: var(--color-primary)">
                {{ new Date(ev.datum_von).getDate() }}
              </span>
              <span class="text-xs font-medium uppercase opacity-70" style="color: var(--color-primary)">
                {{ monthShort(ev.datum_von) }}
              </span>
            </div>
            <!-- Inhalt -->
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-base leading-snug text-slate-900 mb-1">{{ ev.titel }}</p>
              <p class="text-sm text-slate-500 truncate">{{ ev.veranstaltungsort || 'Ort wird bekannt gegeben' }}</p>
              <!-- Badges + Infos -->
              <div class="flex flex-wrap gap-1.5 mt-2">
                <span v-if="ev.uhrzeit_von" class="text-xs text-slate-400">🕐 {{ ev.uhrzeit_von.slice(0,5) }} Uhr</span>
                <span v-if="ev.kosten_mitglieder > 0" class="text-xs text-slate-400">💶 {{ formatBetrag(ev.kosten_mitglieder) }}</span>
                <span v-if="isAngemeldet(ev.name)" class="badge badge-green text-xs">✓ Angemeldet</span>
                <span v-if="ev.kategorie" class="badge badge-blue text-xs">{{ ev.kategorie }}</span>
                <span v-if="!isAngemeldet(ev.name) && ev.anmeldung_erforderlich" class="badge badge-amber text-xs">Anmeldung nötig</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Bottom Sheet: Event Detail ─── -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        leave-active-class="transition-all duration-200 ease-in">
        <!-- Backdrop -->
        <div v-if="selected" class="fixed inset-0 z-40 flex flex-col justify-end md:justify-center md:items-center md:p-6"
             @click.self="closeDetail">
          <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="closeDetail" />
          <!-- Sheet -->
          <Transition
            enter-active-class="transition-transform duration-300 ease-out"
            enter-from-class="translate-y-full md:translate-y-0 md:scale-95 md:opacity-0"
            enter-to-class="translate-y-0 md:scale-100 md:opacity-100"
            leave-active-class="transition-transform duration-200 ease-in"
            leave-from-class="translate-y-0 md:scale-100 md:opacity-100"
            leave-to-class="translate-y-full md:translate-y-0 md:scale-95 md:opacity-0"
            appear>
            <div v-if="selected"
              class="relative bg-white rounded-t-3xl md:rounded-2xl w-full md:max-w-xl
                     max-h-[92vh] md:max-h-[85vh] flex flex-col shadow-2xl z-10">
              <!-- Handle Bar (nur Smartphone) -->
              <div class="md:hidden flex justify-center pt-3 pb-1 shrink-0">
                <div class="w-10 h-1 rounded-full bg-slate-300" />
              </div>
              <!-- Header -->
              <div class="flex items-start gap-3 px-5 pt-3 pb-4 border-b border-slate-100 shrink-0">
                <div class="flex-1 min-w-0">
                  <div class="flex flex-wrap items-center gap-2 mb-1">
                    <span v-if="selected.kategorie" class="badge badge-blue text-xs">{{ selected.kategorie }}</span>
                  </div>
                  <h2 class="text-xl font-bold text-slate-900 leading-snug">{{ selected.titel }}</h2>
                </div>
                <button @click="closeDetail"
                  class="shrink-0 w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center transition-colors">
                  <X :size="16" class="text-slate-500" />
                </button>
              </div>
              <!-- Content -->
              <div class="flex-1 overflow-y-auto px-5 py-4 space-y-4">
                <img v-if="selected.bild" :src="selected.bild" class="w-full h-44 object-cover rounded-xl" />
                <!-- Infos -->
                <div class="grid grid-cols-2 gap-3 text-sm">
                  <div class="flex items-center gap-2 text-slate-600">
                    <Calendar :size="15" class="text-slate-400 shrink-0" />
                    <span>{{ formatDateLong(selected.datum_von) }}</span>
                  </div>
                  <div v-if="selected.uhrzeit_von" class="flex items-center gap-2 text-slate-600">
                    <Clock :size="15" class="text-slate-400 shrink-0" />
                    <span>{{ selected.uhrzeit_von?.slice(0,5) }} Uhr</span>
                  </div>
                  <div class="col-span-2 flex items-center gap-2 text-slate-600">
                    <MapPin :size="15" class="text-slate-400 shrink-0" />
                    <span>{{ selected.veranstaltungsort || 'Ort wird bekannt gegeben' }}</span>
                  </div>
                  <div v-if="selected.kosten_mitglieder > 0" class="flex items-center gap-2 text-slate-600">
                    <Euro :size="15" class="text-slate-400 shrink-0" />
                    <span>{{ formatBetrag(selected.kosten_mitglieder) }} (Mitglieder)</span>
                  </div>
                  <div v-if="selected.anmeldeschluss" class="flex items-center gap-2 text-slate-600">
                    <AlarmClock :size="15" class="text-slate-400 shrink-0" />
                    <span>Anmeldeschluss: {{ formatDate(selected.anmeldeschluss) }}</span>
                  </div>
                  <div v-if="selected.max_teilnehmer" class="flex items-center gap-2 text-slate-600">
                    <Users :size="15" class="text-slate-400 shrink-0" />
                    <span>Max. {{ selected.max_teilnehmer }} Teilnehmer</span>
                  </div>
                </div>
                <MapCard
                  v-if="selected.adresse || selected.veranstaltungsort"
                  :address="selected.adresse || selected.veranstaltungsort"
                  :maps-key="verein.info?.google_maps_key"
                />
                <div v-if="selected.beschreibung"
                  class="text-sm text-slate-700 border-t border-slate-100 pt-4 prose prose-sm max-w-none"
                  v-html="selected.beschreibung" />
                <AppAlert v-if="actionMsg" :type="actionMsg.type" :message="actionMsg.text" />
              </div>
              <!-- Footer: Anmeldung -->
              <div v-if="selected.anmeldung_erforderlich" class="px-5 py-4 border-t border-slate-100 shrink-0"
                   style="padding-bottom: max(1rem, env(safe-area-inset-bottom))">
                <div v-if="isAngemeldet(selected.name)"
                  class="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-xl">
                  <CheckCircle :size="16" class="text-green-500 shrink-0" />
                  <div class="flex-1">
                    <div class="font-medium text-green-800 text-sm">Du bist angemeldet</div>
                    <div v-if="meineAnmeldungen.find(a => a.veranstaltung === selected.name)?.anmeldung_status === 'Warteliste'"
                      class="text-xs text-amber-600">Warteliste</div>
                  </div>
                  <button @click="openAbmeldenConfirm(selected.name)"
                    :disabled="actionLoading === selected.name"
                    class="btn btn-secondary btn-sm text-red-600 hover:bg-red-50 shrink-0">Abmelden</button>
                </div>
                <button v-else @click="anmelden(selected.name)" :disabled="actionLoading === selected.name"
                  class="w-full btn btn-primary flex items-center justify-center gap-2 py-3">
                  <CalendarCheck :size="17" />
                  {{ actionLoading === selected.name ? 'Wird angemeldet...' : 'Jetzt anmelden' }}
                </button>
              </div>
              <div v-else class="px-5 py-3 shrink-0" style="padding-bottom: max(0.75rem, env(safe-area-inset-bottom))" />
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <!-- ─── Abmelden Bestätigung Modal ─── -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        leave-active-class="transition-all duration-150 ease-in">
        <div v-if="abmeldenTarget" class="fixed inset-0 z-50 flex items-end lg:items-center justify-center p-4 lg:p-6"
             @click.self="abmeldenTarget = null">
          <div class="absolute inset-0 bg-black/50" @click="abmeldenTarget = null" />
          <div class="relative bg-white rounded-2xl w-full max-w-sm shadow-2xl p-6 space-y-4 z-10">
            <h3 class="font-bold text-lg text-slate-900">Abmelden?</h3>
            <p class="text-sm text-slate-600">Anmeldung wirklich stornieren?</p>
            <div class="flex gap-3 pt-2">
              <button @click="abmeldenTarget = null" class="btn btn-secondary flex-1">Abbrechen</button>
              <button @click="abmeldenBestaetigen" :disabled="actionLoading === abmeldenTarget"
                class="btn btn-danger flex-1">
                {{ actionLoading === abmeldenTarget ? 'Wird abgemeldet...' : 'Ja, abmelden' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import MapCard from '@/components/ui/MapCard.vue'
import { CheckCircle, CalendarCheck, X, Calendar, Clock, MapPin, Euro, AlarmClock, Users } from 'lucide-vue-next'
import { useRealtimeRefresh } from '@/composables/useRealtimeRefresh'
import { useVereinStore } from '@/stores/verein'

const verein = useVereinStore()

const events = ref([])
const loading = ref(true)
const selected = ref(null)
const meineAnmeldungen = ref([])
const actionLoading = ref(null)
const actionMsg = ref(null)
const abmeldenTarget = ref(null)
const listError = ref('')  // Fehler für Abmelden aus der Schnellliste

async function loadKalender() {
  try {
    const [ev, anm] = await Promise.all([
      api.getVeranstaltungen({ limit: 30 }),
      api.call('dms_verein.api.verein.get_meine_anmeldungen').catch(() => []),
    ])
    events.value = ev || []
    meineAnmeldungen.value = anm || []
  } catch {}
}

onMounted(async () => {
  try { await loadKalender() } finally { loading.value = false }
})
useRealtimeRefresh(['Veranstaltung'], () => loadKalender())

function isAngemeldet(name) {
  // Backend filtert bereits status != "Abgesagt", daher reicht Vorhandensein
  return meineAnmeldungen.value.some(a => a.veranstaltung === name)
}

function openDetail(ev) { selected.value = ev; actionMsg.value = null }
function closeDetail() { selected.value = null; actionMsg.value = null }

async function anmelden(name) {
  actionLoading.value = name; actionMsg.value = null
  try {
    const r = await api.call('dms_verein.api.verein.anmelden_veranstaltung', { veranstaltung_name: name })
    meineAnmeldungen.value.push({
      veranstaltung: name, anmeldung_status: r.status,
      titel: selected.value?.titel, datum_von: selected.value?.datum_von
    })
    actionMsg.value = {
      type: 'success',
      text: r.status === 'Warteliste' ? 'Du wurdest auf die Warteliste gesetzt.' : 'Erfolgreich angemeldet!'
    }
  } catch (e) { actionMsg.value = { type: 'error', text: e.message } }
  finally { actionLoading.value = null }
}

function openAbmeldenConfirm(veranstaltungName) {
  abmeldenTarget.value = veranstaltungName
}

async function abmeldenBestaetigen() {
  const name = abmeldenTarget.value
  if (!name) return
  actionLoading.value = name
  try {
    await api.call('dms_verein.api.verein.abmelden_veranstaltung', { veranstaltung_name: name })
    meineAnmeldungen.value = meineAnmeldungen.value.filter(a => a.veranstaltung !== name)
    abmeldenTarget.value = null
    if (selected.value?.name === name) {
      actionMsg.value = { type: 'success', text: 'Anmeldung storniert.' }
    }
  } catch (e) {
    if (selected.value?.name === name) {
      actionMsg.value = { type: 'error', text: e.message }
    } else {
      listError.value = e.message
      setTimeout(() => { listError.value = '' }, 5000)
    }
    abmeldenTarget.value = null
  } finally { actionLoading.value = null }
}

const monthShort = (d) => new Date(d).toLocaleDateString('de-DE', { month: 'short' })
const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE') : '—'
const formatDateLong = (d) => d ? new Date(d).toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long' }) : '—'
const formatBetrag = (v) => Number(v || 0).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
</script>
