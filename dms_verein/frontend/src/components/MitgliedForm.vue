<template>
  <form @submit.prevent="save" class="space-y-4">
    <AppAlert v-if="error" type="error" :message="error" />

    <div class="grid grid-cols-2 gap-4">
      <div class="form-group">
        <label class="label">Anrede</label>
        <select v-model="form.anrede" class="input">
          <option value="">Bitte wählen</option>
          <option>Herr</option><option>Frau</option><option>Divers</option>
        </select>
      </div>
      <div class="form-group">
        <label class="label">Geburtsdatum</label>
        <input v-model="form.geburtsdatum" type="date" class="input" />
      </div>
    </div>

    <div class="grid grid-cols-2 gap-4">
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

    <div class="grid grid-cols-3 gap-4">
      <div class="form-group">
        <label class="label">PLZ <span class="text-red-500">*</span></label>
        <input v-model="form.plz" class="input" required />
      </div>
      <div class="form-group col-span-2">
        <label class="label">Ort <span class="text-red-500">*</span></label>
        <input v-model="form.ort" class="input" required />
      </div>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <div class="form-group">
        <label class="label">E-Mail</label>
        <input v-model="form.email" type="email" class="input" />
      </div>
      <div class="form-group">
        <label class="label">Telefon</label>
        <input v-model="form.telefon" class="input" />
      </div>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <div class="form-group">
        <label class="label">Mitgliedstyp <span class="text-red-500">*</span></label>
        <select v-model="form.mitgliedstyp" class="input" required>
          <option value="">Bitte wählen</option>
          <option v-for="t in typen" :key="t.name" :value="t.name">
            {{ t.bezeichnung }} ({{ formatCurrency(t.beitragsbetrag) }}/{{ t.zahlungsintervall }})
          </option>
        </select>
      </div>
      <div class="form-group">
        <label class="label">Eintrittsdatum <span class="text-red-500">*</span></label>
        <input v-model="form.eintrittsdatum" type="date" class="input" required />
      </div>
    </div>

    <div class="flex justify-end gap-3 pt-2">
      <button type="button" @click="$emit('cancel')" class="btn btn-secondary">Abbrechen</button>
      <button type="submit" :disabled="saving" class="btn btn-primary">
        <span v-if="saving">Wird gespeichert...</span>
        <span v-else>Mitglied anlegen</span>
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '@/utils/api'
import AppAlert from '@/components/ui/AppAlert.vue'

const props = defineProps({ typen: Array })
const emit = defineEmits(['saved', 'cancel'])

const form = ref({
  anrede: '',
  vorname: '',
  nachname: '',
  geburtsdatum: '',
  strasse: '',
  plz: '',
  ort: '',
  land: 'Deutschland',
  email: '',
  telefon: '',
  mitgliedstyp: '',
  eintrittsdatum: new Date().toISOString().split('T')[0],
  status: 'Aktiv',
})

const saving = ref(false)
const error = ref('')

async function save() {
  saving.value = true
  error.value = ''
  try {
    await api.insertDoc({ doctype: 'Mitglied', ...form.value })
    emit('saved')
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

const formatCurrency = (v) => v ? `${Number(v).toFixed(2)} €` : 'kostenlos'
</script>
