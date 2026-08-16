<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2>{{ verein.strukturPlural }}</h2><p class="text-slate-500 mt-1">Gemeinschaften und Gruppen des Vereins</p></div>
      <button @click="openCreate" class="btn btn-primary"><Plus :size="16" /> {{ verein.strukturSingular }} anlegen</button>
    </div>

    <AppSpinner v-if="loading" full-page />
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-if="!sparten.length" class="col-span-full card card-body text-center py-12 text-slate-400">Keine {{ verein.strukturPlural }} vorhanden.</div>
      <div v-for="s in sparten" :key="s.name" class="card hover:shadow-md transition-shadow cursor-pointer overflow-hidden" @click="openDetail(s)">
        <div class="flex">
          <!-- Spartenbild: schmale Spalte links, volle Kartenhöhe -->
          <div v-if="s.bild" class="w-28 shrink-0 overflow-hidden bg-slate-100">
            <img :src="s.bild" class="w-full h-full object-cover object-top" />
          </div>
          <div class="card-body flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-3">
              <div class="text-3xl shrink-0">{{ s.icon || '🏃' }}</div>
              <div class="flex-1 min-w-0">
                <h3 class="text-base truncate">{{ s.name_sparte }}</h3>
                <p v-if="spartenleitungText(s)" class="text-sm text-slate-500 truncate">{{ spartenleitungText(s) }}</p>
              </div>
              <span :class="s.aktiv ? 'badge-green' : 'badge-gray'" class="badge shrink-0">{{ s.aktiv ? 'Aktiv' : 'Inaktiv' }}</span>
            </div>
            <p v-if="s.treffpunkt" class="text-xs text-slate-500 flex items-center gap-1"><MapPin :size="12" /> {{ s.treffpunkt }}</p>
          </div>
        </div>
      </div>
      <button @click="openCreate" class="card border-dashed border-2 border-slate-300 hover:border-primary-400 hover:bg-primary-50 transition-all flex items-center justify-center gap-2 text-slate-400 hover:text-primary-600 p-8 rounded-xl">
        <Plus :size="20" /> {{ verein.strukturSingular }} hinzufügen
      </button>
    </div>

    <!-- ── Detail Modal ──────────────────────────────────────────────────── -->
    <AppModal v-if="selected" :show="!!selected" :title="selected.name_sparte" size="xl" @close="selected = null">
      <div class="flex flex-col lg:flex-row gap-6">

        <!-- Bild links (wenn vorhanden) -->
        <div v-if="selected.bild" class="lg:w-72 shrink-0">
          <img :src="selected.bild" class="w-full h-52 lg:h-full object-cover object-top rounded-xl" />
        </div>

        <!-- Infos rechts -->
        <div class="flex-1 min-w-0 space-y-5">
          <!-- Titel-Zeile -->
          <div class="flex items-center gap-3">
            <span class="text-4xl">{{ selected.icon || '🏃' }}</span>
            <div>
              <h3 class="text-xl font-bold text-slate-900">{{ selected.name_sparte }}</h3>
              <span :class="selected.aktiv ? 'badge-green' : 'badge-gray'" class="badge mt-1">
                {{ selected.aktiv ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </div>
          </div>

          <!-- Info-Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3 text-sm">
            <div v-if="leitung().length" class="flex items-start gap-2 col-span-2">
              <span class="text-slate-400 shrink-0 mt-0.5"><Users :size="14"/></span>
              <div>
                <p class="label text-xs mb-1">{{ verein.strukturLeitung }}</p>
                <div class="flex flex-wrap gap-2">
                  <span v-for="l in leitung()" :key="l.mitglied"
                    class="inline-flex items-center gap-1.5 bg-slate-100 rounded-full px-3 py-1 text-xs font-medium">
                    <span class="w-5 h-5 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-[10px] font-bold">
                      {{ (l.nachname || l.mitglied)?.[0]?.toUpperCase() }}
                    </span>
                    {{ l.nachname }}, {{ l.vorname }}
                    <span class="text-slate-400">· {{ l.funktion }}</span>
                  </span>
                </div>
              </div>
            </div>
            <div v-if="selected.email" class="flex items-start gap-2">
              <span class="text-slate-400 shrink-0 mt-0.5"><Mail :size="14"/></span>
              <div><p class="label text-xs">E-Mail</p><p class="font-medium">{{ selected.email }}</p></div>
            </div>
            <div v-if="selected.treffpunkt" class="flex items-start gap-2">
              <span class="text-slate-400 shrink-0 mt-0.5"><MapPin :size="14"/></span>
              <div><p class="label text-xs">Treffpunkt</p><p class="font-medium">{{ selected.treffpunkt }}</p></div>
            </div>
            <div v-if="selected.gruendungsjahr" class="flex items-start gap-2">
              <span class="text-slate-400 shrink-0 mt-0.5"><Calendar :size="14"/></span>
              <div><p class="label text-xs">Gegründet</p><p class="font-medium">{{ selected.gruendungsjahr }}</p></div>
            </div>
          </div>

          <!-- Beschreibung -->
          <div v-if="selected.beschreibung" class="text-sm text-slate-700 border-t border-slate-100 pt-4 leading-relaxed">
            {{ selected.beschreibung }}
          </div>

          <!-- Aktions-Kacheln -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 border-t border-slate-100 pt-4">
            <button @click="openMitglieder(selected)"
              class="flex flex-col items-center gap-2 p-4 rounded-xl border border-slate-200 hover:border-primary hover:bg-slate-50 transition-all text-sm font-medium text-slate-700">
              <Users :size="20" class="text-slate-400" /> Mitglieder
            </button>
            <button @click="openTermine(selected)"
              class="flex flex-col items-center gap-2 p-4 rounded-xl border border-slate-200 hover:border-primary hover:bg-slate-50 transition-all text-sm font-medium text-slate-700">
              <CalendarDays :size="20" class="text-slate-400" /> Termine
            </button>
            <RouterLink :to="`/admin/sparten/${selected.name}/baukasten`" @click="selected = null"
              class="flex flex-col items-center gap-2 p-4 rounded-xl border border-slate-200 hover:border-primary hover:bg-slate-50 transition-all text-sm font-medium text-slate-700">
              <Layers :size="20" class="text-slate-400" /> Seite gestalten
            </RouterLink>
            <button @click="openEdit(selected)"
              class="flex flex-col items-center gap-2 p-4 rounded-xl border border-slate-200 hover:border-primary hover:bg-slate-50 transition-all text-sm font-medium text-slate-700">
              <Pencil :size="20" class="text-slate-400" /> Bearbeiten
            </button>
          </div>
        </div>
      </div>
      <template #footer>
        <button @click="selected = null" class="btn btn-secondary">Schließen</button>
        <button v-if="auth.isAdmin" @click="deleteSelected(selected)" class="btn btn-danger"><Trash2 :size="14" /> Löschen</button>
      </template>
    </AppModal>

    <!-- ── Edit Modal ────────────────────────────────────────────────────── -->
    <AppModal :show="showEdit" :title="`${verein.strukturSingular} bearbeiten`" size="lg" @close="showEdit = false">
      <form @submit.prevent="saveEdit" class="space-y-4">
        <AppAlert v-if="formError" type="error" :message="formError" />
        <div class="form-group">
          <label class="label">Name (nicht änderbar)</label>
          <input :value="editTarget?.name_sparte" class="input bg-slate-50 cursor-not-allowed" disabled />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="form-group">
            <label class="label">Icon</label>
            <IconPicker v-model="editForm.icon" />
          </div>
          <div class="form-group">
            <label class="label">Farbe</label>
            <input v-model="editForm.farbe" type="color" class="input h-10 cursor-pointer" />
          </div>
        </div>

        <!-- Spartenbild -->
        <div class="form-group">
          <label class="label">Spartenbild</label>
          <div class="space-y-2">
            <div v-if="editForm.bild" class="relative w-full aspect-video rounded-lg overflow-hidden border border-slate-200 bg-slate-50">
              <img :src="editForm.bild" class="w-full h-full object-cover" />
              <button type="button" @click="editForm.bild = ''"
                class="absolute top-2 right-2 bg-white rounded-full p-1 shadow hover:bg-red-50 text-slate-500 hover:text-red-600 transition-colors">
                <X :size="14" />
              </button>
            </div>
            <label class="flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 cursor-pointer font-medium">
              <ImageIcon :size="15" />
              {{ editForm.bild ? 'Anderes Bild wählen' : 'Bild hochladen' }}
              <input type="file" accept="image/*" class="hidden" @change="uploadBild($event, 'edit')" :disabled="uploadingBild" />
            </label>
            <p v-if="uploadingBild" class="text-xs text-slate-400">Wird hochgeladen...</p>
          </div>
        </div>

        <!-- Spartenbeitrag -->
        <div class="border border-slate-200 rounded-xl p-4 space-y-3">
          <h4 class="text-sm font-semibold text-slate-700">Spartenbeitrag (extra)</h4>
          <div class="grid grid-cols-2 gap-3">
            <div class="form-group">
              <label class="label">Betrag (€)</label>
              <input v-model.number="editForm.beitrag" type="number" step="0.01" min="0" class="input" placeholder="0.00" />
            </div>
            <div class="form-group">
              <label class="label">Intervall</label>
              <select v-model="editForm.beitrag_intervall" class="input">
                <option value="">— kein extra Beitrag —</option>
                <option>Jährlich</option>
                <option>Halbjährlich</option>
                <option>Vierteljährlich</option>
                <option>Monatlich</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="label">Bezeichnung</label>
            <input v-model="editForm.beitrag_bezeichnung" class="input" placeholder="z.B. Trainingsbeitrag Schwimmen" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="form-group"><label class="label">Treffpunkt</label><input v-model="editForm.treffpunkt" class="input" /></div>
          <div class="form-group"><label class="label">E-Mail</label><input v-model="editForm.email" type="email" class="input" /></div>
        </div>
        <div class="form-group"><label class="label">Gründungsjahr</label><input v-model="editForm.gruendungsjahr" type="number" class="input" /></div>
        <div class="form-group"><label class="label">Beschreibung</label><textarea v-model="editForm.beschreibung" class="input h-20 resize-none" /></div>
        <label class="flex items-center gap-2 cursor-pointer"><input v-model="editForm.aktiv" type="checkbox" :true-value="1" :false-value="0" class="w-4 h-4" /><span class="text-sm">Aktiv</span></label>
      </form>
      <template #footer>
        <button @click="showEdit = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="openMitglieder(editTarget)" class="btn btn-secondary"><Users :size="14" /> Mitglieder</button>
        <button @click="saveEdit" :disabled="saving" class="btn btn-primary"><Save :size="14" /> {{ saving ? 'Speichert...' : 'Speichern' }}</button>
      </template>
    </AppModal>

    <!-- ── Create Modal ──────────────────────────────────────────────────── -->
    <AppModal :show="showCreate" :title="`${verein.strukturSingular} anlegen`" @close="showCreate = false">
      <form @submit.prevent="createSparte" class="space-y-4">
        <AppAlert v-if="createError" type="error" :message="createError" />
        <div class="form-group">
          <label class="label">Name *</label>
          <input v-model="newSparte.name_sparte" class="input" required />
        </div>
        <div class="form-group">
          <label class="label">Icon</label>
          <IconPicker v-model="newSparte.icon" />
        </div>
        <div class="form-group"><label class="label">Treffpunkt</label><input v-model="newSparte.treffpunkt" class="input" /></div>
      </form>
      <template #footer>
        <button type="button" @click="showCreate = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="createSparte" :disabled="creating" class="btn btn-primary">{{ creating ? 'Erstelle...' : 'Anlegen' }}</button>
      </template>
    </AppModal>

    <!-- ── Mitglieder-Modal ──────────────────────────────────────────────── -->
    <AppModal :show="showMitglieder" :title="`Mitglieder: ${mitgliederSparte?.name_sparte || ''}`" size="lg" @close="showMitglieder = false">
      <div class="space-y-4">
        <AppAlert v-if="mitgliederError" type="error" :message="mitgliederError" />

        <AppSpinner v-if="mitgliederLoading" />

        <div v-else>
          <!-- Mitglied-Liste -->
          <div v-if="!mitgliederList.length" class="text-center py-6 text-slate-400 text-sm">
            Noch keine Mitglieder in dieser Zuordnung.
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="(m, idx) in mitgliederList"
              :key="idx"
              class="flex items-start gap-3 p-3 rounded-xl border border-slate-100 bg-slate-50"
            >
              <!-- Avatar -->
              <div class="shrink-0 w-9 h-9 rounded-full overflow-hidden bg-slate-200 flex items-center justify-center">
                <img v-if="m.foto" :src="m.foto" class="w-full h-full object-cover" />
                <span v-else class="text-sm font-semibold text-slate-500">{{ initials(m) }}</span>
              </div>

              <!-- Info -->
              <div class="flex-1 min-w-0 space-y-2">
                <div class="font-medium text-sm">{{ m.nachname }}, {{ m.vorname }}</div>
                <div class="grid grid-cols-2 gap-2">
                  <div class="form-group">
                    <label class="label text-xs">Funktion</label>
                    <select v-model="m.funktion" class="input text-sm py-1.5">
                      <option value="">— keine Angabe —</option>
                      <option>Spartenleiter</option>
                      <option>Stv. Spartenleiter</option>
                      <option>Trainer</option>
                      <option>Betreuer</option>
                      <option>Kassierer</option>
                      <option>Mitglied</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="label text-xs">Mitglied seit</label>
                    <input v-model="m.von" type="date" class="input text-sm py-1.5" />
                  </div>
                </div>
                <!-- Spartenleiter-Hinweis -->
                <p v-if="m.funktion === 'Spartenleiter' || m.funktion === 'Stv. Spartenleiter'"
                   class="text-xs text-amber-600 flex items-center gap-1">
                  <ShieldCheck :size="12" /> Erhält die Frappe-Rolle "Spartenleiter" beim Speichern
                </p>
              </div>

              <!-- Aktiv-Toggle + Entfernen -->
              <div class="shrink-0 flex flex-col items-center gap-2 pt-1">
                <label class="flex items-center gap-1 text-xs text-slate-500 cursor-pointer">
                  <input v-model="m.aktiv" type="checkbox" :true-value="1" :false-value="0" class="w-3.5 h-3.5" />
                  Aktiv
                </label>
                <button @click="removeMitglied(idx)" class="text-red-400 hover:text-red-600 transition-colors">
                  <UserMinus :size="16" />
                </button>
              </div>
            </div>
          </div>

          <!-- Neues Mitglied hinzufügen -->
          <div class="mt-4 pt-4 border-t border-slate-200">
            <h4 class="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-1.5">
              <UserPlus :size="15" /> Mitglied hinzufügen
            </h4>
            <div class="flex gap-2">
              <select v-model="addMitgliedName" class="input flex-1 text-sm">
                <option value="">Mitglied auswählen…</option>
                <option
                  v-for="opt in mitgliederAuswahl"
                  :key="opt.value"
                  :value="opt.value"
                  :disabled="mitgliederList.some(m => m.mitglied === opt.value)"
                >{{ opt.label }}</option>
              </select>
              <button
                @click="addMitglied"
                :disabled="!addMitgliedName"
                class="btn btn-secondary shrink-0"
              ><UserPlus :size="14" /> Hinzufügen</button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <button @click="showMitglieder = false" class="btn btn-secondary">Abbrechen</button>
        <button @click="saveMitglieder" :disabled="mitgliederSaving" class="btn btn-primary">
          <Save :size="14" /> {{ mitgliederSaving ? 'Speichert…' : 'Speichern' }}
        </button>
      </template>
    </AppModal>

    <!-- ── Termine Modal ─────────────────────────────────────────────────── -->
    <AppModal :show="showTermine" :title="termineSparte ? `Termine: ${termineSparte.name_sparte}` : 'Termine'" size="lg" @close="showTermine = false">
      <div class="space-y-4">
        <AppAlert v-if="termineError" type="error" :message="termineError" />

        <!-- Terminliste -->
        <AppSpinner v-if="termineLoading" />
        <div v-else>
          <div v-if="!termineListe.length" class="text-center py-6 text-slate-400 text-sm">
            Noch keine Termine. Legen Sie den ersten Termin an.
          </div>
          <div v-else class="space-y-2">
            <div v-for="t in termineListe" :key="t.name"
              class="flex items-start gap-3 p-3 rounded-xl border border-slate-100 bg-slate-50">
              <div class="shrink-0 w-12 text-center">
                <div class="text-lg font-bold leading-none" style="color: var(--color-primary)">
                  {{ new Date(t.datum).getDate() }}
                </div>
                <div class="text-xs text-slate-400">{{ monthShortDE(t.datum) }}</div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-sm">{{ t.titel }}</p>
                <p class="text-xs text-slate-500 mt-0.5 flex items-center gap-2 flex-wrap">
                  <span v-if="t.uhrzeit_von">🕐 {{ t.uhrzeit_von.slice(0,5) }}{{ t.uhrzeit_bis ? ` – ${t.uhrzeit_bis.slice(0,5)}` : '' }} Uhr</span>
                  <span v-if="t.treffpunkt">📍 {{ t.treffpunkt }}</span>
                  <span v-if="t.wiederholung && t.wiederholung !== 'Keine'"
                    class="badge badge-blue text-[10px]">🔄 {{ t.wiederholung }}</span>
                  <span v-if="!t.aktiv" class="badge badge-gray text-[10px]">Inaktiv</span>
                </p>
              </div>
              <div class="shrink-0 flex gap-1">
                <button @click="editTermin(t)" class="text-slate-400 hover:text-slate-700 p-1"><Pencil :size="13" /></button>
                <button @click="deleteTermin(t)" class="text-slate-400 hover:text-red-500 p-1"><Trash2 :size="13" /></button>
              </div>
            </div>
          </div>

          <!-- Neuer Termin -->
          <div class="mt-4 border-t border-slate-200 pt-4">
            <h4 class="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-1.5">
              <Plus :size="15" /> {{ terminEdit ? 'Termin bearbeiten' : 'Neuer Termin' }}
            </h4>
            <div class="space-y-3">
              <div class="form-group">
                <label class="label">Titel *</label>
                <input v-model="terminForm.titel" class="input" placeholder="z.B. Vereinstraining" />
              </div>
              <div class="grid grid-cols-3 gap-2">
                <div class="form-group">
                  <label class="label">Datum *</label>
                  <input v-model="terminForm.datum" type="date" class="input" />
                </div>
                <div class="form-group">
                  <label class="label">Beginn</label>
                  <input v-model="terminForm.uhrzeit_von" type="time" class="input" />
                </div>
                <div class="form-group">
                  <label class="label">Ende</label>
                  <input v-model="terminForm.uhrzeit_bis" type="time" class="input" />
                </div>
              </div>
              <div class="form-group">
                <label class="label">Treffpunkt / Ort</label>
                <input v-model="terminForm.treffpunkt" class="input" placeholder="z.B. Vereinsheim, Halle 2" />
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div class="form-group">
                  <label class="label">Wiederholung</label>
                  <select v-model="terminForm.wiederholung" class="input text-sm">
                    <option>Keine</option>
                    <option>Wöchentlich</option>
                    <option>Zweiwöchentlich</option>
                    <option>Monatlich (selber Tag)</option>
                    <option>Monatlich (1. Wochentag)</option>
                    <option>Monatlich (2. Wochentag)</option>
                    <option>Monatlich (3. Wochentag)</option>
                    <option>Monatlich (4. Wochentag)</option>
                  </select>
                </div>
                <div v-if="terminForm.wiederholung !== 'Keine'" class="form-group">
                  <label class="label">Wochentag</label>
                  <select v-model="terminForm.wiederholung_wochentag" class="input text-sm">
                    <option value="">— aus Datum —</option>
                    <option>Montag</option><option>Dienstag</option><option>Mittwoch</option>
                    <option>Donnerstag</option><option>Freitag</option><option>Samstag</option><option>Sonntag</option>
                  </select>
                </div>
              </div>
              <div v-if="terminForm.wiederholung !== 'Keine'" class="form-group">
                <label class="label">Wiederholen bis (leer = 1 Jahr)</label>
                <input v-model="terminForm.wiederholung_bis" type="date" class="input" />
              </div>
              <div class="form-group">
                <label class="label">Beschreibung / Hinweise</label>
                <textarea v-model="terminForm.beschreibung" class="input" rows="2" placeholder="Optionale Hinweise…" />
              </div>
              <div class="flex items-center gap-2">
                <label class="flex items-center gap-2 cursor-pointer text-sm">
                  <input v-model="terminForm.aktiv" type="checkbox" :true-value="1" :false-value="0" class="w-4 h-4" />
                  Aktiv
                </label>
              </div>
              <div class="flex gap-2 justify-end pt-2">
                <button v-if="terminEdit" @click="cancelTerminEdit" class="btn btn-secondary btn-sm">Abbrechen</button>
                <button @click="saveTermin" :disabled="terminSaving || !terminForm.titel || !terminForm.datum"
                  class="btn btn-primary btn-sm">
                  <Save :size="13" /> {{ terminSaving ? 'Speichert…' : (terminEdit ? 'Aktualisieren' : 'Anlegen') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <button @click="showTermine = false" class="btn btn-secondary">Schließen</button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import { useVereinStore } from '@/stores/verein'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { Plus, MapPin, Pencil, Trash2, Save, Layers, X, Image as ImageIcon,
         Users, UserPlus, UserMinus, ShieldCheck, Mail, Calendar, CalendarDays } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'
import IconPicker from '@/components/ui/IconPicker.vue'

const auth = useAuthStore()
const verein = useVereinStore()

const sparten = ref([])
const loading = ref(true)
const selected = ref(null)
const editTarget = ref(null)
const showEdit = ref(false)
const showCreate = ref(false)
const saving = ref(false)
const formError = ref('')
const editForm = ref({})
const newSparte = ref({ name_sparte: '', icon: '', treffpunkt: '', aktiv: 1 })
const creating = ref(false)
const createError = ref('')
const uploadingBild = ref(false)

// Mitglieder-Modal State
const showMitglieder = ref(false)
const mitgliederSparte = ref(null)
const mitgliederList = ref([])
const mitgliederAuswahl = ref([])
const mitgliederLoading = ref(false)
const mitgliederSaving = ref(false)
const mitgliederError = ref('')
const addMitgliedName = ref('')

// Leitung im Detail-Modal
const selectedMitglieder = ref([])

function leitung() {
  return selectedMitglieder.value.filter(m =>
    m.aktiv && (m.funktion === 'Spartenleiter' || m.funktion === 'Stv. Spartenleiter')
  )
}

function spartenleitungText(s) {
  return s.spartenleiter ? `${verein.strukturLeitung} hinterlegt` : ''
}

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    sparten.value = await api.getList('Sparte', {
      fields: ['name','name_sparte','icon','farbe','treffpunkt','email','gruendungsjahr','beschreibung','aktiv','spartenleiter','bild'],
      order_by: 'name_sparte', limit_page_length: 50
    }) || []
  } finally { loading.value = false }
}

async function openDetail(s) {
  selected.value = s
  selectedMitglieder.value = []
  try {
    const rows = await api.call('dms_verein.api.verein.get_sparte_mitglieder', { sparte_name: s.name })
    selectedMitglieder.value = rows || []
  } catch {}
}

async function openEdit(s) {
  editTarget.value = s
  formError.value = ''
  selected.value = null
  try {
    const full = await api.getDoc('Sparte', s.name)
    editForm.value = {
      icon: full.icon || '', farbe: full.farbe || '#2563eb',
      treffpunkt: full.treffpunkt || '', email: full.email || '',
      gruendungsjahr: full.gruendungsjahr || '',
      beschreibung: full.beschreibung || '', aktiv: full.aktiv ?? 1,
      bild: full.bild || '',
      beitrag: full.beitrag || 0,
      beitrag_intervall: full.beitrag_intervall || '',
      beitrag_bezeichnung: full.beitrag_bezeichnung || '',
    }
  } catch {
    editForm.value = {
      icon: s.icon || '', farbe: s.farbe || '#2563eb',
      treffpunkt: s.treffpunkt || '', email: s.email || '',
      gruendungsjahr: s.gruendungsjahr || '',
      beschreibung: s.beschreibung || '', aktiv: s.aktiv ?? 1,
      bild: '', beitrag: 0, beitrag_intervall: '', beitrag_bezeichnung: '',
    }
  }
  showEdit.value = true
}

async function openMitglieder(s) {
  if (!s) return
  mitgliederSparte.value = s
  mitgliederError.value = ''
  addMitgliedName.value = ''
  showMitglieder.value = true
  selected.value = null

  mitgliederLoading.value = true
  try {
    const [rows, auswahl] = await Promise.all([
      api.call('dms_verein.api.verein.get_sparte_mitglieder', { sparte_name: s.name }),
      api.call('dms_verein.api.verein.get_mitglieder_liste_einfach'),
    ])
    mitgliederList.value = (rows || []).map(r => ({ ...r }))
    mitgliederAuswahl.value = auswahl || []
  } catch (e) {
    mitgliederError.value = e.message
  } finally {
    mitgliederLoading.value = false
  }
}

function initials(m) {
  return ((m.vorname?.[0] || '') + (m.nachname?.[0] || '')).toUpperCase() || '?'
}

function addMitglied() {
  if (!addMitgliedName.value) return
  const opt = mitgliederAuswahl.value.find(o => o.value === addMitgliedName.value)
  if (!opt) return
  const parts = opt.label.split(',')
  const nachname = parts[0]?.trim() || ''
  const vorname = parts[1]?.split('(')[0]?.trim() || ''
  mitgliederList.value.push({
    mitglied: addMitgliedName.value,
    vorname, nachname,
    funktion: 'Mitglied',
    von: new Date().toISOString().slice(0, 10),
    aktiv: 1,
    foto: '',
  })
  addMitgliedName.value = ''
}

function removeMitglied(idx) {
  mitgliederList.value.splice(idx, 1)
}

async function saveMitglieder() {
  mitgliederSaving.value = true
  mitgliederError.value = ''
  try {
    await api.call('dms_verein.api.verein.set_sparte_mitglieder', {
      sparte_name: mitgliederSparte.value.name,
      mitglieder: JSON.stringify(mitgliederList.value.map(m => ({
        mitglied: m.mitglied,
        funktion: m.funktion || '',
        von: m.von || '',
        aktiv: m.aktiv,
      }))),
    })
    showMitglieder.value = false
    await load()
  } catch (e) {
    mitgliederError.value = e.message
  } finally {
    mitgliederSaving.value = false
  }
}

async function uploadBild(event) {
  const file = event.target.files?.[0]
  if (!file) return
  uploadingBild.value = true
  try {
    const url = await api.uploadFile(file, 'Sparte', editTarget.value?.name || '')
    if (url) editForm.value.bild = url
  } catch (e) { alert('Upload fehlgeschlagen: ' + e.message) }
  finally { uploadingBild.value = false }
}

function openCreate() { newSparte.value = { name_sparte: '', icon: '', treffpunkt: '', aktiv: 1 }; createError.value = ''; showCreate.value = true }

async function saveEdit() {
  saving.value = true; formError.value = ''
  try {
    await api.updateRecord('Sparte', editTarget.value.name, editForm.value)
    showEdit.value = false
    await load()
  } catch (e) { formError.value = e.message }
  finally { saving.value = false }
}

async function deleteSelected(s) {
  if (!confirm(`Sparte "${s.name_sparte}" wirklich löschen?`)) return
  try { await api.deleteRecord('Sparte', s.name); selected.value = null; await load() }
  catch (e) { alert('Fehler: ' + e.message) }
}

async function createSparte() {
  creating.value = true; createError.value = ''
  try { await api.insertDoc({ doctype: 'Sparte', ...newSparte.value }); showCreate.value = false; await load() }
  catch (e) { createError.value = e.message }
  finally { creating.value = false }
}

// ── Termine ──────────────────────────────────────────────────────────────────
const showTermine    = ref(false)
const termineSparte  = ref(null)
const termineListe   = ref([])
const termineLoading = ref(false)
const termineError   = ref('')
const termineSaving  = ref(false)
const terminSaving   = ref(false)
const terminEdit     = ref(null)

const blankTerminForm = () => ({
  titel: '', datum: new Date().toISOString().split('T')[0],
  uhrzeit_von: '', uhrzeit_bis: '', treffpunkt: '', beschreibung: '',
  wiederholung: 'Keine', wiederholung_wochentag: '', wiederholung_bis: '', aktiv: 1,
})
const terminForm = ref(blankTerminForm())

async function openTermine(s) {
  termineSparte.value = s
  termineError.value = ''
  terminEdit.value = null
  terminForm.value = blankTerminForm()
  showTermine.value = true
  selected.value = null
  termineLoading.value = true
  try {
    termineListe.value = await api.call('dms_verein.api.verein.get_sparten_termine_admin', { sparte_name: s.name }) || []
  } catch (e) { termineError.value = e.message }
  finally { termineLoading.value = false }
}

function editTermin(t) {
  terminEdit.value = t
  terminForm.value = {
    titel: t.titel, datum: t.datum?.split(' ')[0] || '',
    uhrzeit_von: t.uhrzeit_von?.slice(0,5) || '', uhrzeit_bis: t.uhrzeit_bis?.slice(0,5) || '',
    treffpunkt: t.treffpunkt || '', beschreibung: t.beschreibung || '',
    wiederholung: t.wiederholung || 'Keine',
    wiederholung_wochentag: t.wiederholung_wochentag || '',
    wiederholung_bis: t.wiederholung_bis?.split(' ')[0] || '',
    aktiv: t.aktiv ?? 1,
  }
}
function cancelTerminEdit() { terminEdit.value = null; terminForm.value = blankTerminForm() }

async function saveTermin() {
  if (!terminForm.value.titel || !terminForm.value.datum) return
  terminSaving.value = true; termineError.value = ''
  try {
    const f = terminForm.value
    if (terminEdit.value) {
      await api.call('dms_verein.api.verein.update_sparten_termin', {
        name: terminEdit.value.name, ...f,
        uhrzeit_von: f.uhrzeit_von || '', uhrzeit_bis: f.uhrzeit_bis || '',
        wiederholung_bis: f.wiederholung_bis || '',
      })
    } else {
      await api.call('dms_verein.api.verein.create_sparten_termin', {
        sparte_name: termineSparte.value.name, ...f,
        uhrzeit_von: f.uhrzeit_von || '', uhrzeit_bis: f.uhrzeit_bis || '',
        wiederholung_bis: f.wiederholung_bis || '',
      })
    }
    terminEdit.value = null; terminForm.value = blankTerminForm()
    termineListe.value = await api.call('dms_verein.api.verein.get_sparten_termine_admin', { sparte_name: termineSparte.value.name }) || []
  } catch (e) { termineError.value = e.message }
  finally { terminSaving.value = false }
}

async function deleteTermin(t) {
  if (!confirm(`Termin „${t.titel}" wirklich löschen?`)) return
  try {
    await api.call('dms_verein.api.verein.delete_sparten_termin', { name: t.name })
    termineListe.value = await api.call('dms_verein.api.verein.get_sparten_termine_admin', { sparte_name: termineSparte.value.name }) || []
  } catch (e) { termineError.value = e.message }
}

const monthShortDE = (d) => new Date(d).toLocaleDateString('de-DE', { month: 'short' })
</script>
