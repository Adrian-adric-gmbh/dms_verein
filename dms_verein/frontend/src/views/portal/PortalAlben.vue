<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2>Fotoalben</h2>
        <p class="text-slate-500 mt-1">Erinnerungen aus dem Vereinsleben</p>
      </div>
      <button v-if="isAdmin" @click="openCreate" class="btn btn-primary">
        <Plus :size="16" /> Neues Album
      </button>
    </div>

    <AppSpinner v-if="loading" full-page />

    <!-- Album Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-if="!alben.length"
        class="col-span-full card card-body text-center py-16 text-slate-400">
        <div class="text-5xl mb-3">📷</div>
        <p class="font-medium">Noch keine Fotoalben vorhanden</p>
        <p class="text-sm mt-1">
          {{ isAdmin ? 'Klicken Sie auf „Neues Album" um zu beginnen' : 'Der Administrator legt Alben an — du kannst dann Fotos hochladen' }}
        </p>
      </div>

      <div v-for="a in alben" :key="a.name"
        class="card overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
        @click="openAlbum(a)">
        <div class="h-44 bg-slate-100 relative overflow-hidden">
          <img v-if="a.titelbild" :src="a.titelbild"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
          <div v-else
            class="w-full h-full flex flex-col items-center justify-center gap-2 text-slate-400">
            <Camera :size="40" />
            <span class="text-xs">Kein Titelbild</span>
          </div>
          <div class="absolute top-2 left-2 flex gap-1.5">
            <span v-if="!a.oeffentlich" class="badge badge-gray text-xs">Intern</span>
          </div>
          <div
            class="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-0.5 rounded-full flex items-center gap-1">
            <ImageIcon :size="11" /> {{ a.foto_count || 0 }}
          </div>
        </div>
        <div class="card-body py-3">
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <h3 class="text-sm font-semibold truncate">{{ a.titel }}</h3>
              <p class="text-xs text-slate-500 mt-0.5">{{ formatDate(a.datum) }}</p>
              <p v-if="a.beschreibung" class="text-xs text-slate-400 mt-1 line-clamp-1">{{ a.beschreibung }}</p>
            </div>
            <button v-if="isAdmin" @click.stop="openEdit(a)"
              class="btn btn-secondary btn-sm p-1.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
              title="Bearbeiten">
              <Pencil :size="12" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Album Detail Modal ─── -->
    <AppModal v-if="albumDetail" :show="!!albumDetail" :title="albumDetail.titel" size="xl"
      @close="albumDetail = null">
      <!-- Info Bar -->
      <div class="flex flex-wrap items-center gap-3 pb-4 mb-4 border-b border-slate-200">
        <span class="text-sm text-slate-500">{{ formatDate(albumDetail.datum) }}</span>
        <span class="text-sm text-slate-400">{{ albumDetail.fotos?.length || 0 }} Foto(s)</span>
        <div class="ml-auto flex gap-2">
          <label v-if="albumBerechtigung.darf_hochladen" class="btn btn-primary btn-sm cursor-pointer">
            <Upload :size="13" /> Fotos hochladen
            <input type="file" accept="image/*" multiple class="hidden" @change="handleUpload" />
          </label>
          <span v-else class="text-xs text-slate-400 self-center">Kein Upload-Recht für dieses Album</span>
        </div>
      </div>

      <!-- Upload Progress -->
      <div v-if="uploading" class="mb-4 p-3 bg-primary-50 rounded-lg flex items-center gap-3">
        <AppSpinner size="sm" />
        <span class="text-sm text-primary-700">{{ uploadProgress }}</span>
      </div>
      <AppAlert v-if="uploadError" type="error" :message="uploadError" class="mb-4" />

      <!-- Foto Grid -->
      <div v-if="!albumDetail.fotos?.length && !uploading"
        class="text-center py-12 text-slate-400">
        <div class="text-4xl mb-3">🖼️</div>
        <p class="font-medium">Noch keine Fotos</p>
        <p class="text-sm mt-1">Lade Bilder mit „Fotos hochladen" hoch</p>
      </div>

      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        <div v-for="(foto, idx) in albumDetail.fotos" :key="foto.name"
          class="relative rounded-xl overflow-hidden bg-slate-100 aspect-square cursor-pointer"
          @click="openLightbox(idx)">
          <img :src="foto.datei" class="w-full h-full object-cover" />
          <!-- Cover Badge -->
          <div v-if="foto.datei === albumDetail.titelbild" class="absolute top-1.5 left-1.5">
            <span class="badge badge-yellow text-xs py-0">Cover</span>
          </div>
          <!-- Foto-Titel -->
          <div v-if="foto.titel"
            class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent px-2 py-1">
            <p class="text-white text-xs truncate">{{ foto.titel }}</p>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex items-center gap-2 w-full">
          <button v-if="isAdmin" @click="deleteAlbum(albumDetail)"
            class="btn btn-danger btn-sm">
            <Trash2 :size="13" /> Album löschen
          </button>
          <div class="ml-auto">
            <button @click="albumDetail = null" class="btn btn-secondary">Schließen</button>
          </div>
        </div>
      </template>
    </AppModal>

    <!-- ─── Lightbox ─── -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="lightbox !== null"
          class="fixed inset-0 z-[9999] bg-black/95 flex flex-col items-center justify-center touch-none"
          @click.self="lightbox = null">
          <!-- Close -->
          <button @click.stop="lightbox = null"
            class="absolute top-4 right-4 text-white/70 hover:text-white z-10 p-2 -m-2">
            <X :size="28" />
          </button>
          <!-- Prev -->
          <button v-if="lightbox > 0" @click.stop="lightbox--"
            class="absolute left-3 top-1/2 -translate-y-1/2 text-white bg-black/40 active:bg-black/70 rounded-full p-3 z-10">
            <ChevronLeft :size="24" />
          </button>
          <!-- Next -->
          <button v-if="lightbox < (albumDetail?.fotos?.length ?? 0) - 1" @click.stop="lightbox++"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-white bg-black/40 active:bg-black/70 rounded-full p-3 z-10">
            <ChevronRight :size="24" />
          </button>
          <!-- Image -->
          <img :src="currentFoto?.datei"
            class="max-w-[92vw] max-h-[72dvh] object-contain rounded-lg shadow-2xl select-none pointer-events-none" />
          <!-- Untere Leiste: Caption + Aktionen -->
          <div class="absolute bottom-0 left-0 right-0 px-4 pb-6 pt-3 flex flex-col items-center gap-3">
            <div class="text-center">
              <p v-if="currentFoto?.titel"
                class="text-white text-sm bg-black/60 inline-block px-4 py-1.5 rounded-full mb-1">
                {{ currentFoto.titel }}
              </p>
              <p class="text-white/50 text-xs">
                {{ (lightbox ?? 0) + 1 }} / {{ albumDetail?.fotos?.length }}
              </p>
            </div>
            <!-- Aktions-Buttons -->
            <div v-if="currentFoto" class="flex gap-3" @click.stop>
              <button v-if="isAdmin"
                @click.stop="setTitelbild(currentFoto)"
                class="flex items-center gap-1.5 px-4 py-2 rounded-full bg-white/15 hover:bg-white/25 active:bg-white/30 text-white text-sm transition-colors">
                <ImageIcon :size="15" /> Als Cover
              </button>
              <button
                v-if="albumBerechtigung.darf_loeschen || (albumBerechtigung.darf_eigene_loeschen && currentFoto.hochgeladen_von && currentFoto.hochgeladen_von === albumBerechtigung.current_mitglied)"
                @click.stop="deleteFotoAndClose(currentFoto)"
                class="flex items-center gap-1.5 px-4 py-2 rounded-full bg-red-500/80 hover:bg-red-500 active:bg-red-600 text-white text-sm transition-colors">
                <Trash2 :size="15" /> Löschen
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ─── Album erstellen Modal ─── -->
    <AppModal :show="showCreate" title="Neues Fotoalbum" @close="showCreate = false">
      <form @submit.prevent="createAlbum" class="space-y-4">
        <AppAlert v-if="createError" type="error" :message="createError" />
        <div class="form-group">
          <label class="label">Albumtitel *</label>
          <input v-model="createForm.titel" class="input" required placeholder="z.B. Sommerfest 2025" />
        </div>
        <div class="form-group">
          <label class="label">Datum *</label>
          <input v-model="createForm.datum" type="date" class="input" required />
        </div>
        <div class="form-group">
          <label class="label">Beschreibung</label>
          <textarea v-model="createForm.beschreibung" class="input h-16 resize-none"
            placeholder="Kurze Beschreibung des Albums..." />
        </div>
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="createForm.oeffentlich" type="checkbox" :true-value="1" :false-value="0"
            class="w-4 h-4 rounded" />
          <span class="text-sm">Öffentlich sichtbar (auch ohne Login)</span>
        </label>
      </form>
      <template #footer>
        <button @click="showCreate = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="createAlbum" :disabled="creating" class="btn btn-primary">
          {{ creating ? 'Erstelle…' : 'Album erstellen' }}
        </button>
      </template>
    </AppModal>

    <!-- ─── Album bearbeiten Modal ─── -->
    <AppModal :show="showEdit" title="Album bearbeiten" @close="showEdit = false">
      <form @submit.prevent="saveEdit" class="space-y-4">
        <AppAlert v-if="editError" type="error" :message="editError" />
        <div class="form-group">
          <label class="label">Albumtitel *</label>
          <input v-model="editForm.titel" class="input" required />
        </div>
        <div class="form-group">
          <label class="label">Datum *</label>
          <input v-model="editForm.datum" type="date" class="input" required />
        </div>
        <div class="form-group">
          <label class="label">Beschreibung</label>
          <textarea v-model="editForm.beschreibung" class="input h-16 resize-none" />
        </div>
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="editForm.oeffentlich" type="checkbox" :true-value="1" :false-value="0"
            class="w-4 h-4 rounded" />
          <span class="text-sm">Öffentlich sichtbar</span>
        </label>
      </form>
      <template #footer>
        <button @click="showEdit = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="saveEdit" :disabled="saving" class="btn btn-primary">
          {{ saving ? 'Speichert…' : 'Speichern' }}
        </button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { Camera, Plus, Pencil, Trash2, Upload, X, ChevronLeft, ChevronRight, Image as ImageIcon } from 'lucide-vue-next'

const auth = useAuthStore()
const isAdmin = computed(() => auth.isAdmin || auth.isVorstand)

const alben = ref([])
const loading = ref(true)
const albumDetail = ref(null)
const albumBerechtigung = ref({ darf_hochladen: false, darf_loeschen: false, darf_eigene_loeschen: true, current_mitglied: '' })
const lightbox = ref(null)
const uploading = ref(false)
const uploadProgress = ref('')
const uploadError = ref('')
const showCreate = ref(false)
const showEdit = ref(false)
const creating = ref(false)
const saving = ref(false)
const createError = ref('')
const editError = ref('')
const editTarget = ref(null)

const createForm = ref({ titel: '', datum: new Date().toISOString().split('T')[0], beschreibung: '', oeffentlich: 0 })
const editForm = ref({ titel: '', datum: '', beschreibung: '', oeffentlich: 0 })

const currentFoto = ref(null)
watch(lightbox, (val) => {
  if (val !== null) currentFoto.value = albumDetail.value?.fotos?.[val] ?? null
})

onMounted(() => load())

async function load() {
  loading.value = true
  try { alben.value = await api.call('dms_verein.api.verein.get_alben_liste') || [] }
  finally { loading.value = false }
}

async function openAlbum(a) {
  const [detail, berechtigung] = await Promise.all([
    api.call('dms_verein.api.verein.get_album_detail', { name: a.name }),
    api.call('dms_verein.api.verein.get_album_berechtigung', { album_name: a.name }).catch(() => ({ darf_hochladen: true, darf_loeschen: false })),
  ])
  albumDetail.value = detail
  albumBerechtigung.value = berechtigung || { darf_hochladen: true, darf_loeschen: false, darf_eigene_loeschen: true, current_mitglied: '' }
  uploadError.value = ''
  lightbox.value = null
}

function openCreate() {
  createForm.value = { titel: '', datum: new Date().toISOString().split('T')[0], beschreibung: '', oeffentlich: 0 }
  createError.value = ''
  showCreate.value = true
}

function openEdit(a) {
  editTarget.value = a
  editForm.value = { titel: a.titel || '', datum: a.datum?.split(' ')[0] || '', beschreibung: a.beschreibung || '', oeffentlich: a.oeffentlich ?? 0 }
  editError.value = ''
  showEdit.value = true
}

function openLightbox(idx) { lightbox.value = idx }

async function handleUpload(event) {
  const files = Array.from(event.target.files)
  if (!files.length || !albumDetail.value) return
  uploading.value = true
  uploadError.value = ''

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    uploadProgress.value = `Lade hoch: ${file.name} (${i + 1}/${files.length})`
    try {
      const fileUrl = await api.uploadFile(file, 'Fotoalbum', albumDetail.value.name)
      if (!fileUrl) throw new Error('Upload fehlgeschlagen – keine Datei-URL erhalten')
      const updated = await api.call('dms_verein.api.verein.add_foto_to_album', {
        album_name: albumDetail.value.name,
        datei: fileUrl,
        titel: file.name.replace(/\.[^.]+$/, ''),
        datum: '',
        aufgenommen_von: '',
      })
      albumDetail.value = updated
    } catch (e) {
      uploadError.value = `Fehler bei „${file.name}": ${e.message}`
      break
    }
  }

  uploading.value = false
  uploadProgress.value = ''
  event.target.value = ''
  await load()
}

async function deleteFoto(foto) {
  if (!confirm(`Foto wirklich löschen?`)) return
  try {
    const updated = await api.call('dms_verein.api.verein.delete_foto_from_album', {
      album_name: albumDetail.value.name,
      foto_name: foto.name,
    })
    albumDetail.value = updated
    await load()
  } catch (e) { alert('Fehler: ' + e.message) }
}

async function deleteFotoAndClose(foto) {
  if (!confirm(`Foto wirklich löschen?`)) return
  try {
    const updated = await api.call('dms_verein.api.verein.delete_foto_from_album', {
      album_name: albumDetail.value.name,
      foto_name: foto.name,
    })
    lightbox.value = null
    albumDetail.value = updated
    await load()
  } catch (e) { alert('Fehler: ' + e.message) }
}

async function setTitelbild(foto) {
  try {
    await api.call('dms_verein.api.verein.set_album_titelbild', {
      album_name: albumDetail.value.name,
      datei: foto.datei,
    })
    albumDetail.value = { ...albumDetail.value, titelbild: foto.datei }
    await load()
  } catch (e) { alert('Fehler: ' + e.message) }
}

async function createAlbum() {
  creating.value = true
  createError.value = ''
  try {
    const newDoc = await api.insertDoc({ doctype: 'Fotoalbum', ...createForm.value })
    showCreate.value = false
    await load()
    if (newDoc?.name) await openAlbum({ name: newDoc.name })
  } catch (e) { createError.value = e.message }
  finally { creating.value = false }
}

async function saveEdit() {
  saving.value = true
  editError.value = ''
  try {
    await api.updateRecord('Fotoalbum', editTarget.value.name, editForm.value)
    showEdit.value = false
    if (albumDetail.value?.name === editTarget.value.name) {
      albumDetail.value = { ...albumDetail.value, ...editForm.value }
    }
    await load()
  } catch (e) { editError.value = e.message }
  finally { saving.value = false }
}

async function deleteAlbum(a) {
  if (!confirm(`Album „${a.titel}" und alle Fotos wirklich löschen?`)) return
  try {
    await api.deleteRecord('Fotoalbum', a.name)
    albumDetail.value = null
    await load()
  } catch (e) { alert('Fehler: ' + e.message) }
}

const formatDate = (d) => d
  ? new Date(d).toLocaleDateString('de-DE', { day: 'numeric', month: 'long', year: 'numeric' })
  : '—'
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
