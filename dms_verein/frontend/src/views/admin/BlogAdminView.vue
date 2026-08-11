<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Blog-Verwaltung</h1>
        <p class="text-slate-500 text-sm mt-0.5">Beiträge erstellen und verwalten</p>
      </div>
      <div class="flex items-center gap-2">
        <button v-if="istAdmin" @click="showKategorien = true" class="btn btn-secondary btn-sm">
          <Tag :size="14" /> Kategorien
        </button>
        <button @click="openNew" class="btn btn-primary btn-sm flex items-center gap-1.5">
          <Plus :size="15" /> Neuer Beitrag
        </button>
      </div>
    </div>

    <!-- Filter -->
    <div class="card card-body flex flex-wrap gap-3 items-center">
      <input v-model="search" type="text" placeholder="Titel suchen…" class="input flex-1 min-w-48" />
      <select v-model="filterStatus" class="input w-44">
        <option value="">Alle Status</option>
        <option value="Entwurf">Entwurf</option>
        <option value="Veröffentlicht">Veröffentlicht</option>
      </select>
    </div>

    <!-- Tabelle -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="p-8 text-center">
        <div class="w-6 h-6 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto" />
      </div>
      <div v-else-if="gefiltert.length === 0" class="p-10 text-center">
        <div class="text-4xl mb-3">📭</div>
        <p class="text-slate-500">Keine Beiträge gefunden.</p>
      </div>
      <table v-else class="w-full text-sm">
        <thead class="bg-slate-50 border-b border-slate-200 text-xs uppercase text-slate-500">
          <tr>
            <th class="text-left px-4 py-3">Titel</th>
            <th class="text-left px-4 py-3 hidden sm:table-cell">Kategorie</th>
            <th class="text-left px-4 py-3 hidden md:table-cell">Autor</th>
            <th class="text-left px-4 py-3 hidden md:table-cell">Datum</th>
            <th class="text-left px-4 py-3">Status</th>
            <th class="px-4 py-3" />
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="b in gefiltert" :key="b.name" class="hover:bg-slate-50 transition-colors">
            <td class="px-4 py-3 font-medium text-slate-800">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-slate-100 overflow-hidden shrink-0">
                  <img v-if="b.beitragsbild" :src="b.beitragsbild" class="w-full h-full object-cover" />
                  <div v-else class="w-full h-full flex items-center justify-center text-lg">📰</div>
                </div>
                <span class="line-clamp-2">{{ b.titel }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-slate-500 hidden sm:table-cell">{{ b.kategorie_bezeichnung || b.kategorie || '—' }}</td>
            <td class="px-4 py-3 text-slate-500 hidden md:table-cell">{{ b.autor }}</td>
            <td class="px-4 py-3 text-slate-500 hidden md:table-cell">{{ formatDatum(b.veroeffentlicht_am) }}</td>
            <td class="px-4 py-3">
              <span :class="b.status === 'Veröffentlicht'
                ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'"
                class="text-xs px-2 py-0.5 rounded-full font-medium">{{ b.status }}</span>
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-1 justify-end">
                <a :href="`/verein/blog/${b.slug || b.name}`" target="_blank"
                  class="p-1.5 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors" title="Vorschau">
                  <Eye :size="15" />
                </a>
                <RouterLink :to="`/admin/blog/${b.name}/baukasten`"
                  class="p-1.5 rounded hover:bg-violet-100 text-slate-400 hover:text-violet-700 transition-colors" title="Baukasten">
                  <Layers :size="15" />
                </RouterLink>
                <button @click="openEdit(b)"
                  class="p-1.5 rounded hover:bg-primary-100 text-slate-400 hover:text-primary-700 transition-colors" title="Basisfelder bearbeiten">
                  <Pencil :size="15" />
                </button>
                <button v-if="istAdmin" @click="confirmDelete(b)"
                  class="p-1.5 rounded hover:bg-red-100 text-slate-400 hover:text-red-600 transition-colors">
                  <Trash2 :size="15" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Beitrag bearbeiten / erstellen -->
    <AppModal :show="showForm" :title="form.name ? 'Beitrag bearbeiten' : 'Neuer Beitrag'" size="xl" @close="showForm = false">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div class="sm:col-span-2 space-y-4">
          <div class="form-group">
            <label class="label">Titel *</label>
            <input v-model="form.titel" class="input" placeholder="Beitragstitel" required />
          </div>
          <div class="form-group">
            <label class="label">Kurzfassung / Teaser</label>
            <textarea v-model="form.zusammenfassung" class="input" rows="3"
              placeholder="Kurze Beschreibung für die Übersichtsseite (ca. 200 Zeichen)" />
          </div>
          <div class="form-group">
            <label class="label">Inhalt</label>
            <RichTextEditor v-model="form.inhalt" />
          </div>
        </div>
        <div class="space-y-4">
          <div class="form-group">
            <label class="label">Status</label>
            <select v-model="form.status" class="input">
              <option value="Entwurf">Entwurf</option>
              <option value="Veröffentlicht">Veröffentlicht</option>
            </select>
          </div>
          <div class="form-group">
            <label class="label">Veröffentlicht am</label>
            <input v-model="form.veroeffentlicht_am" type="date" class="input" />
          </div>
          <div class="form-group">
            <label class="label">Kategorie</label>
            <select v-model="form.kategorie" class="input">
              <option value="">— keine —</option>
              <option v-for="k in kategorien" :key="k.name" :value="k.name">{{ k.bezeichnung }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="label">Titelbild</label>
            <div v-if="form.beitragsbild" class="mb-2 relative inline-block">
              <img :src="form.beitragsbild" class="h-24 w-auto rounded-lg border border-slate-200 object-cover" />
              <button @click="form.beitragsbild = ''"
                class="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center">×</button>
            </div>
            <label class="cursor-pointer block">
              <span class="btn btn-secondary btn-sm flex items-center gap-1.5 w-full justify-center">
                <Upload :size="13" /> Bild wählen
              </span>
              <input type="file" class="hidden" accept="image/*" @change="uploadTitelbild" />
            </label>
          </div>
        </div>
      </div>
      <template #footer>
        <button @click="showForm = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="save" :disabled="saving" class="btn btn-primary">
          {{ saving ? 'Wird gespeichert…' : 'Speichern' }}
        </button>
      </template>
    </AppModal>

    <!-- Kategorien verwalten -->
    <AppModal :show="showKategorien" title="Blog-Kategorien" size="md" @close="showKategorien = false">
      <div class="space-y-3 mb-4">
        <div v-for="k in kategorien" :key="k.name"
          class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
          <span class="flex-1 font-medium text-slate-800">{{ k.bezeichnung }}</span>
          <button @click="editKategorie(k)" class="p-1.5 rounded hover:bg-slate-200 text-slate-500"><Pencil :size="14" /></button>
        </div>
        <div v-if="kategorien.length === 0" class="text-slate-400 text-sm text-center py-4">Noch keine Kategorien</div>
      </div>
      <div class="border-t border-slate-200 pt-4 flex gap-2">
        <input v-model="neueKat.bezeichnung" class="input flex-1" placeholder="Neue Kategorie" @keydown.enter="addKategorie" />
        <button @click="addKategorie" class="btn btn-primary btn-sm">Hinzufügen</button>
      </div>
    </AppModal>

    <!-- Löschen bestätigen -->
    <AppModal :show="showDelete" title="Beitrag löschen?" size="sm" @close="showDelete = false">
      <p class="text-slate-600">Soll der Beitrag <strong>„{{ toDelete?.titel }}"</strong> wirklich unwiderruflich gelöscht werden?</p>
      <template #footer>
        <button @click="showDelete = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="doDelete" :disabled="saving" class="btn btn-danger">Löschen</button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import { RouterLink } from 'vue-router'
import { Plus, Pencil, Trash2, Eye, Tag, Upload, Layers } from 'lucide-vue-next'
import AppModal from '@/components/ui/AppModal.vue'
import RichTextEditor from '@/components/builder/RichTextEditor.vue'

const api = useApi()
const auth = useAuthStore()
const istAdmin = computed(() => auth.canAccessAdmin)

const beitraege = ref([])
const kategorien = ref([])
const loading = ref(true)
const showForm = ref(false)
const showKategorien = ref(false)
const showDelete = ref(false)
const saving = ref(false)
const search = ref('')
const filterStatus = ref('')
const toDelete = ref(null)
const neueKat = ref({ bezeichnung: '' })

const form = ref(emptyForm())

function emptyForm() {
  return {
    name: '', titel: '', inhalt: '', zusammenfassung: '',
    beitragsbild: '', kategorie: '', status: 'Entwurf', veroeffentlicht_am: '',
  }
}

const gefiltert = computed(() => {
  let r = beitraege.value
  if (search.value) {
    const q = search.value.toLowerCase()
    r = r.filter(b => b.titel?.toLowerCase().includes(q))
  }
  if (filterStatus.value) r = r.filter(b => b.status === filterStatus.value)
  return r
})

async function load() {
  loading.value = true
  try {
    const res = await api.call('dms_verein.api.verein.get_blog_liste_admin')
    beitraege.value = res.items || []
  } finally {
    loading.value = false
  }
}

async function loadKategorien() {
  kategorien.value = await api.call('dms_verein.api.verein.get_blog_kategorien')
}

function openNew() {
  form.value = emptyForm()
  showForm.value = true
}

async function openEdit(b) {
  // Vollständiges Dokument holen — Liste enthält kein inhalt/zusammenfassung
  try {
    const full = await api.getDoc('Blog Beitrag', b.name)
    form.value = {
      name: full.name,
      titel: full.titel || '',
      slug: full.slug || '',
      inhalt: full.inhalt || '',
      zusammenfassung: full.zusammenfassung || '',
      beitragsbild: full.beitragsbild || '',
      kategorie: full.kategorie || '',
      status: full.status || 'Entwurf',
      veroeffentlicht_am: full.veroeffentlicht_am || '',
    }
  } catch {
    form.value = { ...b, inhalt: '', zusammenfassung: '' }
  }
  showForm.value = true
}

async function save() {
  if (!form.value.titel) return
  saving.value = true
  try {
    await api.call('dms_verein.api.verein.save_blog_beitrag', { data: JSON.stringify(form.value) })
    showForm.value = false
    await load()
  } finally {
    saving.value = false
  }
}

async function uploadTitelbild(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const url = await api.uploadFile(file)
  form.value.beitragsbild = url
  e.target.value = ''
}

function confirmDelete(b) {
  toDelete.value = b
  showDelete.value = true
}

async function doDelete() {
  saving.value = true
  try {
    await api.call('dms_verein.api.verein.delete_blog_beitrag', { name: toDelete.value.name })
    showDelete.value = false
    toDelete.value = null
    await load()
  } finally {
    saving.value = false
  }
}

async function addKategorie() {
  if (!neueKat.value.bezeichnung) return
  await api.call('dms_verein.api.verein.save_blog_kategorie', {
    data: JSON.stringify(neueKat.value)
  })
  neueKat.value.bezeichnung = ''
  await loadKategorien()
}

function editKategorie(k) {
  neueKat.value = { ...k }
}

function formatDatum(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

onMounted(async () => {
  await Promise.all([load(), loadKategorien()])
})
</script>
