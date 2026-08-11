<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Topbar -->
    <div class="bg-white border-b border-slate-200 sticky top-0 z-30">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3">
        <RouterLink to="/admin/blog"
          class="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors text-sm">
          <ChevronLeft :size="18" />
          Blog-Verwaltung
        </RouterLink>
        <span class="text-slate-300">/</span>
        <span class="text-slate-700 font-medium text-sm truncate max-w-[200px]">{{ beitrag?.titel || beitragName }}</span>
        <span class="text-slate-300">/</span>
        <span class="text-slate-900 font-semibold text-sm flex items-center gap-1.5">
          <Layers :size="15" /> Seiten-Baukasten
        </span>
        <div class="ml-auto flex items-center gap-2">
          <a v-if="beitrag?.slug" :href="`/verein/blog/${beitrag.slug}`" target="_blank"
            class="btn btn-sm flex items-center gap-1.5">
            <Eye :size="15" /> Vorschau
          </a>
          <button @click="saveAll" :disabled="saving || !dirty"
            class="btn btn-primary btn-sm flex items-center gap-1.5">
            <Save :size="15" />
            <span>{{ saving ? 'Speichern…' : 'Speichern' }}</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
    </div>

    <div v-else class="max-w-7xl mx-auto px-4 py-6">
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">

        <!-- Block-Palette -->
        <div class="lg:col-span-1">
          <div class="card sticky top-20">
            <div class="card-header">
              <h3 class="font-semibold text-slate-800 flex items-center gap-2">
                <Plus :size="16" /> Block hinzufügen
              </h3>
            </div>
            <div class="card-body p-3 space-y-1.5">
              <button v-for="bt in BLOCK_TYPEN" :key="bt.typ"
                @click="addBlock(bt.typ)"
                class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border border-slate-200 bg-white
                       hover:border-primary-400 hover:bg-primary-50 transition-all group text-left">
                <span class="text-xl w-7 text-center">{{ bt.icon }}</span>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-slate-700 group-hover:text-primary-700">{{ bt.typ }}</div>
                  <div class="text-xs text-slate-400 truncate">{{ bt.hint }}</div>
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- Canvas -->
        <div class="lg:col-span-3 space-y-3">
          <div v-if="sektionen.length === 0"
            class="card flex flex-col items-center justify-center py-16 text-center border-2 border-dashed border-slate-200">
            <Layers :size="36" class="text-slate-300 mb-3" />
            <p class="text-slate-500 font-medium">Noch keine Blöcke</p>
            <p class="text-slate-400 text-sm mt-1">Klicke links auf einen Block-Typ, um zu beginnen</p>
          </div>

          <div v-for="(sektion, idx) in sektionen" :key="sektion._id"
            draggable="true"
            @dragstart="onDragStart(idx)"
            @dragover.prevent="dragOverIdx = idx"
            @drop.prevent="onDrop(idx)"
            @dragend="dragFromIdx = null; dragOverIdx = null"
            class="card overflow-hidden transition-all"
            :class="{
              'ring-2 ring-primary-400': editIdx === idx,
              'opacity-40 scale-[0.98]': dragFromIdx === idx,
              'border-t-2 border-primary-500': dragOverIdx === idx && dragOverIdx !== dragFromIdx,
            }">

            <div class="flex items-center gap-3 px-4 py-3 bg-slate-50 border-b border-slate-200 cursor-grab active:cursor-grabbing">
              <GripVertical :size="16" class="text-slate-300 shrink-0" />
              <span class="text-lg">{{ blockIcon(sektion.typ) }}</span>
              <span class="text-sm font-semibold text-slate-700 flex-1">
                {{ sektion.typ }}
                <span v-if="sektion.titel" class="font-normal text-slate-400 ml-1.5">— {{ sektion.titel }}</span>
              </span>
              <span class="text-xs px-2 py-0.5 rounded-full border"
                :class="bgBadgeClass(sektion.hintergrund)">{{ sektion.hintergrund || 'Weiß' }}</span>
              <div class="flex items-center gap-1">
                <button @click="moveUp(idx)" :disabled="idx === 0"
                  class="p-1.5 rounded hover:bg-slate-200 text-slate-400 disabled:opacity-30">
                  <ChevronUp :size="16" />
                </button>
                <button @click="moveDown(idx)" :disabled="idx === sektionen.length - 1"
                  class="p-1.5 rounded hover:bg-slate-200 text-slate-400 disabled:opacity-30">
                  <ChevronDown :size="16" />
                </button>
                <button @click="editIdx = editIdx === idx ? null : idx"
                  class="p-1.5 rounded hover:bg-primary-100 text-slate-400 hover:text-primary-700">
                  <Pencil :size="16" />
                </button>
                <button @click="deleteBlock(idx)"
                  class="p-1.5 rounded hover:bg-red-100 text-slate-400 hover:text-red-600">
                  <Trash2 :size="16" />
                </button>
              </div>
            </div>

            <div class="px-4 py-3 text-sm text-slate-500">
              <BlogBlockPreview :sektion="sektion" />
            </div>

            <Transition
              enter-active-class="transition-all duration-200 ease-out"
              enter-from-class="opacity-0 -translate-y-2"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition-all duration-150 ease-in"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 -translate-y-2">
              <div v-if="editIdx === idx" class="border-t border-primary-100 bg-primary-50/30 px-4 py-5">
                <BlogBlockEditor :sektion="sektion" @update="(val) => updateSektion(idx, val)" />
              </div>
            </Transition>
          </div>
        </div>
      </div>

      <!-- Live-Vorschau -->
      <div class="mt-8 lg:col-span-4">
        <button @click="vorschauOffen = !vorschauOffen"
          class="w-full flex items-center justify-between px-4 py-3 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors">
          <span class="font-semibold text-slate-700 flex items-center gap-2">
            <Eye :size="16" /> Live-Vorschau
          </span>
          <ChevronDown :size="16" class="text-slate-400 transition-transform"
            :class="vorschauOffen ? 'rotate-180' : ''" />
        </button>
        <div v-if="vorschauOffen"
          class="mt-3 border border-slate-200 rounded-xl overflow-hidden bg-white shadow-inner">
          <div class="bg-slate-100 px-4 py-2 text-xs text-slate-500 border-b border-slate-200">
            Vorschau — so sieht der Beitrag für Leser aus
          </div>
          <BlogSektionenRenderer :sektionen="sektionen" />
          <div v-if="sektionen.length === 0" class="py-12 text-center text-slate-400 text-sm">
            Noch keine Blöcke vorhanden.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useApi } from '@/utils/api'
import { ChevronLeft, ChevronUp, ChevronDown, Pencil, Trash2, Layers, Plus, Eye, Save, GripVertical } from 'lucide-vue-next'
import BlogBlockPreview from '@/components/builder/BlogBlockPreview.vue'
import BlogBlockEditor from '@/components/builder/BlogBlockEditor.vue'
import BlogSektionenRenderer from '@/components/blog/BlogSektionenRenderer.vue'

const route = useRoute()
const api = useApi()
const beitragName = computed(() => route.params.name)

const beitrag = ref(null)
const sektionen = ref([])
const loading = ref(true)
const saving = ref(false)
const dirty = ref(false)
const editIdx = ref(null)
const dragFromIdx = ref(null)
const dragOverIdx = ref(null)
const vorschauOffen = ref(false)

let _id = 0
function mkId() { return ++_id }

const BLOCK_TYPEN = [
  { typ: 'Text',      icon: '📝', hint: 'Rich-Text Abschnitt' },
  { typ: 'Bild',      icon: '🖼️', hint: 'Einzelbild mit Beschriftung' },
  { typ: 'Text & Bild', icon: '🗂️', hint: 'Text neben Bild (2-spaltig)' },
  { typ: 'Diashow',   icon: '▶️', hint: 'Automatisch laufende Bildshow' },
  { typ: 'Galerie',   icon: '🏞️', hint: 'Foto-Galerie Raster' },
  { typ: 'Video',     icon: '🎬', hint: 'YouTube / Vimeo Einbettung' },
  { typ: 'Zitat',     icon: '💬', hint: 'Blockquote mit Quelle' },
  { typ: 'Info-Box',  icon: '📌', hint: 'Farbiger Hinweis-Kasten' },
  { typ: 'Trenner',   icon: '➖', hint: 'Optischer Abstandhalter' },
  { typ: 'HTML-Block', icon: '🔧', hint: 'Freies HTML / Embed-Code' },
]

function blockIcon(typ) {
  return BLOCK_TYPEN.find(b => b.typ === typ)?.icon || '📦'
}

function bgBadgeClass(hg) {
  const map = {
    'Hellgrau': 'bg-slate-100 border-slate-200 text-slate-600',
    'Primärfarbe': 'bg-primary-100 border-primary-200 text-primary-700',
    'Dunkel': 'bg-slate-800 border-slate-700 text-white',
  }
  return map[hg] || 'bg-white border-slate-200 text-slate-500'
}

async function load() {
  loading.value = true
  try {
    const data = await api.call('dms_verein.api.verein.get_blog_beitrag_admin', { name: beitragName.value })
    beitrag.value = data
    sektionen.value = (data.sektionen || []).map(s => ({ ...s, _id: mkId() }))
  } finally {
    loading.value = false
  }
}

function addBlock(typ) {
  sektionen.value.push({
    _id: mkId(), typ, hintergrund: 'Weiß',
    titel: '', text: '', bild: '', bildunterschrift: '',
    bild_ausrichtung: 'Rechts', bilder: '', video_url: '',
    zitat_autor: '', info_typ: 'Info', autoplay: 1, html_inhalt: '',
  })
  editIdx.value = sektionen.value.length - 1
  dirty.value = true
}

function updateSektion(idx, val) {
  sektionen.value[idx] = { ...sektionen.value[idx], ...val }
  dirty.value = true
}

function moveUp(idx) {
  if (idx === 0) return
  const arr = [...sektionen.value]
  ;[arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]]
  sektionen.value = arr
  if (editIdx.value === idx) editIdx.value = idx - 1
  else if (editIdx.value === idx - 1) editIdx.value = idx
  dirty.value = true
}

function moveDown(idx) {
  if (idx === sektionen.value.length - 1) return
  const arr = [...sektionen.value]
  ;[arr[idx], arr[idx + 1]] = [arr[idx + 1], arr[idx]]
  sektionen.value = arr
  if (editIdx.value === idx) editIdx.value = idx + 1
  else if (editIdx.value === idx + 1) editIdx.value = idx
  dirty.value = true
}

function deleteBlock(idx) {
  sektionen.value.splice(idx, 1)
  if (editIdx.value === idx) editIdx.value = null
  else if (editIdx.value > idx) editIdx.value--
  dirty.value = true
}

function onDragStart(idx) {
  dragFromIdx.value = idx
  editIdx.value = null
}

function onDrop(toIdx) {
  const from = dragFromIdx.value
  if (from === null || from === toIdx) return
  const arr = [...sektionen.value]
  const [item] = arr.splice(from, 1)
  arr.splice(toIdx, 0, item)
  sektionen.value = arr
  dragFromIdx.value = null
  dragOverIdx.value = null
  dirty.value = true
}

async function saveAll() {
  saving.value = true
  try {
    await api.call('dms_verein.api.verein.save_blog_sektionen', {
      beitrag_name: beitragName.value,
      sektionen: JSON.stringify(sektionen.value.map(({ _id, ...s }) => s)),
    })
    dirty.value = false
    editIdx.value = null
    await load()
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
