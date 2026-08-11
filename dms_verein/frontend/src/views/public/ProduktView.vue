<template>
  <div class="min-h-screen bg-white font-sans">

    <!-- ══ HERO ══ -->
    <section class="relative overflow-hidden bg-gradient-to-br from-slate-900 via-primary-900 to-slate-800 text-white">
      <div class="absolute inset-0 opacity-10"
           style="background-image: radial-gradient(circle at 25% 50%, #22c55e 0%, transparent 60%), radial-gradient(circle at 75% 20%, #3b82f6 0%, transparent 50%)"></div>
      <div class="relative max-w-6xl mx-auto px-6 py-24 md:py-36 text-center">
        <div class="inline-flex items-center gap-2 bg-white/10 rounded-full px-4 py-1.5 text-sm font-medium text-green-300 mb-6">
          <span class="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
          Vereinssoftware · Made in Germany
        </div>
        <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 leading-tight">
          Die digitale Vereinsplattform –<br />
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-300">
            einfach, modern, komplett.
          </span>
        </h1>
        <p class="text-xl text-slate-300 max-w-2xl mx-auto mb-6 leading-relaxed">
          DMS Verein vereint Mitgliederverwaltung, Kommunikation, Finanzen und ein mobiles
          Mitgliederportal in einer einzigen Plattform – ohne Kompromisse.
        </p>
        <!-- Zielgruppen-Chips -->
        <div class="flex flex-wrap justify-center gap-2 mb-10 text-sm">
          <span v-for="z in zielgruppen" :key="z"
            class="bg-white/10 border border-white/15 text-slate-300 rounded-full px-3 py-1">
            {{ z }}
          </span>
        </div>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="#kontakt"
             class="bg-green-500 hover:bg-green-400 text-white font-semibold px-8 py-3.5 rounded-xl transition-colors shadow-lg shadow-green-500/30">
            Demo anfragen
          </a>
          <a href="#module"
             class="bg-white/10 hover:bg-white/20 text-white font-semibold px-8 py-3.5 rounded-xl transition-colors border border-white/20">
            Alle Module ansehen
          </a>
          <a href="#preise"
             class="bg-white/10 hover:bg-white/20 text-white font-semibold px-8 py-3.5 rounded-xl transition-colors border border-white/20">
            Preise
          </a>
        </div>
      </div>
      <!-- Screenshot-Platzhalter Hero -->
      <!-- 💡 SCREENSHOT-VORSCHLAG: Dashboard-Übersicht Admin + Mobile Portal nebeneinander -->
      <div class="relative max-w-5xl mx-auto px-6 pb-0 -mb-1">
        <div class="bg-slate-800/60 border border-white/10 rounded-t-2xl overflow-hidden shadow-2xl">
          <div class="bg-slate-700/50 px-4 py-2.5 flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-red-400"></span>
            <span class="w-3 h-3 rounded-full bg-yellow-400"></span>
            <span class="w-3 h-3 rounded-full bg-green-400"></span>
            <span class="text-xs text-slate-400 ml-2">verein.dms-iot.de</span>
          </div>
          <div class="h-52 md:h-80 relative">
            <div class="absolute inset-0 flex flex-col items-center justify-center gap-2 text-center">
              <p class="text-slate-500 text-sm">Admin-Dashboard Gesamtübersicht</p>
              <p class="text-xs font-mono font-semibold text-green-400">hero_dashboard.jpg</p>
              <p class="text-xs text-slate-600">1200 × 380 px</p>
            </div>
            <img :src="'/assets/dms_verein/screenshots/hero_dashboard.jpg'"
                 alt="Dashboard"
                 class="absolute inset-0 w-full h-full object-cover object-top rounded"
                 @error="e => e.target.style.display='none'" />
          </div>
        </div>
      </div>
    </section>

    <!-- ══ KENNZAHLEN ══ -->
    <section class="bg-slate-50 border-b border-slate-200">
      <div class="max-w-6xl mx-auto px-6 py-12 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
        <div v-for="kpi in kpis" :key="kpi.label">
          <p class="text-3xl font-extrabold text-primary-700">{{ kpi.value }}</p>
          <p class="text-sm text-slate-500 mt-1">{{ kpi.label }}</p>
        </div>
      </div>
    </section>

    <!-- ══ MODULE ══ -->
    <section id="module" class="py-24 px-6">
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-16">
          <span class="text-sm font-semibold text-primary-600 uppercase tracking-widest">Funktionsumfang</span>
          <h2 class="text-3xl md:text-4xl font-extrabold text-slate-900 mt-2">Alles was Ihr Verein braucht</h2>
          <p class="text-slate-500 mt-3 max-w-xl mx-auto">Jedes Modul ist nahtlos mit den anderen verbunden – kein Datenwirrwarr, kein doppelter Aufwand.</p>
        </div>
        <div class="space-y-24">
          <div v-for="(modul, idx) in module" :key="modul.id"
               :class="['grid md:grid-cols-2 gap-12 items-center', idx % 2 === 1 ? 'md:grid-flow-col-dense' : '']">
            <!-- Text -->
            <div :class="idx % 2 === 1 ? 'md:col-start-2' : ''">
              <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl mb-4"
                   :style="{ backgroundColor: modul.farbe + '20', color: modul.farbe }">
                <component :is="modul.icon" :size="22" />
              </div>
              <h3 class="text-2xl font-bold text-slate-900 mb-3">{{ modul.titel }}</h3>
              <p class="text-slate-600 leading-relaxed mb-5">{{ modul.beschreibung }}</p>
              <ul class="space-y-2">
                <li v-for="f in modul.features" :key="f" class="flex items-start gap-2.5 text-sm text-slate-700">
                  <CheckCircle2 :size="16" class="shrink-0 mt-0.5 text-green-500" />
                  {{ f }}
                </li>
              </ul>
            </div>
            <!-- Bild-Platzhalter -->
            <div :class="idx % 2 === 1 ? 'md:col-start-1 md:row-start-1' : ''">
              <div class="rounded-2xl overflow-hidden shadow-xl border border-slate-200 bg-slate-50 h-64 md:h-72 relative">
                <!-- Platzhalter (sichtbar solange Bild fehlt) -->
                <div class="absolute inset-0 flex flex-col items-center justify-center gap-3 p-6 text-center">
                  <component :is="modul.icon" :size="36" class="text-slate-300" />
                  <p class="text-xs font-mono font-semibold text-primary-500">{{ modul.imgFile }}</p>
                  <p class="text-xs text-slate-400">{{ modul.imgSize }}</p>
                </div>
                <!-- Echtes Bild (sobald Datei vorhanden) -->
                <img :src="'/assets/dms_verein/screenshots/' + modul.imgFile"
                     :alt="modul.titel"
                     class="absolute inset-0 w-full h-full object-cover object-top"
                     @error="e => e.target.style.display='none'" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ MOBILE APP ══ -->
    <section class="bg-gradient-to-br from-green-50 to-emerald-50 py-24 px-6 border-y border-green-100">
      <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-16 items-center">
        <div>
          <span class="text-sm font-semibold text-green-700 uppercase tracking-widest">Progressive Web App</span>
          <h2 class="text-3xl font-extrabold text-slate-900 mt-2 mb-4">Das Mitgliederportal –<br/>direkt auf dem Handy</h2>
          <p class="text-slate-600 leading-relaxed mb-6">
            Kein App-Store, keine Installation: Mitglieder können das Portal einfach auf dem Home-Bildschirm speichern und wie eine native App nutzen – auf iOS, Android und am Desktop.
          </p>
          <ul class="space-y-3">
            <li v-for="f in mobileFeatures" :key="f" class="flex items-center gap-3 text-sm text-slate-700">
              <span class="w-6 h-6 rounded-full bg-green-100 text-green-700 flex items-center justify-center font-bold text-xs shrink-0">✓</span>
              {{ f }}
            </li>
          </ul>
        </div>
        <!-- 💡 SCREENSHOT-VORSCHLAG: Zwei Smartphone-Mockups nebeneinander – z.B. Veranstaltungen + Chat -->
        <div class="flex gap-4 justify-center">
          <div class="relative">
            <div class="w-44 h-80 bg-slate-100 rounded-xl flex flex-col items-center justify-center gap-1 px-3 text-center">
              <p class="text-xs text-slate-400">Mobile – Veranstaltungen</p>
              <p class="text-[10px] font-mono font-semibold text-primary-500">mobile_veranstaltungen.jpg</p>
              <p class="text-[10px] text-slate-400">390 × 844 px</p>
            </div>
            <img :src="'/assets/dms_verein/screenshots/mobile_veranstaltungen.jpg'"
                 alt="Mobile Veranstaltungen"
                 class="absolute inset-0 w-full h-full object-contain drop-shadow-2xl"
                 @error="e => e.target.style.display='none'" />
          </div>
          <div class="relative mt-8">
            <div class="w-44 h-80 bg-slate-100 rounded-xl flex flex-col items-center justify-center gap-1 px-3 text-center">
              <p class="text-xs text-slate-400">Mobile – Chat</p>
              <p class="text-[10px] font-mono font-semibold text-primary-500">mobile_chat.jpg</p>
              <p class="text-[10px] text-slate-400">390 × 844 px</p>
            </div>
            <img :src="'/assets/dms_verein/screenshots/mobile_chat.jpg'"
                 alt="Mobile Chat"
                 class="absolute inset-0 w-full h-full object-contain drop-shadow-2xl"
                 @error="e => e.target.style.display='none'" />
          </div>
        </div>
      </div>
    </section>

    <!-- ══ VERSCHLÜSSELUNG / DATENSCHUTZ ══ -->
    <section class="py-24 px-6">
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-12">
          <span class="text-sm font-semibold text-primary-600 uppercase tracking-widest">Sicherheit & Datenschutz</span>
          <h2 class="text-3xl font-extrabold text-slate-900 mt-2">Datenschutz ist keine Option – er ist Standard</h2>
        </div>
        <div class="grid md:grid-cols-3 gap-8">
          <div v-for="s in sicherheit" :key="s.titel"
               class="bg-slate-50 rounded-2xl p-6 border border-slate-200 text-center">
            <div class="w-12 h-12 rounded-xl bg-primary-100 text-primary-700 flex items-center justify-center mx-auto mb-4">
              <component :is="s.icon" :size="22" />
            </div>
            <h3 class="font-bold text-slate-800 mb-2">{{ s.titel }}</h3>
            <p class="text-sm text-slate-500 leading-relaxed">{{ s.text }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ KONTAKT ══ -->
    <section id="kontakt" class="bg-slate-900 text-white py-24 px-6">
      <div class="max-w-xl mx-auto text-center mb-10">
        <span class="text-sm font-semibold text-green-400 uppercase tracking-widest">Kontakt & Demo</span>
        <h2 class="text-3xl font-extrabold mt-2 mb-3">Bereit für den digitalen Verein?</h2>
        <p class="text-slate-400">Schreiben Sie mir – ich melde mich innerhalb von 24 Stunden mit einem unverbindlichen Demo-Zugang.</p>
      </div>
      <div class="max-w-xl mx-auto bg-white/5 border border-white/10 rounded-2xl p-8 backdrop-blur-sm">
        <form @submit.prevent="sendKontakt" class="space-y-5">
          <div class="grid sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-1.5">Vorname *</label>
              <input v-model="form.vorname" required placeholder="Max"
                     class="w-full bg-white/10 border border-white/20 text-white placeholder-slate-500 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 transition" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-1.5">Nachname *</label>
              <input v-model="form.nachname" required placeholder="Mustermann"
                     class="w-full bg-white/10 border border-white/20 text-white placeholder-slate-500 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 transition" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-1.5">Vereinsname</label>
            <input v-model="form.verein" placeholder="TSV Musterstadt e.V."
                   class="w-full bg-white/10 border border-white/20 text-white placeholder-slate-500 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 transition" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-1.5">E-Mail *</label>
            <input v-model="form.email" type="email" required placeholder="max@musterverein.de"
                   class="w-full bg-white/10 border border-white/20 text-white placeholder-slate-500 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 transition" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-1.5">Telefon</label>
            <input v-model="form.telefon" type="tel" placeholder="+49 800 000000"
                   class="w-full bg-white/10 border border-white/20 text-white placeholder-slate-500 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 transition" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-1.5">Mitgliederanzahl (ca.)</label>
            <select v-model="form.mitglieder"
                    class="w-full bg-white/10 border border-white/20 text-white rounded-xl px-4 py-2.5 text-sm outline-none focus:border-green-400 transition">
              <option value="" class="text-slate-900">Bitte wählen</option>
              <option class="text-slate-900">Unter 50</option>
              <option class="text-slate-900">50 – 200</option>
              <option class="text-slate-900">200 – 500</option>
              <option class="text-slate-900">Über 500</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-1.5">Nachricht</label>
            <textarea v-model="form.nachricht" rows="4" placeholder="Womit kann ich helfen?"
                      class="w-full bg-white/10 border border-white/20 text-white placeholder-slate-500 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 transition resize-none"></textarea>
          </div>
          <div v-if="sendError" class="bg-red-500/10 border border-red-500/30 text-red-300 text-sm rounded-xl px-4 py-3">
            {{ sendError }}
          </div>
          <div v-if="sendSuccess" class="bg-green-500/10 border border-green-500/30 text-green-300 text-sm rounded-xl px-4 py-3">
            ✓ Ihre Anfrage wurde erfolgreich gesendet. Ich melde mich bald!
          </div>
          <button type="submit" :disabled="sending"
                  class="w-full bg-green-500 hover:bg-green-400 disabled:opacity-60 text-white font-semibold py-3.5 rounded-xl transition-colors shadow-lg shadow-green-500/20">
            {{ sending ? 'Wird gesendet…' : 'Demo anfragen →' }}
          </button>
          <p class="text-xs text-slate-500 text-center">Mit dem Absenden stimmen Sie der Verarbeitung Ihrer Daten zur Bearbeitung Ihrer Anfrage zu.</p>
        </form>
      </div>
    </section>

    <!-- ══ PREISE ══ -->
    <section id="preise" class="py-24 px-6 bg-slate-50 border-t border-slate-200">
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-6">
          <span class="text-sm font-semibold text-primary-600 uppercase tracking-widest">Preise</span>
          <h2 class="text-3xl md:text-4xl font-extrabold text-slate-900 mt-2">Transparent. Keine versteckten Kosten.</h2>
          <p class="text-slate-500 mt-3 max-w-xl mx-auto">
            Alle Tarife enthalten <strong>denselben vollen Funktionsumfang</strong> –
            kein künstliches Feature-Sperren. Der Preis richtet sich ausschließlich nach der Mitgliederanzahl.
          </p>
        </div>

        <!-- Jahres/Monats Toggle -->
        <div class="flex justify-center mb-10">
          <div class="inline-flex items-center bg-white border border-slate-200 rounded-xl p-1 gap-1 shadow-sm">
            <button @click="preisJaehrlich = false"
              :class="['px-5 py-2 rounded-lg text-sm font-medium transition-colors', !preisJaehrlich ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-700']">
              Monatlich
            </button>
            <button @click="preisJaehrlich = true"
              :class="['px-5 py-2 rounded-lg text-sm font-medium transition-colors', preisJaehrlich ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-700']">
              Jährlich
              <span class="ml-1.5 bg-green-100 text-green-700 text-xs font-bold px-1.5 py-0.5 rounded-full">−2 Monate</span>
            </button>
          </div>
        </div>

        <!-- Tarif-Karten -->
        <div class="grid sm:grid-cols-2 lg:grid-cols-5 gap-5 mb-12">
          <div v-for="tarif in tarife" :key="tarif.name"
               :class="['bg-white rounded-2xl border-2 p-6 flex flex-col relative',
                        tarif.highlight ? 'border-primary-500 shadow-xl shadow-primary-100' : 'border-slate-200']">
            <div v-if="tarif.highlight"
                 class="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary-600 text-white text-xs font-bold px-3 py-1 rounded-full">
              Beliebt
            </div>
            <p class="text-lg font-bold text-slate-900">{{ tarif.name }}</p>
            <p class="text-sm text-slate-500 mt-0.5 mb-5">{{ tarif.mitglieder }}</p>
            <div class="mb-1">
              <span class="text-4xl font-extrabold text-slate-900">
                €{{ preisJaehrlich ? tarif.jaehrlich : tarif.monatlich }}
              </span>
              <span class="text-slate-400 text-sm">/Monat</span>
            </div>
            <p v-if="preisJaehrlich" class="text-xs text-green-600 font-medium mb-5">
              €{{ tarif.jaehrlich * 12 }} / Jahr – 2 Monate gratis
            </p>
            <p v-else class="text-xs text-slate-400 mb-5">monatlich kündbar</p>
            <a href="#kontakt"
               :class="['mt-auto block text-center font-semibold py-2.5 rounded-xl transition-colors text-sm',
                        tarif.highlight
                          ? 'bg-primary-600 hover:bg-primary-500 text-white'
                          : 'bg-slate-100 hover:bg-slate-200 text-slate-800']">
              Demo anfragen
            </a>
          </div>
        </div>

        <!-- Was ist immer inklusive -->
        <div class="bg-white border border-slate-200 rounded-2xl p-8">
          <p class="text-center font-bold text-slate-800 mb-6 text-lg">In jedem Tarif enthalten – ohne Ausnahme</p>
          <div class="grid sm:grid-cols-2 md:grid-cols-3 gap-x-10 gap-y-3">
            <div v-for="f in immerInklusive" :key="f" class="flex items-center gap-2.5 text-sm text-slate-700">
              <CheckCircle2 :size="16" class="shrink-0 text-green-500" />
              {{ f }}
            </div>
          </div>
        </div>

        <!-- Einrichtungsgebühr -->
        <div class="mt-6 bg-amber-50 border border-amber-200 rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div class="w-10 h-10 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center shrink-0">
            <Settings :size="20" />
          </div>
          <div class="flex-1">
            <p class="font-bold text-slate-800">Einmalige Einrichtungsgebühr: €299</p>
            <p class="text-sm text-slate-600 mt-0.5">
              Beinhaltet: Server-Setup, individuelle Konfiguration (Logo, Farben, SMTP), Datenmigration vorhandener Mitgliederdaten sowie eine persönliche Einführungsschulung per Video-Call.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ FOOTER ══ -->
    <footer class="bg-slate-950 text-slate-500 py-10 px-6 text-sm">
      <div class="max-w-3xl mx-auto text-center space-y-4">
        <p>© {{ new Date().getFullYear() }} {{ ANBIETER.firma }} · Softwarelösung für Vereine</p>

        <!-- Anbieterkennzeichnung gemäß § 5 DDG -->
        <div class="text-xs leading-relaxed text-slate-600 space-y-1">
          <p class="font-medium text-slate-500">Anbieter gemäß § 5 DDG</p>
          <p>{{ ANBIETER.firma }} · Inhaber: {{ ANBIETER.inhaber }}</p>
          <p>{{ ANBIETER_ANSCHRIFT }}</p>
          <p>
            <a :href="ANBIETER_TEL_HREF" class="hover:text-white transition-colors">{{ ANBIETER.telefon }}</a>
            ·
            <a :href="'mailto:' + ANBIETER.email" class="hover:text-white transition-colors">{{ ANBIETER.email }}</a>
          </p>
          <p>USt-IdNr.: {{ ANBIETER.ustIdNr }}</p>
        </div>

        <p class="text-xs">
          <a :href="ANBIETER.impressumUrl" target="_blank" rel="noopener"
             class="hover:text-white transition-colors">Impressum & Datenschutz</a>
          ·
          <a :href="'mailto:' + ANBIETER.kontaktEmail"
             class="hover:text-white transition-colors">{{ ANBIETER.kontaktEmail }}</a>
        </p>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Users, MessageSquare, Calendar, CreditCard, Image, Vote,
  BookOpen, FileText, BarChart3, Shield, Settings, Layers,
  CheckCircle2, Lock, Server, Globe, PenLine, LayoutDashboard,
  Building2, Gavel
} from 'lucide-vue-next'
import { ANBIETER, ANBIETER_ANSCHRIFT, ANBIETER_TEL_HREF } from '@/utils/anbieter'

// ─── Zielgruppen ──────────────────────────────────────────────────────────────
const zielgruppen = [
  '⚽ Sportvereine', '🚒 Feuerwehren', '🎵 Musikvereine', '🌿 Naturschutz',
  '🎭 Kulturvereine', '🏘️ Bürgervereine', '🤝 Soziale Vereine', '🐾 Tierschutz',
]

// ─── KPIs ─────────────────────────────────────────────────────────────────────
const kpis = [
  { value: '17+', label: 'Funktionsmodule' },
  { value: '100%', label: 'DSGVO-konform' },
  { value: 'PWA', label: 'Mobil ohne App-Store' },
  { value: 'AES-256', label: 'Chat-Verschlüsselung' },
]

// ─── Module ───────────────────────────────────────────────────────────────────
const module = [
  {
    id: 'mitglieder',
    titel: 'Mitgliederverwaltung',
    icon: Users,
    farbe: '#6366f1',
    beschreibung: 'Das Herzstück der Software: Alle Mitgliederdaten zentral erfasst und jederzeit abrufbar. Von der Aufnahme bis zum Austritt wird jeder Schritt lückenlos dokumentiert.',
    features: [
      'Vollständige Stammdaten (Adresse, Kontakt, Geburtsdatum, Foto)',
      'Mitgliedsstatus: Aktiv, Passiv, Gesperrt, Ausgetreten, Verstorben',
      'Mitgliedsnummer & Eintrittsdatum automatisch verwaltet',
      'Beitragsklasse direkt am Mitglied hinterlegt',
      'Notizfeld für interne Vermerke',
      'Filterbarer Export & Listenansicht mit Suchfunktion',
      'Mitgliedschaftshistorie (Typ, Zeitraum, Status)',
    ],
    imgFile: 'mitglieder_liste.jpg', imgSize: '800 × 500 px',
  },
  {
    id: 'portal',
    titel: 'Mitgliederportal (Self-Service)',
    icon: LayoutDashboard,
    farbe: '#22c55e',
    beschreibung: 'Mitglieder verwalten sich selbst: Adresse ändern, Beiträge einsehen, Veranstaltungen buchen – alles ohne Admin-Aufwand. Das Portal ist responsiv und als PWA auf dem Smartphone nutzbar.',
    features: [
      'Persönliches Dashboard mit Übersicht aller relevanten Informationen',
      'Selbstverwaltung: Kontaktdaten, IBAN, Passwort',
      'Eigene Beitragsübersicht und Rechnungsdownload',
      'Anmeldung zu Veranstaltungen',
      'SEPA-Lastschriftmandat online erteilen & widerrufen',
      'Abstimmungen direkt im Portal',
      'Fotoalben & Blog einsehen',
    ],
    imgFile: 'portal_dashboard.jpg', imgSize: '390 × 844 px (Hochformat)',
  },
  {
    id: 'chat',
    titel: 'Interner Chat (Ende-zu-Ende verschlüsselt)',
    icon: MessageSquare,
    farbe: '#0ea5e9',
    beschreibung: 'Ein vollständig in die Plattform integriertes Messaging-System – kein externer Dienst, keine Datenweitergabe. Direkt-Nachrichten und Gruppen-Chats mit Echtzeit-Übertragung.',
    features: [
      'Direkt-Nachrichten zwischen Mitgliedern',
      'Gruppen-Chats mit eigenem Avatar und Admin-Verwaltung',
      'Fotos & Dateien teilen',
      'Ende-zu-Ende-Verschlüsselung (AES-256) aller Nachrichten',
      'Ungelesen-Badge in der Navigation',
      'Eigene Nachrichten löschen (erscheint auch beim Empfänger als gelöscht)',
      'Nachrichtenverlauf für sich leeren',
      'Chat ausblenden ohne Datenverlust',
    ],
    imgFile: 'chat_nachricht.jpg', imgSize: '800 × 500 px',
  },
  {
    id: 'veranstaltungen',
    titel: 'Veranstaltungen & Kalender',
    icon: Calendar,
    farbe: '#f59e0b',
    beschreibung: 'Vereinsveranstaltungen anlegen, veröffentlichen und Anmeldungen verwalten – alles in einem. Mitglieder sehen die nächsten Events sofort im Portal und auf der Vereinswebsite.',
    features: [
      'Veranstaltungen mit Datum, Uhrzeit, Ort und Kategorie',
      'Öffentliche oder mitgliedsbeschränkte Events',
      'Anmeldepflicht & Teilnehmerlistenverwaltung',
      'Kostenangabe pro Veranstaltung',
      'Kalenderansicht im Mitgliederportal und auf der Vereinswebsite',
    ],
    imgFile: 'veranstaltungen_liste.jpg', imgSize: '800 × 500 px',
  },
  {
    id: 'finanzen',
    titel: 'Finanzen, Beiträge & Rechnungen',
    icon: CreditCard,
    farbe: '#10b981',
    beschreibung: 'Beitragsklassen flexibel konfigurieren, Rechnungen automatisch erstellen und SEPA-Lastschriften verwalten. Ein vollständiger Finanzüberblick für Kassenwart und Vorstand.',
    features: [
      'Beitragsklassen mit Betrag, Zahlungsintervall und Altersgrenze',
      'Automatische Beitragszuweisung nach Alter',
      'Rechnungserstellung mit Druckfunktion',
      'SEPA-Lastschriftmandate anlegen und verwalten',
      'SEPA-Sammelexport (XML) für die Hausbank',
      'Finanzübersicht für Kassenwart und Vorstand',
    ],
    imgFile: 'finanzen_uebersicht.jpg', imgSize: '800 × 500 px',
  },
  {
    id: 'antraege',
    titel: 'Online-Mitgliedsanträge',
    icon: FileText,
    farbe: '#8b5cf6',
    beschreibung: 'Interessenten stellen ihren Mitgliedsantrag direkt auf der Vereinswebsite – kein Papierkram mehr. Admins prüfen, genehmigen oder lehnen ab und das Mitglied wird automatisch angelegt.',
    features: [
      'Öffentliches Online-Antragsformular auf der Vereinswebsite',
      'Auswahl der gewünschten Beitragsklasse direkt im Antrag',
      'Admin-Prüfworkflow: annehmen oder ablehnen mit Begründung',
      'Automatische Mitgliedsanlage bei Annahme',
      'Portal-Zugang wird automatisch eingerichtet',
      'E-Mail-Benachrichtigung bei Annahme oder Ablehnung',
    ],
    imgFile: 'antraege_formular.jpg', imgSize: '800 × 500 px',
  },
  {
    id: 'sparten',
    titel: 'Sparten & Abteilungen',
    icon: Layers,
    farbe: '#ec4899',
    beschreibung: 'Große Vereine bilden ihre Struktur mit Sparten ab. Jede Sparte hat eine eigene Seite auf der Vereinswebsite, eigene Mitgliederlisten und einen Spartenleiter.',
    features: [
      'Beliebig viele Sparten (Tennis, Fußball, Schwimmen …)',
      'Öffentliche Spartenseite mit eigenem Inhalt (visueller Seiteneditor)',
      'Mitgliederzuordnung zu einer oder mehreren Sparten',
      'Spartenleiter-Rolle mit eingeschränktem Admin-Zugriff',
      'Mitglieder sehen ihre Sparten im Portal',
    ],
    imgFile: 'sparten_seite.jpg', imgSize: '800 × 500 px',
  },
  {
    id: 'abstimmungen',
    titel: 'Digitale Abstimmungen',
    icon: Vote,
    farbe: '#f97316',
    beschreibung: 'Hauptversammlung, Vorstandswahl, spontane Umfragen – Abstimmungen können jederzeit gestartet und von Mitgliedern bequem im Portal abgestimmt werden.',
    features: [
      'Abstimmungen mit Titel, Beschreibung und Frist erstellen',
      'Ja/Nein oder Multiple-Choice-Optionen',
      'Stimmberechtigung nach Mitgliedstyp einschränkbar',
      'Ergebnisauswertung für Admins',
      'Badge in der Navigation bei offenen Abstimmungen',
    ],
    imgFile: 'abstimmungen_uebersicht.jpg', imgSize: '800 × 500 px',
  },
  {
    id: 'mailing',
    titel: 'Mailing & Kommunikation',
    icon: BookOpen,
    farbe: '#06b6d4',
    beschreibung: 'Gezielte E-Mails an alle Mitglieder oder einzelne Gruppen versenden – direkt aus der Verwaltungsoberfläche, ohne externen Dienst.',
    features: [
      'E-Mails an alle Mitglieder oder nach Sparte/Status/Typ filtern',
      'Betreff und formatierbarer Nachrichtentext',
      'Versand über eigene SMTP-Konfiguration (kein Drittanbieter nötig)',
    ],
    imgFile: 'mailing_formular.jpg', imgSize: '800 × 500 px',
  },
  {
    id: 'protokolle',
    titel: 'Protokolle & Vorstandsbereich',
    icon: Gavel,
    farbe: '#64748b',
    beschreibung: 'Sitzungsprotokolle zentral ablegen und den Vorstand mit seinem eigenen Bereich in der Plattform unterstützen. Wer zum Vorstand gehört, wird transparent kommuniziert.',
    features: [
      'Protokolle hochladen und intern zugänglich machen',
      'Vorstandsmitglieder mit Bild und Funktion verwalten',
      'Vorstandsseite auf der Vereinswebsite automatisch gepflegt',
      'Rollenbasierter Zugriff (Vorstand, Kassenwart, Spartenleiter)',
    ],
    imgFile: 'protokolle_vorstand.jpg', imgSize: '800 × 500 px',
  },
  {
    id: 'fotoalben',
    titel: 'Fotoalben',
    icon: Image,
    farbe: '#a855f7',
    beschreibung: 'Fotos vom Vereinsleben zentral speichern und für Mitglieder zugänglich machen. Alben können öffentlich oder nur für angemeldete Mitglieder sichtbar sein.',
    features: [
      'Alben erstellen und Fotos hochladen',
      'Öffentlich oder nur für Mitglieder sichtbar',
      'Galerie-Ansicht im Mitgliederportal',
      'Titelbilder pro Album definieren',
    ],
    imgFile: 'fotoalben_galerie.jpg', imgSize: '800 × 500 px',
  },
  {
    id: 'blog',
    titel: 'Blog & Vereinsnachrichten',
    icon: PenLine,
    farbe: '#84cc16',
    beschreibung: 'Beiträge aus dem Vereinsleben veröffentlichen – als internes Blog für Mitglieder oder öffentlich auf der Vereinswebsite. Mit einem visuellen Drag-&-Drop-Baukasten.',
    features: [
      'Blog-Beiträge mit Bild, Text und Kategorien',
      'Visueller Seiteneditor für Inhalte',
      'Veröffentlichung öffentlich oder nur für Mitglieder',
      'Blogger-Rolle: bestimmte Mitglieder dürfen eigene Beiträge verfassen',
      'Beiträge im Mitgliederportal und auf der öffentlichen Website',
    ],
    imgFile: 'blog_editor.jpg', imgSize: '800 × 500 px',
  },
  {
    id: 'website',
    titel: 'Öffentliche Vereinswebsite',
    icon: Globe,
    farbe: '#0891b2',
    beschreibung: 'Inkludiert: Eine vollständige öffentliche Vereinswebsite mit eigenem Design, Sparten, Kalender, Blog, Vorstand und Mitgliedsantrag – ohne zusätzlichen CMS-Aufwand.',
    features: [
      'Startseite mit Vereinsinfo, News, Veranstaltungen und Sparten',
      'Öffentlicher Veranstaltungskalender',
      'Öffentliche Spartenseiten mit individuellem Inhalt',
      'Blog / Vereinsnachrichten öffentlich einsehbar',
      'Impressum & Datenschutzseite',
      'Mitgliedsantrag-Formular online',
      'Design-Anpassung über Konfiguration (Farbe, Logo, Name)',
    ],
    imgFile: 'website_startseite.jpg', imgSize: '1200 × 750 px',
  },
  {
    id: 'konfiguration',
    titel: 'Administration & Konfiguration',
    icon: Settings,
    farbe: '#475569',
    beschreibung: 'Die gesamte Plattform lässt sich über eine zentrale Konfigurationsseite anpassen – kein Code notwendig. Von Vereinsdaten bis SMTP-Einstellungen.',
    features: [
      'Vereinsname, Logo, Primärfarbe, Rechtsform, Adresse',
      'SMTP-Konfiguration für E-Mail-Versand',
      'SEPA-Mandatsreferenz-Präfix definieren',
      'Impressum- und Datenschutz-Felder (TMG-konform)',
      'Rollen: Admin, Kassenwart, Vorstand, Spartenleiter, Blogger',
      'Portal-Zugänge pro Mitglied anlegen und aktivieren/deaktivieren',
    ],
    imgFile: 'konfiguration_admin.jpg', imgSize: '800 × 500 px',
  },
]

// ─── Mobile Features ───────────────────────────────────────────────────────────
const mobileFeatures = [
  'Installierbar auf iOS & Android (ohne App-Store)',
  'Optimiertes Touch-Interface mit Bottom-Navigation',
  'Echtzeit-Benachrichtigungen via WebSocket (Chat, Abstimmungen)',
  'Vollbild-Modus wie eine native App',
  'Funktioniert auf allen modernen Browsern und Geräten',
]

// ─── Sicherheit ───────────────────────────────────────────────────────────────
const sicherheit = [
  { icon: Lock, titel: 'Ende-zu-Ende Verschlüsselung', text: 'Chat-Nachrichten werden mit AES-256 verschlüsselt. Nur Mitglieder der Konversation können den Inhalt lesen – nicht einmal der Server-Admin.' },
  { icon: Server, titel: 'Hosting inklusive – unter Ihrer Domain', text: 'Ich hoste die Software für Sie – unter Ihrer eigenen Vereinsdomain (z. B. mitglieder.ihr-verein.de). Auf Wunsch auch Self-Hosted auf Ihrem eigenen Server.' },
  { icon: Shield, titel: 'DSGVO-konform', text: 'Alle Verarbeitungen entsprechen der DSGVO. Datenschutzerklärung direkt im System hinterlegt. Kein Tracking, keine externen CDNs.' },
]

// ─── Preise ───────────────────────────────────────────────────────────────────
const preisJaehrlich = ref(false)

const tarife = [
  { name: 'Basis',        mitglieder: 'bis 30 Mitglieder',       monatlich: 19,  jaehrlich: 16,  highlight: false },
  { name: 'Starter',      mitglieder: 'bis 100 Mitglieder',      monatlich: 39,  jaehrlich: 33,  highlight: false },
  { name: 'Standard',     mitglieder: 'bis 300 Mitglieder',      monatlich: 69,  jaehrlich: 58,  highlight: true  },
  { name: 'Professional', mitglieder: 'bis 1.000 Mitglieder',    monatlich: 99,  jaehrlich: 83,  highlight: false },
  { name: 'Enterprise',   mitglieder: 'unbegrenzte Mitglieder',  monatlich: 149, jaehrlich: 124, highlight: false },
]

const immerInklusive = [
  'Alle 17+ Module ohne Einschränkung',
  'Mitgliederverwaltung & -portal',
  'Ende-zu-Ende verschlüsselter Chat',
  'SEPA-Lastschrift & Rechnungen',
  'Digitale Abstimmungen',
  'Öffentliche Vereinswebsite',
  'Blog, Fotoalben, Veranstaltungen',
  'Online-Mitgliedsanträge',
  'Sparten & Abteilungen',
  'Mailing an Mitglieder',
  'Protokolle & Vorstandsbereich',
  'Mobile PWA (kein App-Store)',
  'SSL / HTTPS inklusive',
  'Updates & Wartung inklusive',
  'DSGVO-konformer Betrieb',
]

// ─── Kontaktformular ──────────────────────────────────────────────────────────
const form = ref({ vorname: '', nachname: '', verein: '', email: '', telefon: '', mitglieder: '', nachricht: '' })
const sending = ref(false)
const sendSuccess = ref(false)
const sendError = ref('')

async function sendKontakt() {
  sending.value = true
  sendError.value = ''
  sendSuccess.value = false
  try {
    const res = await fetch('/api/method/dms_verein.api.verein.produkt_kontakt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': window.csrf_token || '' },
      body: JSON.stringify({ ...form.value }),
    })
    const data = await res.json()
    if (!res.ok || data.exc) throw new Error(data.message || 'Fehler beim Senden')
    sendSuccess.value = true
    form.value = { vorname: '', nachname: '', verein: '', email: '', telefon: '', mitglieder: '', nachricht: '' }
  } catch (e) {
    sendError.value = e.message || 'Unbekannter Fehler. Bitte versuchen Sie es erneut.'
  } finally {
    sending.value = false
  }
}
</script>
