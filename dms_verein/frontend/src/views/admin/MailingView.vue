<template>
  <div>
    <div class="mb-6">
      <h2>Massen-E-Mail</h2>
      <p class="text-slate-500 mt-1">E-Mails an Mitgliedergruppen versenden</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Composer -->
      <div class="lg:col-span-2 space-y-4">
        <div class="card card-body space-y-4">
          <div class="form-group">
            <label class="label">Empfängergruppe *</label>
            <select v-model="form.gruppe" @change="updateVorschau" class="input">
              <optgroup label="Standard">
                <option v-for="g in gruppen.standard" :key="g.key" :value="g.key">{{ g.label }}</option>
              </optgroup>
              <optgroup v-if="gruppen.mitgliedstypen?.length" label="Nach Beitragsklasse">
                <option v-for="g in gruppen.mitgliedstypen" :key="g.key" :value="g.key">{{ g.label }}</option>
              </optgroup>
              <optgroup v-if="gruppen.sparten?.length" :label="`Nach ${verein.strukturSingular}`">
                <option v-for="g in gruppen.sparten" :key="g.key" :value="g.key">{{ g.label }}</option>
              </optgroup>
            </select>
          </div>

          <!-- Vorschau der Empfänger -->
          <div v-if="vorschau !== null"
            class="text-sm bg-slate-50 rounded-lg px-4 py-3 border border-slate-200 flex items-center gap-2">
            <Users :size="14" class="text-slate-500 shrink-0" />
            <span>
              <strong>{{ vorschau.anzahl }}</strong> Empfänger
              <span v-if="vorschau.vorschau?.length" class="text-slate-400 ml-1">
                (z.B. {{ vorschau.vorschau.slice(0,3).join(', ') }}{{ vorschau.anzahl > 3 ? ' ...' : '' }})
              </span>
            </span>
          </div>

          <div class="form-group">
            <label class="label">Betreff *</label>
            <input v-model="form.betreff" class="input" placeholder="Betreff der E-Mail" />
          </div>

          <div class="form-group">
            <label class="label">Inhalt *</label>
            <div class="border border-slate-200 rounded-xl overflow-hidden">
              <!-- Mini Toolbar -->
              <div class="flex gap-1 p-2 border-b border-slate-100 bg-slate-50">
                <button type="button" @click="insertTag('<b>','</b>')"
                  class="w-7 h-7 flex items-center justify-center rounded hover:bg-white border border-transparent hover:border-slate-200 text-xs font-bold">B</button>
                <button type="button" @click="insertTag('<i>','</i>')"
                  class="w-7 h-7 flex items-center justify-center rounded hover:bg-white border border-transparent hover:border-slate-200 text-xs italic">I</button>
                <button type="button" @click="insertTag('<br><br>','')"
                  class="w-7 h-7 flex items-center justify-center rounded hover:bg-white border border-transparent hover:border-slate-200 text-xs">¶</button>
                <div class="w-px bg-slate-200 mx-1" />
                <button type="button" @click="insertTag('<ul><li>','</li></ul>')"
                  class="w-7 h-7 flex items-center justify-center rounded hover:bg-white border border-transparent hover:border-slate-200 text-xs">≡</button>
                <div class="flex-1" />
                <button type="button" @click="showPreview = !showPreview"
                  class="text-xs px-2 py-1 rounded hover:bg-white border border-slate-200 text-slate-500">
                  {{ showPreview ? 'HTML' : 'Vorschau' }}
                </button>
              </div>
              <div v-if="!showPreview">
                <textarea ref="textareaRef" v-model="form.inhalt"
                  class="w-full p-4 text-sm font-mono resize-none border-0 outline-none min-h-[280px]"
                  placeholder="Sehr geehrte Mitglieder,&#10;&#10;..." />
              </div>
              <div v-else class="p-4 min-h-[280px] prose prose-sm max-w-none text-sm" v-html="form.inhalt" />
            </div>
            <p class="text-xs text-slate-400 mt-1">HTML erlaubt. Platzhalter: <span v-pre class="font-mono bg-slate-100 px-1 rounded">{{ vorname }}</span> <span v-pre class="font-mono bg-slate-100 px-1 rounded">{{ nachname }}</span> <span v-pre class="font-mono bg-slate-100 px-1 rounded">{{ vollname }}</span> <span v-pre class="font-mono bg-slate-100 px-1 rounded">{{ mitgliedsnummer }}</span> <span v-pre class="font-mono bg-slate-100 px-1 rounded">{{ email }}</span> <span v-pre class="font-mono bg-slate-100 px-1 rounded">{{ verein }}</span></p>
          </div>

          <AppAlert v-if="sendResult" :type="sendResult.type" :message="sendResult.text" />

          <div class="flex gap-3 justify-end">
            <div class="flex items-center gap-2 mr-auto">
              <input v-model="form.test_empfaenger" type="email" class="input text-sm w-56"
                placeholder="Test senden an E-Mail..." />
              <button @click="sendTest" :disabled="!form.test_empfaenger || sending"
                class="btn btn-secondary text-sm flex items-center gap-1.5">
                <Send :size="13" /> Test
              </button>
            </div>
            <button @click="sendAll" :disabled="!canSend || sending" class="btn btn-primary flex items-center gap-1.5">
              <Send :size="14" /> {{ sending ? 'Wird gesendet...' : `An ${vorschau?.anzahl || '?'} senden` }}
            </button>
          </div>
        </div>
      </div>

      <!-- Seitenleiste: Tipps -->
      <div class="space-y-4">
        <div class="card card-body">
          <h3 class="font-semibold text-sm mb-3">Platzhalter</h3>
          <div class="space-y-1.5 text-xs text-slate-600">
            <div class="font-mono bg-slate-50 rounded px-2 py-1.5 flex justify-between" v-pre><span>{{ vorname }}</span><span class="text-slate-400">Vorname</span></div>
            <div class="font-mono bg-slate-50 rounded px-2 py-1.5 flex justify-between" v-pre><span>{{ nachname }}</span><span class="text-slate-400">Nachname</span></div>
            <div class="font-mono bg-slate-50 rounded px-2 py-1.5 flex justify-between" v-pre><span>{{ vollname }}</span><span class="text-slate-400">Vor- + Nachname</span></div>
            <div class="font-mono bg-slate-50 rounded px-2 py-1.5 flex justify-between" v-pre><span>{{ mitgliedsnummer }}</span><span class="text-slate-400">Mitgl.-Nr.</span></div>
            <div class="font-mono bg-slate-50 rounded px-2 py-1.5 flex justify-between" v-pre><span>{{ email }}</span><span class="text-slate-400">E-Mail</span></div>
            <div class="font-mono bg-slate-50 rounded px-2 py-1.5 flex justify-between" v-pre><span>{{ verein }}</span><span class="text-slate-400">Vereinsname</span></div>
          </div>
          <p class="text-xs text-slate-400 mt-3">Werden beim Versand pro Mitglied ersetzt.</p>
        </div>

        <div class="card card-body">
          <h3 class="font-semibold text-sm mb-3">Vorlagen</h3>
          <div class="space-y-1.5">
            <button v-for="t in vorlagen" :key="t.name" @click="useVorlage(t)"
              class="w-full text-left text-xs p-2 rounded-lg hover:bg-slate-50 border border-slate-200 hover:border-primary-200 transition-colors">
              {{ t.name }}
            </button>
          </div>
        </div>

        <div class="card card-body bg-amber-50 border-amber-200">
          <div class="flex items-start gap-2 text-xs text-amber-800">
            <Info :size="13" class="shrink-0 mt-0.5 text-amber-500" />
            <div>Teste vor dem Versand immer mit der Test-Funktion. Massen-E-Mails können nicht zurückgerufen werden.</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/api'
import { useVereinStore } from '@/stores/verein'
import AppAlert from '@/components/ui/AppAlert.vue'
import { Send, Users, Info } from 'lucide-vue-next'

const form = ref({ gruppe: 'mit_email', betreff: '', inhalt: '', test_empfaenger: '' })
const gruppen = ref({ standard: [], mitgliedstypen: [], sparten: [] })
const verein = useVereinStore()
const vorschau = ref(null)
const sending = ref(false)
const sendResult = ref(null)
const showPreview = ref(false)
const textareaRef = ref(null)

const canSend = computed(() => form.value.gruppe && form.value.betreff && form.value.inhalt && (vorschau.value?.anzahl || 0) > 0)

const vorlagen = [
  {
    name: 'Einladung Hauptversammlung',
    betreff: 'Einladung zur Hauptversammlung – {{ verein }}',
    inhalt: 'Hallo {{ vorname }},<br><br>wir laden dich herzlich zur diesjährigen Hauptversammlung ein.<br><br><strong>Datum:</strong> [Datum eintragen]<br><strong>Ort:</strong> [Ort eintragen]<br><strong>Uhrzeit:</strong> [Uhrzeit eintragen]<br><br>Bitte gib uns bis zum [Datum] Bescheid, ob du teilnimmst.<br><br>Mit freundlichen Grüßen<br>{{ verein }}',
  },
  {
    name: 'Beitragsrechnung',
    betreff: 'Dein Mitgliedsbeitrag – {{ verein }}',
    inhalt: 'Hallo {{ vorname }},<br><br>deine Beitragsrechnung für das aktuelle Jahr steht im Mitgliederportal zum Abruf bereit.<br><br>Mitgliedsnummer: <strong>{{ mitgliedsnummer }}</strong><br><br>Bei Fragen stehen wir dir gerne zur Verfügung.<br><br>Mit freundlichen Grüßen<br>{{ verein }}',
  },
  {
    name: 'Willkommen neues Mitglied',
    betreff: 'Herzlich willkommen bei {{ verein }}!',
    inhalt: 'Hallo {{ vorname }},<br><br>herzlich willkommen bei <strong>{{ verein }}</strong>!<br><br>Deine Mitgliedsnummer lautet: <strong>{{ mitgliedsnummer }}</strong><br><br>Im Mitgliederportal kannst du deine Daten einsehen und verwalten.<br><br>Wir freuen uns auf deine Mitgliedschaft!<br><br>Mit freundlichen Grüßen<br>{{ verein }}',
  },
  {
    name: 'Allgemeine Information',
    betreff: 'Information vom Vorstand – {{ verein }}',
    inhalt: 'Liebe {{ vollname }},<br><br>wir möchten dich über Folgendes informieren:<br><br>[Inhalt hier einfügen]<br><br>Bei Fragen kannst du uns unter <a href="mailto:{{ email }}">{{ email }}</a> erreichen.<br><br>Mit freundlichen Grüßen<br>{{ verein }}',
  },
]

onMounted(async () => {
  gruppen.value = await api.call('dms_verein.api.verein.get_email_gruppen') || {}
  updateVorschau()
})

async function updateVorschau() {
  if (!form.value.gruppe) return
  try {
    vorschau.value = await api.call('dms_verein.api.verein.get_email_empfaenger_vorschau', { gruppe: form.value.gruppe })
  } catch { vorschau.value = null }
}

function useVorlage(t) {
  form.value.betreff = t.betreff
  form.value.inhalt = t.inhalt
}

function insertTag(open, close) {
  const el = textareaRef.value
  if (!el) return
  const start = el.selectionStart, end = el.selectionEnd
  const sel = form.value.inhalt.slice(start, end)
  form.value.inhalt = form.value.inhalt.slice(0, start) + open + sel + close + form.value.inhalt.slice(end)
}

async function sendTest() {
  sending.value = true; sendResult.value = null
  try {
    const r = await api.call('dms_verein.api.verein.send_massen_email', {
      gruppe: form.value.gruppe, betreff: form.value.betreff,
      inhalt: form.value.inhalt, test_empfaenger: form.value.test_empfaenger,
    })
    const n = r?.anzahl ?? '?'
    sendResult.value = { type: 'success', text: `Vorschau-Mail mit ${n} Empfängern an ${form.value.test_empfaenger} gesendet.` }
  } catch (e) { sendResult.value = { type: 'error', text: e.message } }
  finally { sending.value = false }
}

async function sendAll() {
  const n = vorschau.value?.anzahl || 0
  if (!confirm(`E-Mail wirklich an ${n} Mitglieder senden?`)) return
  sending.value = true; sendResult.value = null
  try {
    const r = await api.call('dms_verein.api.verein.send_massen_email', {
      gruppe: form.value.gruppe, betreff: form.value.betreff, inhalt: form.value.inhalt,
    })
    sendResult.value = { type: 'success', text: `${r.gesendet} E-Mail(s) erfolgreich in die Warteschlange eingereiht.` }
  } catch (e) { sendResult.value = { type: 'error', text: e.message } }
  finally { sending.value = false }
}
</script>
