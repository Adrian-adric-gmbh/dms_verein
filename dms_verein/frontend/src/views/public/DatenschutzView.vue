<template>
  <div class="min-h-screen bg-slate-50 py-12 px-4">
    <div class="max-w-3xl mx-auto">
      <RouterLink to="/" class="btn btn-secondary btn-sm mb-6 inline-flex"><ArrowLeft :size="14" /> Zurück zur Startseite</RouterLink>

      <div class="card card-body">
        <h1 class="mb-8">Datenschutzerklärung</h1>

        <AppSpinner v-if="!v" />

        <div v-else class="space-y-6 text-sm text-slate-700">

          <!-- Custom Datenschutz-Text aus Admin-Konfiguration -->
          <div v-if="v.datenschutz_text" class="prose prose-sm max-w-none text-slate-700" v-html="v.datenschutz_text" />

          <!-- Fallback: Standard-Datenschutzerklärung wenn kein custom Text -->
          <template v-else>
            <section>
              <h2 class="text-lg font-semibold text-slate-900 mb-3">1. Verantwortlicher</h2>
              <p>Verantwortlich für die Datenverarbeitung auf dieser Website ist:</p>
              <div class="bg-slate-50 rounded-xl p-4 mt-3 space-y-1">
                <p class="font-semibold">{{ v.vereinsname }}<span v-if="v.rechtsform"> {{ v.rechtsform }}</span></p>
                <p v-if="v.strasse">{{ v.strasse }} {{ v.hausnummer }}, {{ v.plz }} {{ v.ort }}</p>
                <p v-if="v.email">E-Mail: <a :href="'mailto:'+v.email" class="underline">{{ v.email }}</a></p>
                <p v-if="v.telefon">Telefon: {{ v.telefon }}</p>
              </div>
            </section>

            <section>
              <h2 class="text-lg font-semibold text-slate-900 mb-3">2. Datenschutzbeauftragter</h2>
              <div v-if="v.datenschutzbeauftragter || v.datenschutz_email">
                <p v-if="v.datenschutzbeauftragter">Name: {{ v.datenschutzbeauftragter }}</p>
                <p v-if="v.datenschutz_email">E-Mail: <a :href="'mailto:'+v.datenschutz_email" class="underline">{{ v.datenschutz_email }}</a></p>
              </div>
              <p v-else class="text-slate-500">Der Verein hat keinen gesetzlich verpflichtenden Datenschutzbeauftragten bestellt. Bei Fragen zum Datenschutz wenden Sie sich bitte an die oben genannte Adresse.</p>
            </section>

            <section>
              <h2 class="text-lg font-semibold text-slate-900 mb-3">3. Erhebung und Verarbeitung personenbezogener Daten</h2>
              <div class="space-y-3">
                <div>
                  <h3 class="font-semibold text-slate-800 mb-1">Mitgliederdaten</h3>
                  <p>Im Rahmen der Mitgliedschaft werden folgende personenbezogene Daten erhoben und verarbeitet: Name, Anschrift, Geburtsdatum, Kontaktdaten (E-Mail, Telefon), Bankverbindung (bei SEPA-Lastschrift), Beitrittsdatum und Mitgliedsstatus. Die Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung) sowie Art. 6 Abs. 1 lit. c DSGVO (gesetzliche Pflichten).</p>
                </div>
                <div>
                  <h3 class="font-semibold text-slate-800 mb-1">Website-Nutzung</h3>
                  <p>Bei der Nutzung dieser Website werden automatisch Informationen technischer Art (IP-Adresse, Datum, Uhrzeit, Browser, Betriebssystem) im Serverlog gespeichert. Dies dient dem Betrieb des Servers und der Fehleranalyse. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse).</p>
                </div>
              </div>
            </section>

            <section>
              <h2 class="text-lg font-semibold text-slate-900 mb-3">4. Weitergabe von Daten</h2>
              <p>Eine Weitergabe Ihrer personenbezogenen Daten an Dritte erfolgt nur, wenn dies gesetzlich zulässig oder erforderlich ist (z.B. Meldepflichten nach Vereinsrecht, Daten an Bankinstitute für SEPA-Lastschriften) oder Sie ausdrücklich eingewilligt haben.</p>
            </section>

            <section>
              <h2 class="text-lg font-semibold text-slate-900 mb-3">5. Speicherdauer</h2>
              <p>Personenbezogene Daten werden nur so lange gespeichert, wie es für den jeweiligen Zweck erforderlich ist oder gesetzliche Aufbewahrungsfristen dies vorschreiben. Nach Beendigung der Mitgliedschaft werden die Daten nach Ablauf der steuerrechtlichen Aufbewahrungsfristen (regelmäßig 10 Jahre) gelöscht.</p>
            </section>

            <section>
              <h2 class="text-lg font-semibold text-slate-900 mb-3">6. Ihre Rechte</h2>
              <p>Gemäß DSGVO haben Sie folgende Rechte:</p>
              <ul class="mt-2 space-y-1 list-disc list-inside text-slate-600">
                <li><strong>Auskunftsrecht</strong> (Art. 15 DSGVO): Auskunft über Ihre gespeicherten Daten</li>
                <li><strong>Berichtigungsrecht</strong> (Art. 16 DSGVO): Berichtigung unrichtiger Daten</li>
                <li><strong>Löschungsrecht</strong> (Art. 17 DSGVO): Löschung Ihrer Daten</li>
                <li><strong>Einschränkungsrecht</strong> (Art. 18 DSGVO): Einschränkung der Verarbeitung</li>
                <li><strong>Datenübertragbarkeit</strong> (Art. 20 DSGVO): Übertragung Ihrer Daten</li>
                <li><strong>Widerspruchsrecht</strong> (Art. 21 DSGVO): Widerspruch gegen die Verarbeitung</li>
              </ul>
              <p class="mt-3">Zur Ausübung Ihrer Rechte wenden Sie sich bitte an:
                <a v-if="v.datenschutz_email" :href="'mailto:'+v.datenschutz_email" class="underline">{{ v.datenschutz_email }}</a>
                <a v-else-if="v.email" :href="'mailto:'+v.email" class="underline">{{ v.email }}</a>
                <span v-else>die oben genannte Kontaktadresse</span>.
              </p>
            </section>

            <section>
              <h2 class="text-lg font-semibold text-slate-900 mb-3">7. Beschwerderecht</h2>
              <p>Sie haben das Recht, sich bei einer Datenschutz-Aufsichtsbehörde über die Verarbeitung Ihrer personenbezogenen Daten durch uns zu beschweren. Die zuständige Aufsichtsbehörde richtet sich nach dem Bundesland des Vereinssitzes.</p>
            </section>
          </template>

          <!-- Stand-Datum -->
          <div class="border-t border-slate-200 pt-4 text-xs text-slate-400">
            Verantwortlich: {{ v.vereinsname }}<span v-if="v.rechtsform"> {{ v.rechtsform }}</span>
            <span v-if="v.ort"> · {{ v.ort }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useVereinStore } from '@/stores/verein'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import { ArrowLeft } from 'lucide-vue-next'

const verein = useVereinStore()
const v = computed(() => verein.info)
</script>
