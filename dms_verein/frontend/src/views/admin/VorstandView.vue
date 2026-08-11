<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2>Vorstand</h2><p class="text-slate-500 mt-1">Vorstandsmitglieder und Ämter verwalten</p></div>
      <button @click="openCreate" class="btn btn-primary"><Plus :size="16" /> Hinzufügen</button>
    </div>

    <AppSpinner v-if="loading" full-page />
    <div v-else>
      <!-- Aktuelle Amtsinhaber -->
      <div v-if="aktive.length" class="mb-8">
        <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">Aktuell im Amt</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="v in aktive" :key="v.name"
            class="card card-body cursor-pointer hover:shadow-md transition-all"
            @click="openDetail(v)">
            <div class="flex items-start gap-3">
              <div class="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold text-lg shrink-0">
                {{ (v.mitglied_name || v.mitglied)?.[0]?.toUpperCase() || '?' }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold truncate">{{ v.mitglied_name || v.mitglied }}</p>
                <p class="text-sm font-medium" style="color: var(--color-primary)">{{ v.position }}</p>
                <p class="text-xs text-slate-400 mt-0.5">seit {{ formatDate(v.amtsperiode_von) }}</p>
                <div v-if="v.email_dienstlich || v.telefon_dienstlich" class="flex flex-wrap gap-x-3 mt-1.5">
                  <span v-if="v.email_dienstlich" class="text-xs text-slate-400 flex items-center gap-1">
                    <Mail :size="10" /> {{ v.email_dienstlich }}
                  </span>
                  <span v-if="v.telefon_dienstlich" class="text-xs text-slate-400 flex items-center gap-1">
                    <Phone :size="10" /> {{ v.telefon_dienstlich }}
                  </span>
                </div>
              </div>
              <button @click.stop="openEdit(v)" class="text-slate-300 hover:text-slate-600 transition-colors p-1">
                <Pencil :size="13" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Ehemalige -->
      <div v-if="ehemalige.length">
        <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">Ehemalige Amtsinhaber</h3>
        <div class="table-wrapper">
          <table class="table text-sm">
            <thead><tr><th>Name</th><th>Position</th><th>Von</th><th>Bis</th><th></th></tr></thead>
            <tbody>
              <tr v-for="v in ehemalige" :key="v.name">
                <td class="font-medium">{{ v.mitglied_name || v.mitglied }}</td>
                <td class="text-slate-500">{{ v.position }}</td>
                <td class="text-slate-500">{{ formatDate(v.amtsperiode_von) }}</td>
                <td class="text-slate-500">{{ formatDate(v.amtsperiode_bis) }}</td>
                <td>
                  <div class="flex gap-1">
                    <button @click="openEdit(v)" class="btn btn-secondary btn-sm p-1.5"><Pencil :size="12" /></button>
                    <button @click="deleteEintrag(v)" class="btn btn-danger btn-sm p-1.5"><Trash2 :size="12" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="!vorstand.length" class="card card-body text-center py-12 text-slate-400">
        Noch keine Vorstandsmitglieder erfasst. Klicken Sie auf „Hinzufügen".
      </div>
    </div>

    <!-- Detail Modal -->
    <AppModal v-if="selected && !showEdit" :show="!!selected"
      :title="selected.mitglied_name || selected.mitglied" @close="selected = null">
      <div class="space-y-3 text-sm">
        <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
          <div class="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold text-xl">
            {{ (selected.mitglied_name || selected.mitglied)?.[0]?.toUpperCase() || '?' }}
          </div>
          <div>
            <p class="font-semibold text-base">{{ selected.mitglied_name || selected.mitglied }}</p>
            <p class="font-medium" style="color: var(--color-primary)">{{ selected.position }}</p>
          </div>
          <span :class="['badge ml-auto shrink-0', selected.aktiv ? 'badge-green' : 'badge-gray']">
            {{ selected.aktiv ? 'Im Amt' : 'Ehemaliger' }}
          </span>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div><p class="text-slate-400 text-xs">Amtsantritt</p><p class="font-medium">{{ formatDate(selected.amtsperiode_von) }}</p></div>
          <div><p class="text-slate-400 text-xs">Amtsende</p><p class="font-medium">{{ selected.amtsperiode_bis ? formatDate(selected.amtsperiode_bis) : '— (noch im Amt)' }}</p></div>
          <div v-if="selected.email_dienstlich" class="col-span-2"><p class="text-slate-400 text-xs">E-Mail (dienstlich)</p><p class="font-medium">{{ selected.email_dienstlich }}</p></div>
          <div v-if="selected.telefon_dienstlich"><p class="text-slate-400 text-xs">Telefon (dienstlich)</p><p class="font-medium">{{ selected.telefon_dienstlich }}</p></div>
        </div>
      </div>
      <template #footer>
        <button @click="selected = null" class="btn btn-secondary">Schließen</button>
        <button @click="openEdit(selected)" class="btn btn-secondary"><Pencil :size="14" /> Bearbeiten</button>
        <button @click="deleteEintrag(selected)" class="btn btn-danger"><Trash2 :size="14" /> Löschen</button>
      </template>
    </AppModal>

    <!-- Edit/Create Modal -->
    <AppModal :show="showEdit || showCreate"
      :title="editTarget ? 'Eintrag bearbeiten' : 'Vorstandsmitglied hinzufügen'"
      @close="closeForm">
      <form @submit.prevent="saveForm" class="space-y-4">
        <AppAlert v-if="formError" type="error" :message="formError" />

        <!-- Mitglied-Suche -->
        <div class="form-group">
          <label class="label">Mitglied *</label>
          <div class="relative">
            <input v-model="mitgliedSuche" @input="onMitgliedInput" @blur="hideMitgliedDropdown"
              class="input" placeholder="Name oder Mitgliedsnummer eingeben…" autocomplete="off" />
            <div v-if="mitgliedResults.length && showMitgliedDropdown"
              class="absolute z-50 left-0 right-0 bg-white border border-slate-200 rounded-xl shadow-lg mt-1 overflow-hidden">
              <button v-for="m in mitgliedResults" :key="m.value"
                @mousedown.prevent="selectMitglied(m)"
                class="w-full text-left px-4 py-2.5 text-sm hover:bg-slate-50 border-b border-slate-100 last:border-0">
                <span class="font-medium">{{ m.label }}</span>
                <span class="text-xs text-slate-400 ml-2">{{ m.value }}</span>
              </button>
            </div>
          </div>
          <p v-if="form.mitglied" class="text-xs text-green-600 mt-1">✓ {{ form.mitglied_name || form.mitglied }}</p>
        </div>

        <!-- Position-Dropdown -->
        <div class="form-group">
          <label class="label">Position *</label>
          <select v-model="form.position" class="input" required>
            <option value="">— Position auswählen —</option>
            <optgroup label="Pflichtpositionen (§26 BGB)">
              <option v-for="p in positionen.filter(p => p.pflicht)" :key="p.name" :value="p.name">{{ p.name }}</option>
            </optgroup>
            <optgroup label="Weitere Positionen">
              <option v-for="p in positionen.filter(p => !p.pflicht)" :key="p.name" :value="p.name">{{ p.name }}</option>
            </optgroup>
          </select>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="form-group">
            <label class="label">Amtsantritt *</label>
            <input v-model="form.amtsperiode_von" type="date" class="input" required />
          </div>
          <div class="form-group">
            <label class="label">Amtsende</label>
            <input v-model="form.amtsperiode_bis" type="date" class="input" placeholder="leer = noch im Amt" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="form-group">
            <label class="label">E-Mail (dienstlich)</label>
            <input v-model="form.email_dienstlich" type="email" class="input" placeholder="vorstand@verein.de" />
          </div>
          <div class="form-group">
            <label class="label">Telefon (dienstlich)</label>
            <input v-model="form.telefon_dienstlich" class="input" placeholder="+49…" />
          </div>
        </div>

        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="form.aktiv" type="checkbox" :true-value="1" :false-value="0" class="w-4 h-4" />
          <span class="text-sm">Aktuell im Amt</span>
        </label>
      </form>
      <template #footer>
        <button @click="closeForm" class="btn btn-secondary">Abbrechen</button>
        <button @click="saveForm" :disabled="saving" class="btn btn-primary">
          <Save :size="14" /> {{ saving ? 'Speichert...' : 'Speichern' }}
        </button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { Plus, Pencil, Trash2, Save, Mail, Phone } from 'lucide-vue-next'

const vorstand = ref([])
const positionen = ref([])
const loading = ref(true)
const selected = ref(null)
const editTarget = ref(null)
const showEdit = ref(false)
const showCreate = ref(false)
const saving = ref(false)
const formError = ref('')
const mitgliedSuche = ref('')
const mitgliedResults = ref([])
const showMitgliedDropdown = ref(false)
let mitgliedTimer = null

const blankForm = () => ({
  mitglied: '', mitglied_name: '', position: '',
  amtsperiode_von: new Date().toISOString().split('T')[0],
  amtsperiode_bis: '', aktiv: 1,
  email_dienstlich: '', telefon_dienstlich: ''
})
const form = ref(blankForm())

const aktive    = computed(() => vorstand.value.filter(v => v.aktiv))
const ehemalige = computed(() => vorstand.value.filter(v => !v.aktiv))

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    const [vs, ps] = await Promise.all([
      api.call('dms_verein.api.verein.get_vorstand_liste'),
      api.getList('Vorstandsposition', {
        fields: ['name','bezeichnung','pflichtposition','rang'],
        filters: [['aktiv','=',1]],
        order_by: 'rang asc', limit_page_length: 50
      })
    ])
    vorstand.value  = vs || []
    positionen.value = (ps || []).map(p => ({ name: p.name, pflicht: p.pflichtposition }))
  } finally { loading.value = false }
}

async function onMitgliedInput() {
  showMitgliedDropdown.value = true
  clearTimeout(mitgliedTimer)
  if (mitgliedSuche.value.length < 2) { mitgliedResults.value = []; return }
  mitgliedTimer = setTimeout(async () => {
    try {
      const res = await api.call('dms_verein.api.verein.get_mitglieder_liste_einfach') || []
      const q = mitgliedSuche.value.toLowerCase()
      mitgliedResults.value = res.filter(m => m.label.toLowerCase().includes(q)).slice(0, 8)
    } catch { mitgliedResults.value = [] }
  }, 250)
}
function selectMitglied(m) {
  form.value.mitglied = m.value
  form.value.mitglied_name = m.label
  mitgliedSuche.value = m.label
  mitgliedResults.value = []
  showMitgliedDropdown.value = false
}
function hideMitgliedDropdown() { setTimeout(() => { showMitgliedDropdown.value = false }, 150) }

function openDetail(v) { selected.value = v }
function openCreate() {
  editTarget.value = null; form.value = blankForm()
  mitgliedSuche.value = ''; formError.value = ''; showCreate.value = true
}
function openEdit(v) {
  editTarget.value = v
  form.value = {
    mitglied: v.mitglied, mitglied_name: v.mitglied_name || v.mitglied,
    position: v.position,
    amtsperiode_von: v.amtsperiode_von?.split(' ')[0] || '',
    amtsperiode_bis: v.amtsperiode_bis?.split(' ')[0] || '',
    aktiv: v.aktiv ?? 1,
    email_dienstlich: v.email_dienstlich || '',
    telefon_dienstlich: v.telefon_dienstlich || '',
  }
  mitgliedSuche.value = v.mitglied_name || v.mitglied
  formError.value = ''; selected.value = null; showEdit.value = true
}
function closeForm() { showEdit.value = false; showCreate.value = false; editTarget.value = null }

async function saveForm() {
  if (!form.value.mitglied) { formError.value = 'Bitte ein Mitglied auswählen.'; return }
  if (!form.value.position)  { formError.value = 'Bitte eine Position auswählen.'; return }
  saving.value = true; formError.value = ''
  try {
    const data = { ...form.value }
    delete data.mitglied_name
    if (editTarget.value) { await api.updateRecord('Vorstandsmitglied', editTarget.value.name, data) }
    else { await api.insertDoc({ doctype: 'Vorstandsmitglied', ...data }) }
    closeForm(); await load()
  } catch (e) { formError.value = e.message }
  finally { saving.value = false }
}

async function deleteEintrag(v) {
  if (!confirm(`Eintrag "${v.position}" von ${v.mitglied_name || v.mitglied} wirklich löschen?`)) return
  try { await api.deleteRecord('Vorstandsmitglied', v.name); selected.value = null; await load() }
  catch (e) { alert('Fehler: ' + e.message) }
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE') : '—'
</script>
