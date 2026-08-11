<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div><h2>Fotoalben</h2><p class="text-slate-500 mt-1">{{ alben.length }} Album{{ alben.length !== 1 ? 'en' : '' }}</p></div>
      <button @click="openCreate" class="btn btn-primary"><Plus :size="16" /> Neues Album</button>
    </div>

    <AppSpinner v-if="loading" full-page />

    <!-- Album Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div v-if="!alben.length" class="col-span-full card card-body text-center py-16 text-slate-400">
        <div class="text-5xl mb-3">📷</div>
        <p class="font-medium">Noch keine Fotoalben vorhanden</p>
        <p class="text-sm mt-1">Klicken Sie auf „Neues Album" um zu beginnen</p>
      </div>
      <div v-for="a in alben" :key="a.name"
        class="card overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
        @click="openAlbum(a)">
        <!-- Cover -->
        <div class="h-44 bg-slate-100 relative overflow-hidden">
          <img v-if="a.titelbild" :src="a.titelbild" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
          <div v-else class="w-full h-full flex flex-col items-center justify-center gap-2 text-slate-400">
            <span class="text-5xl">📷</span>
            <span class="text-xs">Kein Titelbild</span>
          </div>
          <!-- Badges -->
          <div class="absolute top-2 left-2 flex gap-1.5">
            <span :class="['badge', a.oeffentlich ? 'badge-green' : 'badge-gray']">{{ a.oeffentlich ? 'Öffentlich' : 'Intern' }}</span>
          </div>
          <!-- Foto-Anzahl -->
          <div class="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-0.5 rounded-full flex items-center gap-1">
            <ImageIcon :size="11" /> {{ a.foto_count || 0 }}
          </div>
        </div>
        <div class="card-body py-3">
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <h3 class="text-sm font-semibold truncate">{{ a.titel }}</h3>
              <p class="text-xs text-slate-500 mt-0.5">{{ formatDate(a.datum) }}</p>
            </div>
            <button @click.stop="openEdit(a)" class="btn btn-secondary btn-sm p-1.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" title="Bearbeiten">
              <Pencil :size="12" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Album Detail Modal (mit Foto-Verwaltung) ─── -->
    <AppModal v-if="albumDetail" :show="!!albumDetail" :title="albumDetail.titel" size="xl" @close="albumDetail = null">
      <!-- Album Info Bar -->
      <div class="flex flex-wrap items-center gap-3 pb-4 mb-4 border-b border-slate-200">
        <div class="flex items-center gap-2 text-sm text-slate-600">
          <CalendarIcon :size="14" /> {{ formatDate(albumDetail.datum) }}
        </div>
        <span :class="['badge', albumDetail.oeffentlich ? 'badge-green' : 'badge-gray']">{{ albumDetail.oeffentlich ? 'Öffentlich' : 'Intern' }}</span>
        <span class="text-sm text-slate-400">{{ albumDetail.fotos?.length || 0 }} Foto(s)</span>
        <div class="ml-auto flex gap-2">
          <button @click="openEdit(albumDetail); albumDetail = null" class="btn btn-secondary btn-sm">
            <Pencil :size="13" /> Metadaten
          </button>
          <label class="btn btn-primary btn-sm cursor-pointer">
            <Upload :size="13" /> Fotos hinzufügen
            <input ref="fileInput" type="file" accept="image/*" multiple class="hidden" @change="handleFileUpload" />
          </label>
        </div>
      </div>

      <!-- Upload Progress -->
      <div v-if="uploading" class="mb-4 p-3 bg-primary-50 rounded-lg flex items-center gap-3">
        <AppSpinner size="sm" />
        <span class="text-sm text-primary-700">{{ uploadProgress }}</span>
      </div>
      <AppAlert v-if="uploadError" type="error" :message="uploadError" class="mb-4" />

      <!-- Foto Grid -->
      <div v-if="!albumDetail.fotos?.length && !uploading" class="text-center py-12 text-slate-400">
        <div class="text-5xl mb-3">🖼️</div>
        <p class="font-medium">Noch keine Fotos in diesem Album</p>
        <p class="text-sm mt-1">Verwenden Sie „Fotos hinzufügen" um Bilder hochzuladen</p>
      </div>

      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        <div v-for="foto in albumDetail.fotos" :key="foto.name"
          class="relative group rounded-xl overflow-hidden bg-slate-100 aspect-square cursor-pointer"
          @click="openFotoPreview(foto)">
          <img :src="foto.datei" class="w-full h-full object-cover group-hover:opacity-75 transition-opacity" />
          <!-- Foto Overlay -->
          <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
            <button @click.stop="setAsTitelbild(foto)" class="btn btn-sm bg-white/90 text-slate-700 p-1.5" title="Als Titelbild setzen">
              <ImageIcon :size="14" />
            </button>
            <button @click.stop="deleteFoto(foto)" class="btn btn-sm bg-red-500 text-white p-1.5" title="Löschen">
              <Trash2 :size="14" />
            </button>
          </div>
          <!-- Titelbild Badge -->
          <div v-if="foto.datei === albumDetail.titelbild" class="absolute top-1.5 left-1.5">
            <span class="badge badge-yellow text-xs py-0">Cover</span>
          </div>
          <!-- Titel Tooltip -->
          <div v-if="foto.titel" class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent px-2 py-1">
            <p class="text-white text-xs truncate">{{ foto.titel }}</p>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400">Klick auf Foto → Vorschau · Hover → Aktionen</span>
          <div class="ml-auto flex gap-2">
            <button @click="deleteAlbum(albumDetail)" class="btn btn-danger btn-sm"><Trash2 :size="13" /> Album löschen</button>
            <button @click="albumDetail = null" class="btn btn-secondary">Schließen</button>
          </div>
        </div>
      </template>
    </AppModal>

    <!-- ─── Foto Preview Modal ─── -->
    <AppModal v-if="fotoPreview" :show="!!fotoPreview" :title="fotoPreview.titel || 'Foto'" size="xl" @close="fotoPreview = null">
      <div class="flex flex-col gap-4">
        <img :src="fotoPreview.datei" class="w-full max-h-[60vh] object-contain rounded-xl bg-slate-100" />
        <div v-if="fotoPreview.titel || fotoPreview.datum || fotoPreview.aufgenommen_von" class="grid grid-cols-3 gap-3 text-sm">
          <div v-if="fotoPreview.titel"><span class="text-slate-500">Titel:</span> {{ fotoPreview.titel }}</div>
          <div v-if="fotoPreview.datum"><span class="text-slate-500">Datum:</span> {{ formatDate(fotoPreview.datum) }}</div>
          <div v-if="fotoPreview.aufgenommen_von"><span class="text-slate-500">Von:</span> {{ fotoPreview.aufgenommen_von }}</div>
        </div>
      </div>
      <template #footer>
        <button @click="fotoPreview = null" class="btn btn-secondary">Schließen</button>
      </template>
    </AppModal>

    <!-- ─── Edit Metadata Modal ─── -->
    <AppModal :show="showEdit" title="Album bearbeiten" size="lg" @close="showEdit = false">
      <form @submit.prevent="saveEdit" class="space-y-4">
        <AppAlert v-if="formError" type="error" :message="formError" />
        <div class="form-group"><label class="label">Albumtitel *</label><input v-model="editForm.titel" class="input" required /></div>
        <div class="form-group"><label class="label">Datum *</label><input v-model="editForm.datum" type="date" class="input" required /></div>
        <div class="form-group"><label class="label">Beschreibung</label><textarea v-model="editForm.beschreibung" class="input h-16 resize-none" /></div>
        <label class="flex items-center gap-2 cursor-pointer"><input v-model="editForm.oeffentlich" type="checkbox" :true-value="1" :false-value="0" class="w-4 h-4" /><span class="text-sm">Öffentlich sichtbar</span></label>

        <!-- Berechtigungen -->
        <div class="border-t border-slate-100 pt-4">
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">Berechtigungen</p>
          <div class="grid grid-cols-2 gap-3">
            <div class="form-group">
              <label class="label">Fotos hochladen dürfen</label>
              <select v-model="editForm.upload_berechtigung" class="input">
                <option>Alle Mitglieder</option>
                <option>Spartenleiter</option>
                <option>Ausgewählte Mitglieder</option>
                <option>Nur Admin</option>
              </select>
            </div>
            <div class="form-group">
              <label class="label">Fremde Fotos löschen dürfen</label>
              <select v-model="editForm.loeschen_berechtigung" class="input">
                <option>Nur Admin</option>
                <option>Spartenleiter und Admin</option>
              </select>
            </div>
          </div>
          <p class="text-xs text-slate-400 mt-1">Eigene hochgeladene Fotos kann jedes Mitglied immer selbst löschen.</p>
        </div>

        <!-- Einzelne Mitglieder -->
        <div class="border-t border-slate-100 pt-4">
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">Einzelne Mitglieder</p>
          <p class="text-xs text-slate-400 mb-3">Unabhängig von der obigen Einstellung können hier einzelne Mitglieder zusätzliche Rechte erhalten.</p>

          <!-- Hinzufügen -->
          <div class="flex gap-2 mb-3">
            <select v-model="editMitgliedAuswahl" class="input flex-1 text-sm">
              <option value="">— Mitglied auswählen —</option>
              <option v-for="m in mitgliederListe" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
            <button type="button" @click="addMitgliedBerechtigung"
              :disabled="!editMitgliedAuswahl"
              class="btn btn-secondary btn-sm shrink-0">
              <Plus :size="14" /> Hinzufügen
            </button>
          </div>

          <!-- Tabelle -->
          <div v-if="editForm.mitglied_berechtigungen.length" class="rounded-xl border border-slate-200 overflow-hidden">
            <table class="w-full text-sm">
              <thead class="bg-slate-50">
                <tr>
                  <th class="text-left px-3 py-2 text-xs text-slate-500 font-medium">Mitglied</th>
                  <th class="text-center px-3 py-2 text-xs text-slate-500 font-medium">Hochladen</th>
                  <th class="text-center px-3 py-2 text-xs text-slate-500 font-medium">Löschen</th>
                  <th class="w-8"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="(row, idx) in editForm.mitglied_berechtigungen" :key="idx">
                  <td class="px-3 py-2 text-slate-700">{{ mitgliedLabel(row.mitglied) }}</td>
                  <td class="px-3 py-2 text-center">
                    <input type="checkbox" v-model="row.darf_hochladen" :true-value="1" :false-value="0" class="w-4 h-4" />
                  </td>
                  <td class="px-3 py-2 text-center">
                    <input type="checkbox" v-model="row.darf_loeschen" :true-value="1" :false-value="0" class="w-4 h-4" />
                  </td>
                  <td class="px-3 py-2">
                    <button type="button" @click="removeMitgliedBerechtigung(idx)" class="text-red-400 hover:text-red-600">
                      <Trash2 :size="13" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-xs text-slate-400 italic">Noch keine einzelnen Mitglieder eingetragen.</p>
        </div>
      </form>
      <template #footer>
        <button @click="showEdit = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="saveEdit" :disabled="saving" class="btn btn-primary"><Save :size="14" /> {{ saving ? 'Speichert...' : 'Speichern' }}</button>
      </template>
    </AppModal>

    <!-- ─── Create Modal ─── -->
    <AppModal :show="showCreate" title="Neues Fotoalbum" @close="showCreate = false">
      <form @submit.prevent="createAlbum" class="space-y-4">
        <AppAlert v-if="createError" type="error" :message="createError" />
        <div class="form-group"><label class="label">Albumtitel *</label><input v-model="createForm.titel" class="input" required /></div>
        <div class="form-group"><label class="label">Datum *</label><input v-model="createForm.datum" type="date" class="input" required /></div>
        <div class="form-group"><label class="label">Beschreibung</label><textarea v-model="createForm.beschreibung" class="input h-16 resize-none" /></div>
        <label class="flex items-center gap-2 cursor-pointer"><input v-model="createForm.oeffentlich" type="checkbox" :true-value="1" :false-value="0" class="w-4 h-4" /><span class="text-sm">Öffentlich sichtbar</span></label>
      </form>
      <template #footer>
        <button @click="showCreate = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="createAlbum" :disabled="creating" class="btn btn-primary">{{ creating ? 'Erstelle...' : 'Album erstellen' }}</button>
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
import { Plus, Pencil, Trash2, Save, Upload, Image as ImageIcon, Calendar as CalendarIcon } from 'lucide-vue-next'

const alben = ref([])
const loading = ref(true)
const albumDetail = ref(null)
const fotoPreview = ref(null)
const editTarget = ref(null)
const showEdit = ref(false)
const showCreate = ref(false)
const saving = ref(false)
const creating = ref(false)
const formError = ref('')
const createError = ref('')
const uploading = ref(false)
const uploadProgress = ref('')
const uploadError = ref('')
const fileInput = ref(null)
const mitgliederListe = ref([])
const editMitgliedAuswahl = ref('')

const editForm = ref({ titel: '', datum: '', beschreibung: '', oeffentlich: 0, upload_berechtigung: 'Alle Mitglieder', loeschen_berechtigung: 'Nur Admin', mitglied_berechtigungen: [] })
const createForm = ref({ titel: '', datum: new Date().toISOString().split('T')[0], beschreibung: '', oeffentlich: 0 })

onMounted(() => {
  load()
  api.call('dms_verein.api.verein.get_mitglieder_liste_einfach').then(r => { mitgliederListe.value = r || [] }).catch(() => {})
})

function mitgliedLabel(name) {
  return mitgliederListe.value.find(m => m.value === name)?.label || name
}

function addMitgliedBerechtigung() {
  if (!editMitgliedAuswahl.value) return
  if (editForm.value.mitglied_berechtigungen.find(r => r.mitglied === editMitgliedAuswahl.value)) return
  editForm.value.mitglied_berechtigungen.push({ mitglied: editMitgliedAuswahl.value, darf_hochladen: 1, darf_loeschen: 0 })
  editMitgliedAuswahl.value = ''
}

function removeMitgliedBerechtigung(idx) {
  editForm.value.mitglied_berechtigungen.splice(idx, 1)
}

async function load() {
  loading.value = true
  try { alben.value = await api.getAlbenListe() || [] }
  finally { loading.value = false }
}

async function openAlbum(a) {
  const detail = await api.getAlbumDetail(a.name)
  albumDetail.value = detail
  uploadError.value = ''
}

function openCreate() {
  createForm.value = { titel: '', datum: new Date().toISOString().split('T')[0], beschreibung: '', oeffentlich: 0 }
  createError.value = ''
  showCreate.value = true
}

async function openEdit(a) {
  editTarget.value = a
  formError.value = ''
  editMitgliedAuswahl.value = ''
  // Volles Dokument laden damit Berechtigungen verfügbar sind
  let full = a
  if (!a.mitglied_berechtigungen) {
    try { full = await api.call('frappe.client.get', { doctype: 'Fotoalbum', name: a.name }) } catch {}
  }
  editTarget.value = full
  editForm.value = {
    titel: full.titel || '',
    datum: full.datum?.split(' ')[0] || '',
    beschreibung: full.beschreibung || '',
    oeffentlich: full.oeffentlich ?? 0,
    upload_berechtigung: full.upload_berechtigung || 'Alle Mitglieder',
    loeschen_berechtigung: full.loeschen_berechtigung || 'Nur Admin',
    mitglied_berechtigungen: (full.mitglied_berechtigungen || []).map(r => ({ mitglied: r.mitglied, darf_hochladen: r.darf_hochladen, darf_loeschen: r.darf_loeschen })),
  }
  showEdit.value = true
}

function openFotoPreview(foto) { fotoPreview.value = foto }

async function handleFileUpload(event) {
  const files = Array.from(event.target.files)
  if (!files.length || !albumDetail.value) return
  uploading.value = true
  uploadError.value = ''

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    uploadProgress.value = `Lade hoch: ${file.name} (${i + 1}/${files.length})`
    try {
      const uploadResult = await api.uploadFile(file, 'Fotoalbum', albumDetail.value.name)
      const fileUrl = uploadResult?.file_url
      if (!fileUrl) throw new Error('Kein file_url in Antwort')
      const updated = await api.addFotoToAlbum(albumDetail.value.name, fileUrl, file.name.replace(/\.[^.]+$/, ''), '', '')
      albumDetail.value = updated
    } catch (e) {
      uploadError.value = `Fehler bei "${file.name}": ${e.message}`
      break
    }
  }

  uploading.value = false
  uploadProgress.value = ''
  event.target.value = '' // Reset file input
  await load() // Refresh album list (update foto count)
}

async function deleteFoto(foto) {
  if (!confirm(`Foto "${foto.titel || foto.datei?.split('/').pop()}" wirklich löschen?`)) return
  try {
    const updated = await api.deleteFotoFromAlbum(albumDetail.value.name, foto.name)
    albumDetail.value = updated
    await load()
  } catch (e) { alert('Fehler: ' + e.message) }
}

async function setAsTitelbild(foto) {
  try {
    await api.setAlbumTitelbild(albumDetail.value.name, foto.datei)
    albumDetail.value = { ...albumDetail.value, titelbild: foto.datei }
    await load()
  } catch (e) { alert('Fehler: ' + e.message) }
}

async function saveEdit() {
  saving.value = true; formError.value = ''
  try {
    await api.updateRecord('Fotoalbum', editTarget.value.name, editForm.value)
    showEdit.value = false
    await load()
  } catch (e) { formError.value = e.message }
  finally { saving.value = false }
}

async function createAlbum() {
  creating.value = true; createError.value = ''
  try {
    const newDoc = await api.insertDoc({ doctype: 'Fotoalbum', ...createForm.value })
    showCreate.value = false
    await load()
    if (newDoc?.name) await openAlbum({ name: newDoc.name })
  } catch (e) { createError.value = e.message }
  finally { creating.value = false }
}

async function deleteAlbum(a) {
  if (!confirm(`Album "${a.titel}" und alle ${a.fotos?.length || 0} Fotos wirklich löschen?`)) return
  try {
    await api.deleteRecord('Fotoalbum', a.name)
    albumDetail.value = null
    await load()
  } catch (e) { alert('Fehler beim Löschen: ' + e.message) }
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE', { day: 'numeric', month: 'long', year: 'numeric' }) : '—'
</script>
