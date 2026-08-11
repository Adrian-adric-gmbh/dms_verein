<template>
  <div>
    <div class="flex flex-wrap items-start justify-between gap-3 mb-6">
      <div><h2>Mein Profil</h2><p class="text-slate-500 mt-1">Ihre persönlichen Daten</p></div>
      <button v-if="!editMode" @click="editMode = true" class="btn btn-secondary shrink-0">
        <Pencil :size="16" /> Bearbeiten
      </button>
      <div v-else class="flex gap-2 shrink-0">
        <button @click="cancel" class="btn btn-secondary">Abbrechen</button>
        <button @click="save" :disabled="saving" class="btn btn-primary"><Save :size="16" /> Speichern</button>
      </div>
    </div>

    <AppAlert v-if="success" type="success" message="Ihre Daten wurden gespeichert." :dismissible="true" class="mb-4" />
    <AppAlert v-if="error" type="error" :message="error" class="mb-4" />
    <AppSpinner v-if="loading" full-page />

    <div v-else-if="profil" class="space-y-5">
      <!-- Kontaktdaten -->
      <div class="card">
        <div class="card-header"><h3 class="text-base font-semibold">Kontaktdaten</h3></div>
        <div class="card-body grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p class="label">Vorname</p>
            <p class="font-medium">{{ profil.vorname }}</p>
          </div>
          <div>
            <p class="label">Nachname</p>
            <p class="font-medium">{{ profil.nachname }}</p>
          </div>
          <div>
            <p class="label">E-Mail</p>
            <input v-if="editMode" v-model="form.email" type="email" class="input" />
            <p v-else class="font-medium">{{ profil.email || '—' }}</p>
          </div>
          <div>
            <p class="label">Telefon / Mobil</p>
            <input v-if="editMode" v-model="form.telefon" class="input" />
            <p v-else class="font-medium">{{ profil.telefon || profil.mobil || '—' }}</p>
          </div>
        </div>
      </div>

      <!-- Adresse -->
      <div class="card">
        <div class="card-header"><h3 class="text-base font-semibold">Adresse</h3></div>
        <div class="card-body grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="sm:col-span-2">
            <p class="label">Straße & Hausnummer</p>
            <input v-if="editMode" v-model="form.strasse" class="input" />
            <p v-else class="font-medium">{{ profil.strasse || '—' }}</p>
          </div>
          <div>
            <p class="label">PLZ</p>
            <input v-if="editMode" v-model="form.plz" class="input" maxlength="5" />
            <p v-else class="font-medium">{{ profil.plz || '—' }}</p>
          </div>
          <div>
            <p class="label">Ort</p>
            <input v-if="editMode" v-model="form.ort" class="input" />
            <p v-else class="font-medium">{{ profil.ort || '—' }}</p>
          </div>
        </div>
      </div>

      <!-- Bankdaten -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-base font-semibold">Bankverbindung</h3>
        </div>
        <div class="card-body grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="sm:col-span-2">
            <p class="label">Kreditinstitut</p>
            <input v-if="editMode" v-model="form.bank_name" class="input" />
            <p v-else class="font-medium">{{ profil.bank_name || '—' }}</p>
          </div>
          <div>
            <p class="label">IBAN</p>
            <input v-if="editMode" v-model="form.iban" class="input font-mono" />
            <p v-else class="font-mono font-medium">{{ maskIban(profil.iban) }}</p>
          </div>
          <div>
            <p class="label">BIC</p>
            <input v-if="editMode" v-model="form.bic" class="input font-mono" />
            <p v-else class="font-medium">{{ profil.bic || '—' }}</p>
          </div>
        </div>
      </div>

      <!-- SEPA Lastschriftmandat -->
      <div class="card">
        <div class="card-header flex items-center justify-between">
          <h3 class="text-base font-semibold">SEPA Lastschriftmandat</h3>
          <span v-if="mandat && mandat.iban" class="badge badge-green text-xs">Aktiv</span>
        </div>
        <div class="card-body">
          <AppSpinner v-if="mandatLoading" />

          <!-- Aktives Mandat vorhanden -->
          <div v-else-if="mandat && mandat.iban" class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
              <div>
                <p class="label">Mandatsreferenz</p>
                <p class="font-mono font-medium text-xs">{{ mandat.mandatsreferenz }}</p>
              </div>
              <div>
                <p class="label">Erteilt am</p>
                <p class="font-medium">{{ formatDate(mandat.erteilungsdatum) }}</p>
              </div>
              <div>
                <p class="label">Kontoinhaber</p>
                <p class="font-medium">{{ mandat.kontoinhaber }}</p>
              </div>
              <div>
                <p class="label">Kreditinstitut</p>
                <p class="font-medium">{{ mandat.bank_name || '—' }}</p>
              </div>
              <div>
                <p class="label">IBAN</p>
                <p class="font-mono font-medium">{{ maskIban(mandat.iban) }}</p>
              </div>
              <div>
                <p class="label">Einzüge bisher</p>
                <p class="font-medium">{{ mandat.anzahl_einzuege || 0 }}</p>
              </div>
            </div>
            <div class="pt-2 border-t border-slate-100">
              <AppAlert v-if="mandatError" type="error" :message="mandatError" class="mb-3" />
              <button v-if="!showWiderruf" @click="showWiderruf = true"
                class="btn btn-secondary text-red-600 hover:bg-red-50 text-sm">
                <XCircle :size="14" /> Mandat widerrufen
              </button>
              <div v-else class="space-y-3">
                <p class="text-sm text-slate-600">Möchten Sie das Lastschriftmandat wirklich widerrufen? Zukünftige Beiträge werden dann per Überweisung fällig.</p>
                <div class="flex gap-2">
                  <button @click="showWiderruf = false" class="btn btn-secondary flex-1">Abbrechen</button>
                  <button @click="widerrufMandat" :disabled="mandatSaving" class="btn btn-danger flex-1">
                    {{ mandatSaving ? 'Wird widerrufen…' : 'Ja, widerrufen' }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Kein Mandat → Formular -->
          <div v-else class="space-y-4">
            <p class="text-sm text-slate-600">
              Mit einem SEPA-Lastschriftmandat ermächtigen Sie den Verein, Mitgliedsbeiträge automatisch von Ihrem Konto einzuziehen. Sie können das Mandat jederzeit widerrufen.
            </p>
            <AppAlert v-if="mandatError" type="error" :message="mandatError" />
            <AppAlert v-if="mandatSuccess" type="success" message="Ihr Lastschriftmandat wurde erfolgreich erteilt." />

            <div v-if="!mandatSuccess" class="space-y-3">
              <div class="form-group">
                <label class="label">Kontoinhaber *</label>
                <input v-model="mandatForm.kontoinhaber" class="input"
                  :placeholder="`${profil.vorname} ${profil.nachname}`" />
              </div>
              <div class="form-group">
                <label class="label">IBAN *</label>
                <input v-model="mandatForm.iban" class="input font-mono" placeholder="DE00 0000 0000 0000 0000 00"
                  @input="mandatForm.iban = formatIban($event.target.value)" />
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div class="form-group">
                  <label class="label">BIC</label>
                  <input v-model="mandatForm.bic" class="input font-mono" placeholder="XXXXXXXX" />
                </div>
                <div class="form-group">
                  <label class="label">Kreditinstitut</label>
                  <input v-model="mandatForm.bank_name" class="input" placeholder="Meine Bank" />
                </div>
              </div>
              <!-- Einwilligung -->
              <label class="flex items-start gap-2 cursor-pointer">
                <input v-model="mandatForm.einwilligung" type="checkbox" class="mt-0.5 w-4 h-4 shrink-0" />
                <span class="text-xs text-slate-600">
                  Ich ermächtige den Verein, Zahlungen von meinem Konto mittels Lastschrift einzuziehen.
                  Zugleich weise ich mein Kreditinstitut an, die vom Verein auf mein Konto gezogenen
                  Lastschriften einzulösen. Ich kann innerhalb von 8 Wochen, beginnend mit dem Belastungsdatum,
                  die Erstattung des belasteten Betrages verlangen.
                </span>
              </label>
              <button @click="erteileMandat"
                :disabled="mandatSaving || !mandatForm.einwilligung || !mandatForm.iban || !mandatForm.kontoinhaber"
                class="w-full btn btn-primary">
                {{ mandatSaving ? 'Wird gespeichert…' : 'Lastschriftmandat erteilen' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { Pencil, Save, XCircle } from 'lucide-vue-next'

const profil = ref(null)
const loading = ref(true)
const editMode = ref(false)
const saving = ref(false)
const success = ref(false)
const error = ref('')
const form = ref({})

// SEPA
const mandat = ref(null)
const mandatLoading = ref(true)
const mandatSaving = ref(false)
const mandatError = ref('')
const mandatSuccess = ref(false)
const showWiderruf = ref(false)
const mandatForm = ref({ kontoinhaber: '', iban: '', bic: '', bank_name: '', einwilligung: false })

onMounted(async () => {
  try {
    const [p, m] = await Promise.all([
      api.getMeinProfil(),
      api.call('dms_verein.api.verein.get_mein_sepa_mandat').catch(() => null),
    ])
    profil.value = p
    mandat.value = m
    resetForm()
  } finally {
    loading.value = false
    mandatLoading.value = false
  }
  // Kontoinhaber vorausfüllen
  if (profil.value) {
    mandatForm.value.kontoinhaber = `${profil.value.vorname} ${profil.value.nachname}`
    mandatForm.value.iban = profil.value.iban || ''
    mandatForm.value.bic = profil.value.bic || ''
    mandatForm.value.bank_name = profil.value.bank_name || ''
  }
})

function resetForm() {
  form.value = {
    email: profil.value.email || '',
    telefon: profil.value.telefon || '',
    strasse: profil.value.strasse || '',
    plz: profil.value.plz || '',
    ort: profil.value.ort || '',
    bank_name: profil.value.bank_name || '',
    iban: profil.value.iban || '',
    bic: profil.value.bic || '',
  }
}

function cancel() { editMode.value = false; resetForm() }

async function save() {
  saving.value = true; error.value = ''; success.value = false
  try {
    await api.updateMeinProfil(form.value)
    profil.value = { ...profil.value, ...form.value }
    editMode.value = false
    success.value = true
    setTimeout(() => success.value = false, 3000)
  } catch (e) { error.value = e.message }
  finally { saving.value = false }
}

async function erteileMandat() {
  mandatSaving.value = true; mandatError.value = ''
  try {
    const result = await api.call('dms_verein.api.verein.create_mein_sepa_mandat', {
      iban: mandatForm.value.iban,
      kontoinhaber: mandatForm.value.kontoinhaber,
      bank_name: mandatForm.value.bank_name,
      bic: mandatForm.value.bic,
    })
    mandatSuccess.value = true
    // Mandat nachladen
    mandat.value = await api.call('dms_verein.api.verein.get_mein_sepa_mandat').catch(() => null)
  } catch (e) { mandatError.value = e.message }
  finally { mandatSaving.value = false }
}

async function widerrufMandat() {
  mandatSaving.value = true; mandatError.value = ''
  try {
    await api.call('dms_verein.api.verein.widerruf_mein_sepa_mandat')
    mandat.value = null
    showWiderruf.value = false
  } catch (e) { mandatError.value = e.message }
  finally { mandatSaving.value = false }
}

const maskIban = (iban) => {
  if (!iban) return '—'
  return iban.slice(0, 4) + ' **** **** **** ' + iban.slice(-4)
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE') : '—'

function formatIban(value) {
  const clean = value.replace(/\s/g, '').toUpperCase()
  return clean.replace(/(.{4})/g, '$1 ').trim()
}
</script>
