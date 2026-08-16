<template>
  <div class="min-h-screen bg-slate-50 py-12 px-4">
    <div class="max-w-2xl mx-auto">
      <div class="text-center mb-8">
        <RouterLink to="/" class="inline-block mb-4">
          <div class="w-12 h-12 rounded-xl bg-primary-600 flex items-center justify-center mx-auto">
            <Building2 :size="24" class="text-white" />
          </div>
        </RouterLink>
        <h1 class="text-3xl font-bold">Mitglied werden</h1>
        <p class="text-slate-500 mt-2">{{ verein.info?.vereinsname }} — Mitgliedsantrag</p>
      </div>

      <!-- Erfolg -->
      <div v-if="success" class="card card-body text-center py-12">
        <div class="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
          <CheckCircle2 :size="32" class="text-emerald-600" />
        </div>
        <h2 class="text-2xl font-bold mb-2">Antrag eingereicht!</h2>
        <p class="text-slate-500 max-w-md mx-auto">Vielen Dank für Ihren Antrag. Wir werden Ihre Daten prüfen und uns schnellstmöglich bei Ihnen melden.</p>
        <p class="text-sm text-slate-400 mt-4">Antragsnummer: <strong>{{ antragNr }}</strong></p>
        <RouterLink to="/" class="btn btn-primary mt-6 inline-flex">Zur Startseite</RouterLink>
      </div>

      <!-- Formular -->
      <form v-else @submit.prevent="submit" class="space-y-5">
        <AppAlert v-if="error" type="error" :message="error" />

        <!-- Schritt-Anzeige -->
        <div class="flex items-center gap-2 mb-6">
          <template v-for="(s, i) in steps" :key="i">
            <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors',
                          step > i ? 'bg-primary-600 text-white' : step === i ? 'bg-primary-100 text-primary-700 border-2 border-primary-600' : 'bg-slate-100 text-slate-400']">
              <Check v-if="step > i" :size="16" /><span v-else>{{ i+1 }}</span>
            </div>
            <div v-if="i < steps.length-1" :class="['flex-1 h-1 rounded', step > i ? 'bg-primary-600' : 'bg-slate-200']" />
          </template>
        </div>
        <p class="text-sm font-medium text-slate-500 -mt-2 mb-4">{{ steps[step] }}</p>

        <!-- Schritt 1: Persönliches -->
        <template v-if="step === 0">
          <div class="card card-body space-y-4">
            <div class="grid grid-cols-3 gap-3">
              <div class="form-group">
                <label class="label">Anrede</label>
                <select v-model="form.anrede" class="input">
                  <option value="">—</option><option>Herr</option><option>Frau</option><option>Divers</option>
                </select>
              </div>
              <div class="form-group col-span-2">
                <label class="label">Geburtsdatum</label>
                <input v-model="form.geburtsdatum" type="date" class="input" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div class="form-group">
                <label class="label">Vorname <span class="text-red-500">*</span></label>
                <input v-model="form.vorname" class="input" required />
              </div>
              <div class="form-group">
                <label class="label">Nachname <span class="text-red-500">*</span></label>
                <input v-model="form.nachname" class="input" required />
              </div>
            </div>
            <div class="form-group">
              <label class="label">Straße & Hausnummer <span class="text-red-500">*</span></label>
              <input v-model="form.strasse" class="input" required />
            </div>
            <div class="grid grid-cols-3 gap-3">
              <div class="form-group">
                <label class="label">PLZ <span class="text-red-500">*</span></label>
                <input v-model="form.plz" class="input" maxlength="5" required />
              </div>
              <div class="form-group col-span-2">
                <label class="label">Ort <span class="text-red-500">*</span></label>
                <input v-model="form.ort" class="input" required />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div class="form-group">
                <label class="label">E-Mail <span class="text-red-500">*</span></label>
                <input v-model="form.email" type="email" class="input" required />
              </div>
              <div class="form-group">
                <label class="label">Telefon / Mobil</label>
                <input v-model="form.telefon" class="input" />
              </div>
            </div>
          </div>
        </template>

        <!-- Schritt 2: Mitgliedschaft -->
        <template v-if="step === 1">
          <div class="card card-body space-y-4">
            <div class="form-group">
              <label class="label">Gewünschter Mitgliedstyp <span class="text-red-500">*</span></label>
              <div class="space-y-2 mt-2">
                <label v-for="t in typen" :key="t.name"
                  :class="['flex items-start gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all',
                           form.gewuenschter_mitgliedstyp === t.name ? 'border-primary-500 bg-primary-50' : 'border-slate-200 hover:border-primary-200']">
                  <input type="radio" v-model="form.gewuenschter_mitgliedstyp" :value="t.name" class="mt-1 shrink-0" />
                  <div>
                    <p class="font-medium">{{ t.bezeichnung }}</p>
                    <p class="text-sm text-slate-500">{{ formatCurrency(t.beitragsbetrag) }} / {{ t.zahlungsintervall }}</p>
                    <p v-if="t.beschreibung" class="text-xs text-slate-400 mt-0.5">{{ t.beschreibung }}</p>
                  </div>
                </label>
              </div>
            </div>
            <div class="form-group">
              <label class="label">Gewünschte Zuordnung: {{ verein.strukturSingular }} (optional)</label>
              <select v-model="form.sparte_wunsch" class="input">
                <option value="">Keine Präferenz</option>
                <option v-for="s in sparten" :key="s.name" :value="s.name">{{ s.icon }} {{ s.name_sparte }}</option>
              </select>
            </div>
          </div>
        </template>

        <!-- Schritt 3: SEPA (optional) -->
        <template v-if="step === 2">
          <div class="card card-body space-y-4">
            <div class="flex items-start gap-3">
              <input v-model="form.sepa_gewuenscht" type="checkbox" id="sepa" class="mt-1 w-4 h-4" />
              <label for="sepa">
                <p class="font-medium">SEPA Lastschriftmandat erteilen</p>
                <p class="text-sm text-slate-500">Der Mitgliedsbeitrag wird automatisch eingezogen</p>
              </label>
            </div>
            <template v-if="form.sepa_gewuenscht">
              <div class="form-group">
                <label class="label">Kontoinhaber <span class="text-red-500">*</span></label>
                <input v-model="form.kontoinhaber" class="input" :required="form.sepa_gewuenscht" />
              </div>
              <div class="form-group">
                <label class="label">IBAN <span class="text-red-500">*</span></label>
                <input v-model="form.iban" class="input font-mono" placeholder="DE12 3456 7890 1234 5678 90" :required="form.sepa_gewuenscht" />
              </div>
              <div class="form-group">
                <label class="label">BIC</label>
                <input v-model="form.bic" class="input font-mono" placeholder="XXXXDEXX" />
              </div>
              <p class="text-xs text-slate-400 p-3 bg-slate-50 rounded-lg">
                Ich ermächtige {{ verein.info?.vereinsname }}, Zahlungen von meinem Konto mittels Lastschrift einzuziehen.
                Zugleich weise ich mein Kreditinstitut an, die Lastschriften einzulösen.
              </p>
            </template>
          </div>
        </template>

        <!-- Schritt 4: Zustimmungen -->
        <template v-if="step === 3">
          <div class="card card-body space-y-4">
            <h3 class="text-base font-semibold">Einwilligungen & Bestätigung</h3>
            <label class="flex items-start gap-3 cursor-pointer">
              <input v-model="form.datenschutz_akzeptiert" type="checkbox" class="mt-1 w-4 h-4" required />
              <span class="text-sm">Ich habe die <a v-if="verein.info?.datenschutz_url" :href="verein.info.datenschutz_url" class="text-primary-600 hover:underline" target="_blank">Datenschutzerklärung</a><span v-else>Datenschutzerklärung</span> gelesen und bin einverstanden. <span class="text-red-500">*</span></span>
            </label>
            <label class="flex items-start gap-3 cursor-pointer">
              <input v-model="form.satzung_akzeptiert" type="checkbox" class="mt-1 w-4 h-4" required />
              <span class="text-sm">Ich erkenne die Satzung des Vereins an. <span class="text-red-500">*</span></span>
            </label>
            <label class="flex items-start gap-3 cursor-pointer">
              <input v-model="form.beitragsordnung_akzeptiert" type="checkbox" class="mt-1 w-4 h-4" required />
              <span class="text-sm">Ich akzeptiere die Beitragsordnung. <span class="text-red-500">*</span></span>
            </label>

            <!-- Zusammenfassung -->
            <div class="p-4 bg-slate-50 rounded-lg text-sm space-y-1 border border-slate-200">
              <p class="font-semibold mb-2">Zusammenfassung:</p>
              <p><span class="text-slate-500">Name:</span> {{ form.anrede }} {{ form.vorname }} {{ form.nachname }}</p>
              <p><span class="text-slate-500">Adresse:</span> {{ form.strasse }}, {{ form.plz }} {{ form.ort }}</p>
              <p><span class="text-slate-500">E-Mail:</span> {{ form.email }}</p>
              <p><span class="text-slate-500">Mitgliedstyp:</span> {{ form.gewuenschter_mitgliedstyp }}</p>
              <p v-if="form.sparte_wunsch"><span class="text-slate-500">{{ verein.strukturSingular }}:</span> {{ form.sparte_wunsch }}</p>
              <p><span class="text-slate-500">SEPA:</span> {{ form.sepa_gewuenscht ? 'Ja, ' + form.iban : 'Nein' }}</p>
            </div>
          </div>
        </template>

        <!-- Navigation -->
        <div class="flex justify-between">
          <button v-if="step > 0" type="button" @click="step--" class="btn btn-secondary">
            <ChevronLeft :size="16" /> Zurück
          </button>
          <div v-else></div>
          <button v-if="step < steps.length - 1" type="button" @click="nextStep" class="btn btn-primary">
            Weiter <ChevronRight :size="16" />
          </button>
          <button v-else type="submit" :disabled="submitting" class="btn btn-primary btn-lg">
            {{ submitting ? 'Wird eingereicht...' : 'Antrag einreichen' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import { useVereinStore } from '@/stores/verein'
import AppAlert from '@/components/ui/AppAlert.vue'
import { Building2, CheckCircle2, Check, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const verein = useVereinStore()
const typen = ref([])
const sparten = ref([])
const step = ref(0)
const success = ref(false)
const antragNr = ref('')
const error = ref('')
const submitting = ref(false)

const steps = ['Persönliche Daten', 'Mitgliedschaft', 'Zahlungsweise', 'Bestätigung']

const form = ref({
  anrede: '', vorname: '', nachname: '', geburtsdatum: '',
  strasse: '', plz: '', ort: '', email: '', telefon: '',
  gewuenschter_mitgliedstyp: '', sparte_wunsch: '',
  sepa_gewuenscht: false, kontoinhaber: '', iban: '', bic: '',
  datenschutz_akzeptiert: false, satzung_akzeptiert: false, beitragsordnung_akzeptiert: false,
})

onMounted(async () => {
  const [t, s] = await Promise.all([api.getMitgliedstypen(), api.getSparten()])
  typen.value = t || []
  sparten.value = s || []
})

function nextStep() {
  if (step.value === 0) {
    if (!form.value.vorname || !form.value.nachname || !form.value.strasse || !form.value.plz || !form.value.ort || !form.value.email) {
      error.value = 'Bitte füllen Sie alle Pflichtfelder aus.'
      return
    }
  }
  if (step.value === 1 && !form.value.gewuenschter_mitgliedstyp) {
    error.value = 'Bitte wählen Sie einen Mitgliedstyp.'
    return
  }
  error.value = ''
  step.value++
}

async function submit() {
  submitting.value = true; error.value = ''
  try {
    const res = await api.submitAntrag(form.value)
    antragNr.value = res?.name || ''
    success.value = true
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}

const formatCurrency = (v) => v ? `${Number(v).toFixed(2).replace('.', ',')} €` : 'kostenfrei'
</script>
