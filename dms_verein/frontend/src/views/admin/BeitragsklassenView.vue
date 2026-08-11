<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2>Beitragsklassen</h2>
        <p class="text-slate-500 mt-1">Mitgliedsbeiträge, Tarife und Altersgruppen verwalten</p>
      </div>
      <div class="flex gap-2">
        <button @click="autoZuweisen" :disabled="autoRunning"
          class="btn btn-secondary text-sm flex items-center gap-1.5">
          <RefreshCw :size="14" :class="autoRunning ? 'animate-spin' : ''" />
          Altersbasiert zuweisen
        </button>
        <button @click="openCreate" class="btn btn-primary"><Plus :size="16" /> Neue Klasse</button>
      </div>
    </div>

    <AppAlert v-if="autoMsg" :type="autoMsg.type" :message="autoMsg.text" class="mb-4" @close="autoMsg=null" />

    <!-- Info-Banner -->
    <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 text-sm text-blue-800 flex items-start gap-3">
      <Info :size="16" class="shrink-0 mt-0.5 text-blue-500" />
      <div>
        <strong>Tipp:</strong> Beitragsklassen entsprechen den Mitgliedstypen. Jedes Mitglied bekommt genau eine Klasse zugewiesen.
        Über „Altersbasiert zuweisen" werden alle aktiven Mitglieder automatisch der passenden Klasse zugeteilt (anhand Geburtstag + Altersregeln).
      </div>
    </div>

    <AppSpinner v-if="loading" full-page />

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-if="!klassen.length" class="col-span-full card card-body text-center py-12 text-slate-400">
        Keine Beitragsklassen vorhanden.
      </div>

      <div v-for="k in klassen" :key="k.name"
        :class="['card hover:shadow-md transition-shadow cursor-pointer', k.ist_standardklasse ? 'ring-2 ring-primary-300' : '']"
        @click="openEdit(k)">
        <div class="card-body">
          <div class="flex items-start justify-between gap-2 mb-3">
            <div class="flex items-center gap-2">
              <div v-if="k.farbe" class="w-3 h-3 rounded-full shrink-0" :style="{backgroundColor: k.farbe}" />
              <h3 class="text-base font-semibold">{{ k.bezeichnung }}</h3>
            </div>
            <div class="flex gap-1 shrink-0">
              <span v-if="k.ist_standardklasse" class="badge badge-blue text-xs">Standard</span>
              <span :class="k.aktiv ? 'badge-green' : 'badge-gray'" class="badge">
                {{ k.aktiv ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </div>
          </div>

          <div class="text-2xl font-bold text-primary-700 mb-1">
            {{ formatBetrag(k.beitragsbetrag) }}
            <span class="text-sm font-normal text-slate-500">/ {{ k.zahlungsintervall || 'Jährlich' }}</span>
          </div>

          <div class="text-xs text-slate-500 space-y-0.5 mt-2">
            <div v-if="k.min_alter || k.max_alter" class="flex items-center gap-1">
              <Users :size="11" />
              Alter: {{ k.min_alter ? k.min_alter + ' J.' : '—' }} bis {{ k.max_alter ? k.max_alter + ' J.' : 'unbegrenzt' }}
            </div>
            <div v-else-if="k.ist_standardklasse" class="flex items-center gap-1 text-primary-600">
              <Users :size="11" /> Fallback: alle ohne Altersregel
            </div>
            <div v-else class="flex items-center gap-1 text-slate-400"><Users :size="11" /> Kein Altersfilter</div>
            <div v-if="k.stimmberechtigt" class="flex items-center gap-1 text-green-600">
              <CheckCircle :size="11" /> Stimmberechtigt
            </div>
          </div>

          <p v-if="k.beschreibung" class="text-xs text-slate-400 mt-2 line-clamp-2">{{ k.beschreibung }}</p>
        </div>
      </div>

      <button @click="openCreate"
        class="card border-dashed border-2 border-slate-300 hover:border-primary-400 hover:bg-primary-50 transition-all flex items-center justify-center gap-2 text-slate-400 hover:text-primary-600 p-8 rounded-xl">
        <Plus :size="20" /> Klasse hinzufügen
      </button>
    </div>

    <!-- Formular-Modal -->
    <AppModal :show="showForm" :title="editTarget ? 'Beitragsklasse bearbeiten' : 'Neue Beitragsklasse'" size="md" @close="showForm=false">
      <form @submit.prevent="save" class="space-y-4">
        <AppAlert v-if="formError" type="error" :message="formError" />

        <div class="form-group">
          <label class="label">Bezeichnung *</label>
          <input v-model="form.bezeichnung" class="input" placeholder="z.B. Erwachsene, Kinder, Senioren" required />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="form-group">
            <label class="label">Beitragsbetrag (€)</label>
            <input v-model.number="form.beitragsbetrag" type="number" step="0.01" min="0" class="input" placeholder="0.00" />
          </div>
          <div class="form-group">
            <label class="label">Zahlungsintervall</label>
            <select v-model="form.zahlungsintervall" class="input">
              <option>Jährlich</option>
              <option>Halbjährlich</option>
              <option>Vierteljährlich</option>
              <option>Monatlich</option>
            </select>
          </div>
        </div>

        <div class="border border-slate-200 rounded-xl p-4 space-y-3">
          <h4 class="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
            <Users :size="14" /> Altersregel (optional)
          </h4>
          <p class="text-xs text-slate-400">Wenn gesetzt, kann "Altersbasiert zuweisen" Mitglieder automatisch dieser Klasse zuordnen.</p>
          <div class="grid grid-cols-2 gap-3">
            <div class="form-group">
              <label class="label">Mindestalter (Jahre)</label>
              <input v-model.number="form.min_alter" type="number" min="0" class="input" placeholder="0" />
            </div>
            <div class="form-group">
              <label class="label">Höchstalter (0 = unbegrenzt)</label>
              <input v-model.number="form.max_alter" type="number" min="0" class="input" placeholder="0" />
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="form-group">
            <label class="label">Anzeigefarbe</label>
            <input v-model="form.farbe" type="color" class="input h-10 cursor-pointer" />
          </div>
          <div class="space-y-2 pt-5">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.stimmberechtigt" type="checkbox" :true-value="1" :false-value="0" class="w-4 h-4" />
              <span class="text-sm">Stimmberechtigt</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.aktiv" type="checkbox" :true-value="1" :false-value="0" class="w-4 h-4" />
              <span class="text-sm">Aktiv</span>
            </label>
          </div>
        </div>

        <div class="border border-primary-200 bg-primary-50 rounded-xl p-4">
          <label class="flex items-start gap-3 cursor-pointer">
            <input v-model="form.ist_standardklasse" type="checkbox" :true-value="1" :false-value="0" class="w-4 h-4 mt-0.5 shrink-0" />
            <div>
              <span class="text-sm font-medium text-primary-800">Standardklasse (Fallback bei auto. Zuweisung)</span>
              <p class="text-xs text-primary-600 mt-0.5">
                Mitglieder, die zu keiner Altersregel passen, bekommen automatisch diese Klasse zugewiesen.
                Typisch: "Aktiv Erwachsene" oder "Vollmitglied".
              </p>
            </div>
          </label>
        </div>

        <div class="form-group">
          <label class="label">Beschreibung</label>
          <textarea v-model="form.beschreibung" class="input h-20 resize-none" placeholder="Kurze Beschreibung dieser Beitragsklasse..." />
        </div>
      </form>
      <template #footer>
        <button v-if="editTarget" @click="deleteKlasse" class="btn btn-danger mr-auto"><Trash2 :size="14" /></button>
        <button @click="showForm=false" class="btn btn-secondary">Abbrechen</button>
        <button @click="save" :disabled="saving" class="btn btn-primary">
          <Save :size="14" /> {{ saving ? 'Speichert...' : 'Speichern' }}
        </button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { Plus, Save, Trash2, Users, RefreshCw, CheckCircle, Info } from 'lucide-vue-next'

const klassen = ref([])
const loading = ref(true)
const showForm = ref(false)
const editTarget = ref(null)
const saving = ref(false)
const formError = ref('')
const autoRunning = ref(false)
const autoMsg = ref(null)
const form = ref({})

const emptyForm = () => ({
  bezeichnung: '', beitragsbetrag: 0, zahlungsintervall: 'Jährlich',
  min_alter: 0, max_alter: 0, farbe: '#2563eb',
  stimmberechtigt: 1, aktiv: 1, beschreibung: '', ist_standardklasse: 0,
})

onMounted(() => load())

async function load() {
  loading.value = true
  try { klassen.value = await api.call('dms_verein.api.verein.get_beitragsklassen') || [] }
  finally { loading.value = false }
}

function openCreate() { editTarget.value = null; form.value = emptyForm(); formError.value = ''; showForm.value = true }
function openEdit(k) { editTarget.value = k; form.value = { ...k }; formError.value = ''; showForm.value = true }

async function save() {
  saving.value = true; formError.value = ''
  try {
    const payload = { ...form.value }
    if (editTarget.value) payload.name = editTarget.value.name
    await api.call('dms_verein.api.verein.save_beitragsklasse', { data: payload })
    showForm.value = false
    await load()
  } catch (e) { formError.value = e.message }
  finally { saving.value = false }
}

async function deleteKlasse() {
  if (!confirm(`Beitragsklasse "${editTarget.value.bezeichnung}" wirklich löschen?`)) return
  try {
    await api.call('dms_verein.api.verein.delete_beitragsklasse', { name: editTarget.value.name })
    showForm.value = false; await load()
  } catch (e) { formError.value = e.message }
}

async function autoZuweisen() {
  autoRunning.value = true; autoMsg.value = null
  try {
    const r = await api.call('dms_verein.api.verein.auto_beitragsklasse_zuweisen')
    if (r.info) {
      autoMsg.value = { type: 'warning', text: r.info }
    } else {
      let text = `${r.geaendert} von ${r.gesamt} Mitglied(ern) zugewiesen.`
      if (r.kein_geburtsdatum) text += ` ${r.kein_geburtsdatum} ohne Geburtsdatum übersprungen.`
      if (r.kein_match) text += ` ${r.kein_match} passen zu keiner Altersregel.`
      if (r.altersklassen?.length) text += ` Aktive Regeln: ${r.altersklassen.join(', ')}.`
      autoMsg.value = { type: r.geaendert > 0 ? 'success' : 'info', text }
    }
  } catch (e) { autoMsg.value = { type: 'error', text: e.message } }
  finally { autoRunning.value = false }
}

const formatBetrag = (v) => Number(v || 0).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
</script>
