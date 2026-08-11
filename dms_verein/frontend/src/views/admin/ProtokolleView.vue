<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2>Versammlungsprotokolle</h2><p class="text-slate-500 mt-1">Sitzungen und Beschlüsse dokumentieren</p></div>
      <button @click="openCreate" class="btn btn-primary"><Plus :size="16" /> Neues Protokoll</button>
    </div>
    <AppSpinner v-if="loading" full-page />
    <div v-else class="table-wrapper">
      <table class="table">
        <thead><tr><th>Datum</th><th>Titel</th><th>Art</th><th>Anwesende</th><th></th></tr></thead>
        <tbody>
          <tr v-if="!protokolle.length"><td colspan="5" class="text-center py-8 text-slate-400">Keine Protokolle vorhanden</td></tr>
          <tr v-for="p in protokolle" :key="p.name" class="cursor-pointer hover:bg-slate-50" @click="openDetail(p)">
            <td class="font-medium whitespace-nowrap">{{ formatDate(p.datum) }}</td>
            <td>{{ p.titel }}</td>
            <td><span class="badge badge-blue">{{ p.typ }}</span></td>
            <td class="text-slate-500">{{ p.anzahl_anwesende || '—' }}</td>
            <td @click.stop>
              <div class="flex gap-1">
                <button @click="openEdit(p)" class="btn btn-secondary btn-sm p-1.5"><Pencil :size="13" /></button>
                <button @click="deleteProtokoll(p)" class="btn btn-danger btn-sm p-1.5"><Trash2 :size="13" /></button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Detail Modal -->
    <AppModal v-if="selected && !showEdit" :show="!!selected" :title="selected.titel" size="lg" @close="selected = null">
      <div class="space-y-4 text-sm">
        <div class="grid grid-cols-2 gap-3">
          <div><span class="text-slate-500">Datum:</span> {{ formatDate(selected.datum) }}</div>
          <div><span class="text-slate-500">Art:</span> {{ selected.typ }}</div>
          <div><span class="text-slate-500">Ort:</span> {{ selected.ort || '—' }}</div>
          <div><span class="text-slate-500">Anwesende:</span> {{ selected.anzahl_anwesende || '—' }}</div>
        </div>
        <div v-if="selected.tagesordnung" class="border-t pt-3"><p class="font-semibold mb-2">Tagesordnung</p><p class="whitespace-pre-wrap">{{ selected.tagesordnung }}</p></div>
        <div v-if="selected.beschluesse" class="border-t pt-3"><p class="font-semibold mb-2">Beschlüsse</p><p class="whitespace-pre-wrap">{{ selected.beschluesse }}</p></div>
      </div>
      <template #footer>
        <button @click="selected = null" class="btn btn-secondary">Schließen</button>
        <button @click="openEdit(selected)" class="btn btn-secondary"><Pencil :size="14" /> Bearbeiten</button>
        <button @click="deleteProtokoll(selected)" class="btn btn-danger"><Trash2 :size="14" /> Löschen</button>
      </template>
    </AppModal>

    <!-- Edit/Create Modal -->
    <AppModal :show="showEdit || showCreate" :title="editTarget ? 'Protokoll bearbeiten' : 'Neues Protokoll'" size="lg" @close="closeForm">
      <form @submit.prevent="saveForm" class="space-y-4">
        <AppAlert v-if="formError" type="error" :message="formError" />
        <div class="form-group"><label class="label">Titel *</label><input v-model="form.titel" class="input" required /></div>
        <div class="grid grid-cols-2 gap-3">
          <div class="form-group"><label class="label">Art der Versammlung</label>
            <select v-model="form.typ" class="input">
              <option>Vorstandssitzung</option><option>Hauptversammlung</option><option>Spartensitzung</option>
              <option>Außerordentliche Versammlung</option><option>Sonstige</option>
            </select>
          </div>
          <div class="form-group"><label class="label">Datum *</label><input v-model="form.datum" type="date" class="input" required /></div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="form-group"><label class="label">Ort</label><input v-model="form.ort" class="input" /></div>
          <div class="form-group"><label class="label">Anzahl Anwesende</label><input v-model="form.anzahl_anwesende" type="number" class="input" /></div>
        </div>
        <div class="form-group"><label class="label">Tagesordnung</label><textarea v-model="form.tagesordnung" class="input h-24 resize-none" /></div>
        <div class="form-group"><label class="label">Beschlüsse</label><textarea v-model="form.beschluesse" class="input h-24 resize-none" /></div>
      </form>
      <template #footer>
        <button @click="closeForm" class="btn btn-secondary">Abbrechen</button>
        <button @click="saveForm" :disabled="saving" class="btn btn-primary"><Save :size="14" /> {{ saving ? 'Speichert...' : 'Speichern' }}</button>
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
import { Plus, Pencil, Trash2, Save } from 'lucide-vue-next'

const protokolle = ref([])
const loading = ref(true)
const selected = ref(null)
const editTarget = ref(null)
const showEdit = ref(false)
const showCreate = ref(false)
const saving = ref(false)
const formError = ref('')
const blankForm = () => ({ titel: '', typ: 'Vorstandssitzung', datum: new Date().toISOString().split('T')[0], ort: '', anzahl_anwesende: null, tagesordnung: '', beschluesse: '' })
const form = ref(blankForm())

onMounted(() => load())

async function load() {
  loading.value = true
  try { protokolle.value = await api.getList('Versammlungsprotokoll', { fields: ['name','titel','typ','datum','ort','anzahl_anwesende','tagesordnung','beschluesse'], order_by: 'datum desc', limit_page_length: 50 }) || [] }
  finally { loading.value = false }
}

function openDetail(p) { selected.value = p }
function openCreate() { editTarget.value = null; form.value = blankForm(); formError.value = ''; showCreate.value = true }
function openEdit(p) {
  editTarget.value = p
  form.value = { titel: p.titel, typ: p.typ, datum: p.datum?.split(' ')[0] || '', ort: p.ort || '', anzahl_anwesende: p.anzahl_anwesende || null, tagesordnung: p.tagesordnung || '', beschluesse: p.beschluesse || '' }
  formError.value = ''; selected.value = null; showEdit.value = true
}
function closeForm() { showEdit.value = false; showCreate.value = false; editTarget.value = null }

async function saveForm() {
  saving.value = true; formError.value = ''
  try {
    if (editTarget.value) { await api.updateRecord('Versammlungsprotokoll', editTarget.value.name, form.value) }
    else { await api.insertDoc({ doctype: 'Versammlungsprotokoll', ...form.value }) }
    closeForm(); await load()
  } catch (e) { formError.value = e.message }
  finally { saving.value = false }
}

async function deleteProtokoll(p) {
  if (!confirm(`Protokoll "${p.titel}" wirklich löschen?`)) return
  try { await api.deleteRecord('Versammlungsprotokoll', p.name); selected.value = null; await load() }
  catch (e) { alert('Fehler: ' + e.message) }
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE') : '—'
</script>
