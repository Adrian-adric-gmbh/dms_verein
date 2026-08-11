<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Mein Blog</h1>
        <p class="text-slate-500 text-sm mt-0.5">Deine Beiträge erstellen und verwalten</p>
      </div>
      <button @click="openNew" class="btn btn-primary btn-sm flex items-center gap-1.5">
        <Plus :size="15" /> Neuer Beitrag
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-6 h-6 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
    </div>

    <div v-else-if="beitraege.length === 0" class="card p-10 text-center">
      <div class="text-4xl mb-3">✍️</div>
      <p class="text-slate-500">Noch keine Beiträge.</p>
      <button @click="openNew" class="btn btn-primary btn-sm mt-4">Ersten Beitrag erstellen</button>
    </div>

    <div v-else class="space-y-3">
      <div v-for="b in beitraege" :key="b.name"
        class="card card-body flex flex-col sm:flex-row sm:items-center gap-4">
        <div class="w-16 h-16 rounded-lg bg-slate-100 overflow-hidden shrink-0">
          <img v-if="b.beitragsbild" :src="b.beitragsbild" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center text-2xl">📰</div>
        </div>
        <div class="flex-1 min-w-0">
          <div class="font-semibold text-slate-800 truncate">{{ b.titel }}</div>
          <div class="text-xs text-slate-400 mt-0.5 flex items-center gap-2 flex-wrap">
            <span :class="b.status === 'Veröffentlicht' ? 'text-green-600' : 'text-amber-600'" class="font-medium">
              {{ b.status }}
            </span>
            <span v-if="b.veroeffentlicht_am">· {{ formatDatum(b.veroeffentlicht_am) }}</span>
            <span v-if="b.kategorie">· {{ b.kategorie }}</span>
          </div>
        </div>
        <div class="flex items-center gap-1.5 shrink-0">
          <a v-if="b.status === 'Veröffentlicht' && b.slug"
            :href="`/verein/blog/${b.slug}`" target="_blank"
            class="p-2 rounded-lg hover:bg-slate-100 text-slate-400">
            <Eye :size="16" />
          </a>
          <RouterLink :to="`/portal/blog/${b.name}/baukasten`"
            class="p-2 rounded-lg hover:bg-primary-100 text-primary-600">
            <Layers :size="16" />
          </RouterLink>
          <button @click="openEdit(b)" class="p-2 rounded-lg hover:bg-slate-100 text-slate-500">
            <Pencil :size="16" />
          </button>
        </div>
      </div>
    </div>

    <!-- Beitrag anlegen / bearbeiten -->
    <AppModal :show="showForm" :title="form.name ? 'Beitrag bearbeiten' : 'Neuer Beitrag'" size="lg" @close="showForm = false">
      <div class="space-y-4">
        <div class="form-group">
          <label class="label">Titel *</label>
          <input v-model="form.titel" class="input" placeholder="Beitragstitel" />
        </div>
        <div class="form-group">
          <label class="label">Kurzfassung / Teaser</label>
          <textarea v-model="form.zusammenfassung" class="input" rows="2"
            placeholder="Kurze Beschreibung für die Blog-Übersicht" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="form-group">
            <label class="label">Status</label>
            <select v-model="form.status" class="input">
              <option value="Entwurf">Entwurf</option>
              <option value="Veröffentlicht">Veröffentlicht</option>
            </select>
          </div>
          <div class="form-group">
            <label class="label">Kategorie</label>
            <select v-model="form.kategorie" class="input">
              <option value="">— keine —</option>
              <option v-for="k in kategorien" :key="k.name" :value="k.name">{{ k.bezeichnung }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="label">Titelbild</label>
          <div v-if="form.beitragsbild" class="mb-2 relative inline-block">
            <img :src="form.beitragsbild" class="h-20 w-auto rounded-lg border border-slate-200 object-cover" />
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
      <template #footer>
        <button @click="showForm = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="save" :disabled="saving" class="btn btn-primary">
          {{ saving ? 'Wird gespeichert…' : 'Speichern' }}
        </button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '@/utils/api'
import { Plus, Pencil, Eye, Layers, Upload } from 'lucide-vue-next'
import AppModal from '@/components/ui/AppModal.vue'

const api = useApi()
const beitraege = ref([])
const kategorien = ref([])
const loading = ref(true)
const showForm = ref(false)
const saving = ref(false)

const form = ref(emptyForm())

function emptyForm() {
  return { name: '', titel: '', zusammenfassung: '', beitragsbild: '', kategorie: '', status: 'Entwurf' }
}

async function load() {
  loading.value = true
  try {
    beitraege.value = await api.call('dms_verein.api.verein.get_meine_blog_beitraege')
  } finally {
    loading.value = false
  }
}

async function loadKategorien() {
  kategorien.value = await api.call('dms_verein.api.verein.get_blog_kategorien').catch(() => [])
}

function openNew() {
  form.value = emptyForm()
  showForm.value = true
}

function openEdit(b) {
  form.value = { name: b.name, titel: b.titel || '', zusammenfassung: '',
    beitragsbild: b.beitragsbild || '', kategorie: b.kategorie || '', status: b.status || 'Entwurf' }
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

function formatDatum(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: 'long', year: 'numeric' })
}

onMounted(async () => {
  await Promise.all([load(), loadKategorien()])
})
</script>
