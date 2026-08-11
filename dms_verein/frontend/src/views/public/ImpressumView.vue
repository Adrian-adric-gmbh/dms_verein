<template>
  <div class="min-h-screen bg-slate-50 py-12 px-4">
    <div class="max-w-3xl mx-auto">
      <RouterLink to="/" class="btn btn-secondary btn-sm mb-6 inline-flex"><ArrowLeft :size="14" /> Zurück zur Startseite</RouterLink>

      <div class="card card-body">
        <h1 class="mb-8">Impressum</h1>

        <AppSpinner v-if="!v" />

        <div v-else class="space-y-6 text-sm text-slate-700">

          <!-- Angaben gemäß §5 TMG -->
          <section>
            <h2 class="text-lg font-semibold text-slate-900 mb-3">Angaben gemäß §5 TMG</h2>
            <div class="bg-slate-50 rounded-xl p-4 space-y-1">
              <p class="font-semibold text-base">{{ v.vereinsname }}<span v-if="v.rechtsform"> {{ v.rechtsform }}</span></p>
              <p v-if="v.strasse || v.ort">
                {{ v.strasse }} {{ v.hausnummer }}<br />
                {{ v.plz }} {{ v.ort }}<span v-if="v.bundesland">, {{ v.bundesland }}</span>
              </p>
              <p v-else class="text-slate-400 italic">Anschrift noch nicht hinterlegt</p>
            </div>
          </section>

          <!-- Kontakt -->
          <section>
            <h2 class="text-lg font-semibold text-slate-900 mb-3">Kontakt</h2>
            <div class="space-y-1">
              <p v-if="v.telefon"><span class="font-medium w-32 inline-block">Telefon:</span> <a :href="'tel:'+v.telefon" class="hover:underline">{{ v.telefon }}</a></p>
              <p v-if="v.email"><span class="font-medium w-32 inline-block">E-Mail:</span> <a :href="'mailto:'+v.email" class="hover:underline">{{ v.email }}</a></p>
              <p v-if="v.website"><span class="font-medium w-32 inline-block">Website:</span> <a :href="v.website" target="_blank" rel="noopener" class="hover:underline">{{ v.website }}</a></p>
              <p v-if="!v.telefon && !v.email && !v.website" class="text-slate-400 italic">Kontaktdaten noch nicht hinterlegt</p>
            </div>
          </section>

          <!-- Vereinsregister -->
          <section v-if="v.registernummer || v.amtsgericht">
            <h2 class="text-lg font-semibold text-slate-900 mb-3">Vereinsregister</h2>
            <div class="space-y-1">
              <p v-if="v.registernummer"><span class="font-medium w-48 inline-block">Registernummer:</span> {{ v.registernummer }}</p>
              <p v-if="v.amtsgericht"><span class="font-medium w-48 inline-block">Eingetragen beim:</span> {{ v.amtsgericht }}</p>
            </div>
          </section>

          <!-- Vertretungsberechtigter Vorstand -->
          <section v-if="v.vertretung_vorstand">
            <h2 class="text-lg font-semibold text-slate-900 mb-3">Vertretungsberechtigter Vorstand (§26 BGB)</h2>
            <p class="whitespace-pre-line">{{ v.vertretung_vorstand }}</p>
          </section>

          <!-- Steuerliche Angaben -->
          <section v-if="v.steuernummer || v.gemeinnuetzig">
            <h2 class="text-lg font-semibold text-slate-900 mb-3">Steuerliche Angaben</h2>
            <div class="space-y-1">
              <p v-if="v.steuernummer"><span class="font-medium w-48 inline-block">Steuernummer:</span> {{ v.steuernummer }}</p>
              <p v-if="v.gemeinnuetzig" class="flex items-center gap-2">
                <span class="inline-flex items-center gap-1 bg-emerald-100 text-emerald-800 text-xs font-medium px-2.5 py-1 rounded-full">
                  ✓ Gemeinnützig anerkannt
                </span>
                <span class="text-slate-500">gemäß §4 Nr. 22 UStG</span>
              </p>
            </div>
          </section>

          <!-- Gründungsjahr -->
          <section v-if="v.gruendungsjahr">
            <h2 class="text-lg font-semibold text-slate-900 mb-3">Über den Verein</h2>
            <p>Gegründet: {{ v.gruendungsjahr }}</p>
            <p v-if="v.vereinszweck" class="mt-1 text-slate-600">{{ v.vereinszweck }}</p>
          </section>

          <!-- Datenschutz Hinweis -->
          <section>
            <h2 class="text-lg font-semibold text-slate-900 mb-3">Datenschutz</h2>
            <p>Informationen zur Verarbeitung personenbezogener Daten finden Sie in unserer
              <RouterLink v-if="!v.datenschutz_url" to="/datenschutz" class="underline text-primary-600">Datenschutzerklärung</RouterLink>
              <a v-else :href="v.datenschutz_url" target="_blank" rel="noopener" class="underline text-primary-600">Datenschutzerklärung</a>.
            </p>
            <p v-if="v.datenschutzbeauftragter" class="mt-2">
              Datenschutzbeauftragter: {{ v.datenschutzbeauftragter }}<span v-if="v.datenschutz_email">
              · <a :href="'mailto:'+v.datenschutz_email" class="underline">{{ v.datenschutz_email }}</a></span>
            </p>
          </section>

          <!-- Haftungsausschluss Standard -->
          <section class="border-t border-slate-200 pt-6">
            <h2 class="text-lg font-semibold text-slate-900 mb-3">Haftungsausschluss</h2>
            <div class="space-y-3 text-slate-600">
              <div>
                <h3 class="font-semibold text-slate-800 mb-1">Haftung für Inhalte</h3>
                <p>Als Betreiber sind wir gemäß §7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§8 bis 10 TMG sind wir jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen.</p>
              </div>
              <div>
                <h3 class="font-semibold text-slate-800 mb-1">Haftung für Links</h3>
                <p>Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich.</p>
              </div>
              <div>
                <h3 class="font-semibold text-slate-800 mb-1">Urheberrecht</h3>
                <p>Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.</p>
              </div>
            </div>
          </section>

          <!-- Zusatztext aus Admin-Konfiguration -->
          <section v-if="v.impressum_text" class="border-t border-slate-200 pt-6">
            <div class="prose prose-sm max-w-none text-slate-700" v-html="v.impressum_text" />
          </section>

          <!-- Anbieter der Software (nicht des Vereins) -->
          <section class="border-t border-slate-200 pt-6">
            <h2 class="text-lg font-semibold text-slate-900 mb-3">Technische Bereitstellung</h2>
            <p class="text-slate-600 mb-3">
              Diese Vereinsplattform wird mit der Software <strong>{{ ANBIETER.produkt }}</strong> betrieben.
              Für die Inhalte dieser Seite ist der oben genannte Verein verantwortlich.
              Anbieter der Software ist:
            </p>
            <div class="bg-slate-50 rounded-xl p-4 space-y-1">
              <p class="font-semibold">{{ ANBIETER.firma }}</p>
              <p>Inhaber: {{ ANBIETER.inhaber }}</p>
              <p>{{ ANBIETER.strasse }}<br />{{ ANBIETER.plz }} {{ ANBIETER.ort }}, {{ ANBIETER.land }}</p>
              <p>
                <span class="font-medium w-32 inline-block">Telefon:</span>
                <a :href="ANBIETER_TEL_HREF" class="hover:underline">{{ ANBIETER.telefon }}</a>
              </p>
              <p>
                <span class="font-medium w-32 inline-block">E-Mail:</span>
                <a :href="'mailto:' + ANBIETER.email" class="hover:underline">{{ ANBIETER.email }}</a>
              </p>
              <p>
                <span class="font-medium w-32 inline-block">USt-IdNr.:</span> {{ ANBIETER.ustIdNr }}
              </p>
              <p>
                <a :href="ANBIETER.impressumUrl" target="_blank" rel="noopener"
                   class="underline text-primary-600">Impressum des Anbieters</a>
              </p>
            </div>
          </section>

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
import { ANBIETER, ANBIETER_TEL_HREF } from '@/utils/anbieter'

const verein = useVereinStore()
const v = computed(() => verein.info)
</script>
