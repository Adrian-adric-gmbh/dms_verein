<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2>Vereinskonfiguration</h2>
        <p class="text-slate-500 mt-1">Stammdaten, Rechtliches, Finanzen & Design</p>
      </div>
      <button @click="save" :disabled="saving" class="btn btn-primary">
        <Save :size="16" /> {{ saving ? 'Wird gespeichert...' : 'Speichern' }}
      </button>
    </div>

    <AppAlert v-if="success" type="success" message="Einstellungen erfolgreich gespeichert." :dismissible="true" class="mb-4" />
    <AppAlert v-if="error" type="error" :message="error" class="mb-4" />

    <AppSpinner v-if="loading" full-page />

    <div v-else>
      <!-- Tab Navigation -->
      <div class="flex gap-1 mb-6 bg-slate-100 p-1 rounded-xl w-fit">
        <button v-for="t in tabs" :key="t.id" @click="activeTab = t.id"
          :class="['px-4 py-2 rounded-lg text-sm font-medium transition-all', activeTab === t.id ? 'bg-white shadow-sm text-slate-900' : 'text-slate-500 hover:text-slate-700']">
          {{ t.label }}
        </button>
      </div>

      <!-- Tab: Allgemein -->
      <div v-show="activeTab === 'allgemein'" class="space-y-6">
        <div class="card">
          <div class="card-header"><h3 class="text-base font-semibold">Vereinsidentität</h3></div>
          <div class="card-body grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="form-group lg:col-span-2">
              <label class="label">Vereinsname <span class="text-red-500">*</span></label>
              <input v-model="form.vereinsname" class="input text-lg font-medium" />
            </div>
            <div class="form-group">
              <label class="label">Rechtsform</label>
              <select v-model="form.rechtsform" class="input">
                <option>e.V.</option>
                <option>Körperschaft des öffentlichen Rechts</option>
                <option>GmbH</option>
                <option>Sonstige</option>
              </select>
            </div>
            <div class="form-group">
              <label class="label">Gründungsjahr</label>
              <input v-model="form.gruendungsjahr" type="number" class="input" placeholder="z.B. 1985" />
            </div>
            <div class="form-group lg:col-span-2">
              <label class="label">Vereinszweck (laut Satzung)</label>
              <textarea v-model="form.vereinszweck" class="input h-24 resize-none" placeholder="Beschreibung des satzungsgemäßen Vereinszwecks…" />
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header"><h3 class="text-base font-semibold">Anschrift (Vereinssitz)</h3></div>
          <div class="card-body grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="form-group">
              <label class="label">Straße</label>
              <input v-model="form.strasse" class="input" placeholder="Musterstraße" />
            </div>
            <div class="form-group">
              <label class="label">Hausnummer</label>
              <input v-model="form.hausnummer" class="input" placeholder="1a" />
            </div>
            <div class="form-group">
              <label class="label">PLZ</label>
              <input v-model="form.plz" class="input" placeholder="12345" maxlength="5" />
            </div>
            <div class="form-group">
              <label class="label">Ort <span class="text-red-500">*</span></label>
              <input v-model="form.ort" class="input" />
            </div>
            <div class="form-group lg:col-span-2">
              <label class="label">Bundesland</label>
              <select v-model="form.bundesland" class="input">
                <option v-for="bl in bundeslaender" :key="bl" :value="bl">{{ bl || '— bitte wählen —' }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header"><h3 class="text-base font-semibold">Kontakt</h3></div>
          <div class="card-body grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div class="form-group">
              <label class="label">Telefon</label>
              <input v-model="form.telefon" type="tel" class="input" placeholder="+49 (0) 89 ..." />
            </div>
            <div class="form-group">
              <label class="label">E-Mail</label>
              <input v-model="form.email" type="email" class="input" placeholder="info@verein.de" />
            </div>
            <div class="form-group">
              <label class="label">Website</label>
              <input v-model="form.website" class="input" placeholder="https://www.verein.de" />
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: Rechtliches -->
      <div v-show="activeTab === 'rechtlich'" class="space-y-6">
        <div class="card">
          <div class="card-header">
            <h3 class="text-base font-semibold">Vereinsregister & Steuer</h3>
            <p class="text-xs text-slate-500 mt-0.5">Pflichtangaben für das Impressum gemäß §5 TMG</p>
          </div>
          <div class="card-body grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="form-group">
              <label class="label">Vereinsregisternummer</label>
              <input v-model="form.registernummer" class="input" placeholder="z.B. VR 12345" />
            </div>
            <div class="form-group">
              <label class="label">Zuständiges Amtsgericht</label>
              <input v-model="form.amtsgericht" class="input" placeholder="z.B. Amtsgericht München" />
            </div>
            <div class="form-group">
              <label class="label">Steuernummer</label>
              <input v-model="form.steuernummer" class="input" placeholder="z.B. 123/456/78901" />
            </div>
            <div class="form-group flex items-center gap-3 pt-6">
              <input v-model="form.gemeinnuetzig" type="checkbox" :true-value="1" :false-value="0" id="gem" class="w-4 h-4 rounded cursor-pointer" />
              <label for="gem" class="text-sm font-medium cursor-pointer">Gemeinnützig anerkannt (§4 Nr. 22 UStG)</label>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3 class="text-base font-semibold">Vertretungsberechtigter Vorstand</h3>
            <p class="text-xs text-slate-500 mt-0.5">Pflichtangabe im Impressum gemäß §26 BGB</p>
          </div>
          <div class="card-body">
            <div class="form-group mb-0">
              <label class="label">Vertretungsberechtigte Personen</label>
              <textarea v-model="form.vertretung_vorstand" class="input h-28 resize-none"
                placeholder="z.B.&#10;Max Mustermann (1. Vorsitzender)&#10;Erika Musterfrau (2. Vorsitzende)" />
              <p class="text-xs text-slate-400 mt-1">Jede Person in eine eigene Zeile. Diese Angaben erscheinen im Impressum.</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3 class="text-base font-semibold">Datenschutz (DSGVO)</h3>
            <p class="text-xs text-slate-500 mt-0.5">Angaben zum Datenschutzbeauftragten gemäß Art. 37 DSGVO</p>
          </div>
          <div class="card-body grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="form-group">
              <label class="label">Datenschutzbeauftragter (Name)</label>
              <input v-model="form.datenschutzbeauftragter" class="input" placeholder="Nur falls vorhanden / gesetzlich erforderlich" />
            </div>
            <div class="form-group">
              <label class="label">Datenschutz E-Mail</label>
              <input v-model="form.datenschutz_email" type="email" class="input" placeholder="datenschutz@verein.de" />
            </div>
            <div class="form-group lg:col-span-2">
              <label class="label">URL zur Datenschutzerklärung</label>
              <input v-model="form.datenschutz_url" class="input" placeholder="https://verein.de/datenschutz (leer lassen, wenn interne Seite genutzt wird)" />
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3 class="text-base font-semibold">Datenschutzerklärung</h3>
            <p class="text-xs text-slate-500 mt-0.5">Wird auf der Datenschutz-Seite angezeigt. HTML-Formatierung ist erlaubt.</p>
          </div>
          <div class="card-body">
            <div class="form-group mb-0">
              <textarea v-model="form.datenschutz_text" class="input resize-y font-mono text-xs" style="min-height:220px"
                placeholder="&lt;h2&gt;Datenschutzerklärung&lt;/h2&gt;&#10;&lt;p&gt;Der Verein … erhebt und verarbeitet personenbezogene Daten ausschließlich für …&lt;/p&gt;&#10;&#10;&lt;h3&gt;Verantwortlicher&lt;/h3&gt;&#10;&lt;p&gt;…&lt;/p&gt;" />
              <p class="text-xs text-slate-400 mt-1">Tipp: HTML-Tags wie &lt;h2&gt;, &lt;h3&gt;, &lt;p&gt;, &lt;ul&gt;&lt;li&gt; sind erlaubt und werden im Portal korrekt gerendert.</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3 class="text-base font-semibold">Impressum – Zusatztext</h3>
            <p class="text-xs text-slate-500 mt-0.5">Ergänzende Informationen für das Impressum (z.B. Haftungsausschluss). HTML erlaubt.</p>
          </div>
          <div class="card-body">
            <div class="form-group mb-0">
              <textarea v-model="form.impressum_text" class="input resize-y font-mono text-xs" style="min-height:160px"
                placeholder="&lt;h3&gt;Haftungsausschluss&lt;/h3&gt;&#10;&lt;p&gt;Trotz sorgfältiger inhaltlicher Kontrolle …&lt;/p&gt;" />
              <p class="text-xs text-slate-400 mt-1">Dieser Text wird am Ende des automatisch generierten Impressums angezeigt.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: Finanzen -->
      <div v-show="activeTab === 'finanzen'" class="space-y-6">
        <div class="card">
          <div class="card-header"><h3 class="text-base font-semibold">Bankverbindung</h3></div>
          <div class="card-body grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="form-group">
              <label class="label">Kreditinstitut</label>
              <input v-model="form.bankname" class="input" placeholder="z.B. Volksbank Musterstadt" />
            </div>
            <div class="form-group">
              <label class="label">Kontoinhaber</label>
              <input v-model="form.konto_inhaber" class="input" placeholder="Musterverein e.V." />
            </div>
            <div class="form-group">
              <label class="label">IBAN (Vereinskonto)</label>
              <input v-model="form.iban" class="input font-mono" placeholder="DE00 0000 0000 0000 0000 00" />
            </div>
            <div class="form-group">
              <label class="label">BIC</label>
              <input v-model="form.bic" class="input font-mono" placeholder="XXXXXXXX" />
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header"><h3 class="text-base font-semibold">Beitragseinstellungen</h3></div>
          <div class="card-body grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="form-group">
              <label class="label">Geschäftsjahresbeginn</label>
              <select v-model="form.geschaeftsjahr_start" class="input">
                <option>01.01.</option><option>01.04.</option>
                <option>01.07.</option><option>01.10.</option>
              </select>
            </div>
            <div class="form-group">
              <label class="label">Beitrag fällig am</label>
              <select v-model="form.beitrag_faelligkeit" class="input">
                <option>01.01.</option><option>01.04.</option>
                <option>01.07.</option><option>01.10.</option>
              </select>
            </div>
            <div class="form-group">
              <label class="label">Standard Zahlungsintervall</label>
              <select v-model="form.beitrag_intervall" class="input">
                <option>Jährlich</option><option>Halbjährlich</option>
                <option>Vierteljährlich</option><option>Monatlich</option>
              </select>
            </div>
            <div class="form-group lg:col-span-2">
              <label class="label">Hinweistext auf Beitragsrechnungen</label>
              <textarea v-model="form.beitrag_hinweis" class="input h-20 resize-none"
                placeholder="z.B. Bitte überweisen Sie den Betrag innerhalb von 14 Tagen. Bei Fragen wenden Sie sich an den Kassenwart." />
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header"><h3 class="text-base font-semibold">SEPA Lastschrift</h3></div>
          <div class="card-body grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="form-group">
              <label class="label">SEPA Gläubiger-ID</label>
              <input v-model="form.sepa_glaeubiger_id" class="input font-mono" placeholder="DE98ZZZ09999999999" />
            </div>
            <div class="form-group">
              <label class="label">Mandatsreferenz-Prefix</label>
              <input v-model="form.sepa_mandatsreferenz_prefix" class="input" placeholder="MANDAT-" />
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: Design & Portal -->
      <div v-show="activeTab === 'design'" class="space-y-6">
        <!-- Sichtbarkeit -->
        <div class="card">
          <div class="card-header flex items-center justify-between gap-3">
            <div>
              <h3 class="text-base font-semibold">Öffentliche Vereinsseite</h3>
              <p class="text-xs text-slate-500 mt-0.5">Startseite, Antragsformular, Blog, Kalender und Produktseite</p>
            </div>
            <label class="flex items-center gap-2 cursor-pointer select-none">
              <span class="text-sm font-medium" :class="form.oeffentliche_seite_aktiv ? 'text-green-700' : 'text-slate-400'">
                {{ form.oeffentliche_seite_aktiv ? 'Aktiv' : 'Deaktiviert' }}
              </span>
              <div class="relative" @click="form.oeffentliche_seite_aktiv = form.oeffentliche_seite_aktiv ? 0 : 1">
                <div :class="['w-11 h-6 rounded-full transition-colors', form.oeffentliche_seite_aktiv ? 'bg-green-500' : 'bg-slate-300']" />
                <div :class="['absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform', form.oeffentliche_seite_aktiv ? 'translate-x-5' : '']" />
              </div>
            </label>
          </div>
          <div class="card-body">
            <p class="text-sm text-slate-500">
              Wenn deaktiviert, werden Besucher direkt zum Login weitergeleitet. Login, Impressum und
              Datenschutzerklärung bleiben erreichbar. Mitgliederportal und Admin-Bereich sind davon nicht betroffen.
            </p>
          </div>
        </div>

        <!-- Logo -->
        <div class="card">
          <div class="card-header"><h3 class="text-base font-semibold">Vereinslogo</h3></div>
          <div class="card-body">
            <div class="flex items-start gap-6">
              <!-- Current Logo Preview -->
              <div class="shrink-0">
                <div v-if="form.logo" class="w-28 h-28 rounded-xl border-2 border-slate-200 overflow-hidden bg-slate-50">
                  <img :src="form.logo" class="w-full h-full object-contain p-2" />
                </div>
                <div v-else class="w-28 h-28 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 flex flex-col items-center justify-center gap-2 text-slate-400">
                  <ImageIcon :size="28" />
                  <span class="text-xs">Kein Logo</span>
                </div>
              </div>
              <!-- Upload Controls -->
              <div class="flex-1">
                <p class="text-sm text-slate-600 mb-3">Empfohlene Größe: mindestens 200×200 px, quadratisch. Formate: PNG, JPG, SVG.</p>
                <div class="flex gap-2 flex-wrap">
                  <label class="btn btn-secondary cursor-pointer" :class="{ 'opacity-50 cursor-not-allowed': logoUploading }">
                    <Upload :size="14" /> {{ logoUploading ? 'Wird hochgeladen…' : 'Logo hochladen' }}
                    <input type="file" accept="image/*" class="hidden" :disabled="logoUploading" @change="handleLogoUpload" />
                  </label>
                  <button v-if="form.logo" @click="form.logo = ''" class="btn btn-secondary text-red-600 hover:text-red-700">
                    <Trash2 :size="14" /> Entfernen
                  </button>
                </div>
                <AppAlert v-if="logoError" type="error" :message="logoError" class="mt-3" />
              </div>
            </div>
          </div>
        </div>

        <!-- Farben -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-base font-semibold">Vereinsfarben</h3>
            <p class="text-xs text-slate-500 mt-0.5">Die Primärfarbe wird für Buttons, aktive Navigationspunkte und Akzente genutzt. Änderungen wirken sofort.</p>
          </div>
          <div class="card-body grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="form-group mb-0">
              <label class="label">Primärfarbe</label>
              <div class="flex gap-2 items-center">
                <input v-model="form.primaerfarbe" type="color" class="h-10 w-16 rounded-lg border border-slate-300 cursor-pointer p-0.5" />
                <input v-model="form.primaerfarbe" class="input flex-1 font-mono" placeholder="#2563eb" maxlength="7" />
                <button @click="form.primaerfarbe = '#2563eb'; applyColor('#2563eb')" class="btn btn-secondary btn-sm" title="Auf Standard zurücksetzen">↺</button>
              </div>
              <!-- Live Preview -->
              <div class="mt-3 flex gap-2 flex-wrap">
                <button class="btn btn-primary btn-sm" style="pointer-events:none">Primär-Button</button>
                <span class="sidebar-link active text-sm px-3 py-1.5 rounded-lg pointer-events-none" style="display:inline-flex">Aktiv-Link</span>
              </div>
            </div>
            <div class="form-group mb-0">
              <label class="label">Sekundärfarbe</label>
              <div class="flex gap-2 items-center">
                <input v-model="form.sekundaerfarbe" type="color" class="h-10 w-16 rounded-lg border border-slate-300 cursor-pointer p-0.5" />
                <input v-model="form.sekundaerfarbe" class="input flex-1 font-mono" placeholder="#0f172a" maxlength="7" />
              </div>
              <p class="text-xs text-slate-400 mt-2">Wird für Akzente und sekundäre Elemente genutzt.</p>
            </div>
          </div>
        </div>

        <!-- Externe Dienste: Google Maps -->
        <div class="card">
          <div class="card-header">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-base font-semibold">Google Maps</h3>
                <p class="text-xs text-slate-500 mt-0.5">Adresssuche &amp; Kartenanzeige bei Veranstaltungen</p>
              </div>
              <!-- Aktiv-Toggle -->
              <label class="flex items-center gap-2 cursor-pointer select-none">
                <span class="text-sm font-medium" :class="form.google_maps_aktiv ? 'text-green-700' : 'text-slate-400'">
                  {{ form.google_maps_aktiv ? 'Aktiv' : 'Deaktiviert' }}
                </span>
                <div class="relative" @click="form.google_maps_aktiv = form.google_maps_aktiv ? 0 : 1">
                  <div :class="['w-11 h-6 rounded-full transition-colors', form.google_maps_aktiv ? 'bg-green-500' : 'bg-slate-300']" />
                  <div :class="['absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform', form.google_maps_aktiv ? 'translate-x-5' : '']" />
                </div>
              </label>
            </div>
          </div>
          <div class="card-body space-y-5">
            <!-- API Key -->
            <div class="form-group mb-0">
              <label class="label">API-Schlüssel</label>
              <div class="relative">
                <input v-model="form.google_maps_key" :type="showMapsKey ? 'text' : 'password'"
                  class="input font-mono pr-10" placeholder="AIzaSy…" />
                <button type="button" @click="showMapsKey = !showMapsKey"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                  <Eye v-if="!showMapsKey" :size="15" /><EyeOff v-else :size="15" />
                </button>
              </div>
              <p class="text-xs text-slate-400 mt-1">
                Im <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noopener"
                  class="text-blue-600 hover:underline">Google Cloud Console</a>
                müssen <strong>Maps Embed API</strong> und <strong>Geocoding API</strong> aktiviert sein.
                Schlüsseleinschränkung: <strong>Websites → verein.dms-iot.de/*</strong>
              </p>
            </div>

            <!-- Verbrauchsstatistik -->
            <div class="border-t border-slate-100 pt-4">
              <div class="flex items-center justify-between mb-3">
                <p class="text-sm font-medium text-slate-700">Geocoding-Aufrufe (eigene Adresssuche)</p>
                <a href="https://console.cloud.google.com/apis/dashboard" target="_blank" rel="noopener"
                  class="text-xs text-blue-600 hover:underline flex items-center gap-1">
                  <ExternalLink :size="11" /> Google Cloud Console
                </a>
              </div>

              <AppSpinner v-if="mapsLoading" />
              <div v-else>
                <div class="grid grid-cols-3 gap-3 mb-3">
                  <div v-for="m in mapsNutzung" :key="m.monat"
                    class="bg-slate-50 rounded-xl p-3 text-center border border-slate-200">
                    <p class="text-2xl font-bold text-slate-900">{{ m.geocoding }}</p>
                    <p class="text-xs text-slate-500 mt-0.5">{{ m.monat }}</p>
                  </div>
                </div>

                <!-- Free-Tier Balken (200$ = ~40.000 Geocoding-Anfragen gratis) -->
                <div v-if="mapsNutzung.length">
                  <div class="flex justify-between text-xs text-slate-500 mb-1">
                    <span>Kostenloses Kontingent (ca. 40.000 / Monat)</span>
                    <span :class="pctColor">{{ pctUsed }}% genutzt</span>
                  </div>
                  <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div :class="['h-full rounded-full transition-all', pctColor === 'text-red-600' ? 'bg-red-500' : pctColor === 'text-amber-600' ? 'bg-amber-400' : 'bg-green-500']"
                      :style="{ width: Math.min(pctUsed, 100) + '%' }" />
                  </div>
                  <p class="text-xs text-slate-400 mt-1.5">
                    Hinweis: Map-Embed-Aufrufe (Kartenanzeige im Browser) werden von Google separat gezählt und sind hier nicht enthalten —
                    den vollständigen Verbrauch sehen Sie in der
                    <a href="https://console.cloud.google.com/apis/dashboard" target="_blank" class="text-blue-600 hover:underline">Google Cloud Console</a>.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Portal Texte -->
        <div class="card">
          <div class="card-header"><h3 class="text-base font-semibold">Portal-Texte</h3></div>
          <div class="card-body space-y-4">
            <div class="form-group">
              <label class="label">Vereinsmotto / Slogan</label>
              <input v-model="form.vereinsmotto" class="input" placeholder="Gemeinsam stark!" />
            </div>
            <div class="form-group mb-0">
              <label class="label">Willkommenstext (Portal-Startseite)</label>
              <textarea v-model="form.willkommenstext" class="input resize-y" style="min-height:120px"
                placeholder="Herzlich willkommen im Mitgliederportal! Hier finden Sie alle wichtigen Informationen …" />
              <p class="text-xs text-slate-400 mt-1">Einfaches HTML ist erlaubt (z.B. &lt;b&gt;, &lt;a href=…&gt;).</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header flex items-center justify-between gap-3">
            <div>
              <h3 class="text-base font-semibold">Organisationsstruktur</h3>
              <p class="text-xs text-slate-500 mt-0.5">Bezeichnungen für Gruppen innerhalb des Vereins</p>
            </div>
            <button type="button" class="btn btn-secondary btn-sm" @click="applyFamilienverbandPreset">
              Familienverband
            </button>
          </div>
          <div class="card-body grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div class="form-group mb-0">
              <label class="label">Singular</label>
              <input v-model="form.struktur_singular" class="input" placeholder="Familienstamm" />
            </div>
            <div class="form-group mb-0">
              <label class="label">Plural</label>
              <input v-model="form.struktur_plural" class="input" placeholder="Familienstämme" />
            </div>
            <div class="form-group mb-0">
              <label class="label">Leitung</label>
              <input v-model="form.struktur_leitung" class="input" placeholder="Stammesleitung" />
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: E-Mail -->
      <div v-show="activeTab === 'email'" class="space-y-6">
        <div class="card">
          <div class="card-header">
            <h3 class="text-base font-semibold">Ausgehende E-Mail (SMTP)</h3>
            <p class="text-xs text-slate-500 mt-0.5">Für den Versand von Beitragsrechnungen, Mitgliederbenachrichtigungen und Massen-E-Mails.</p>
          </div>
          <div class="card-body space-y-4">
            <AppAlert v-if="emailMsg" :type="emailMsg.type" :message="emailMsg.text" />

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div class="form-group lg:col-span-2">
                <label class="label">Absender-E-Mail-Adresse *</label>
                <input v-model="emailForm.email_id" type="email" class="input" placeholder="verein@example.de" />
              </div>
              <div class="form-group lg:col-span-2">
                <label class="label">Passwort</label>
                <div class="relative">
                  <input v-model="emailForm.password" :type="showPw ? 'text' : 'password'" class="input pr-10"
                    placeholder="Passwort leer lassen = unveränderter Wert" />
                  <button type="button" @click="showPw = !showPw"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                    <Eye v-if="!showPw" :size="16" />
                    <EyeOff v-else :size="16" />
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label class="label">SMTP-Server *</label>
                <input v-model="emailForm.smtp_server" class="input font-mono" placeholder="smtp.ionos.de" />
              </div>
              <div class="form-group">
                <label class="label">Port</label>
                <select v-model.number="emailForm.smtp_port" class="input">
                  <option :value="587">587 — STARTTLS (empfohlen)</option>
                  <option :value="465">465 — SSL/TLS</option>
                  <option :value="25">25 — Unverschlüsselt</option>
                </select>
              </div>
              <div class="form-group">
                <label class="label">Verschlüsselung</label>
                <div class="flex gap-4 mt-2">
                  <label class="flex items-center gap-2 cursor-pointer text-sm">
                    <input v-model="emailForm.use_tls" type="radio" :value="1" /> STARTTLS
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer text-sm">
                    <input v-model="emailForm.use_ssl" type="radio" :value="1" @change="emailForm.use_tls=0" /> SSL
                  </label>
                </div>
              </div>
              <div class="form-group">
                <label class="label">Login-Benutzername</label>
                <input v-model="emailForm.login_id" class="input" placeholder="Meist identisch mit E-Mail" />
                <p class="text-xs text-slate-400 mt-1">Leer lassen = E-Mail-Adresse wird verwendet.</p>
              </div>
            </div>

            <!-- Anbieter-Quicksets -->
            <div class="border-t border-slate-100 pt-4">
              <p class="text-xs text-slate-500 mb-2 font-medium">Schnell-Konfiguration für bekannte Anbieter:</p>
              <div class="flex flex-wrap gap-2">
                <button v-for="p in smtpPresets" :key="p.name" @click="applyPreset(p)"
                  class="text-xs px-3 py-1.5 border border-slate-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors">
                  {{ p.name }}
                </button>
              </div>
            </div>

            <!-- Test-Mail -->
            <div class="border-t border-slate-100 pt-4 flex items-center gap-3">
              <input v-model="testMailEmpfaenger" type="email" class="input flex-1"
                placeholder="Test-Mail an diese Adresse senden..." />
              <button @click="sendTestMail" :disabled="emailTestRunning || !testMailEmpfaenger"
                class="btn btn-secondary flex items-center gap-1.5 shrink-0">
                <Send :size="14" /> {{ emailTestRunning ? 'Wird gesendet...' : 'Test senden' }}
              </button>
            </div>
          </div>
          <div class="px-6 pb-5 flex justify-end">
            <button @click="saveEmailConfig" :disabled="emailSaving" class="btn btn-primary">
              <Save :size="14" /> {{ emailSaving ? 'Speichert...' : 'SMTP speichern' }}
            </button>
          </div>
        </div>

        <!-- Info-Box -->
        <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800 flex items-start gap-3">
          <Info :size="16" class="shrink-0 mt-0.5 text-blue-500" />
          <div>
            <strong>IONOS Mail Basic:</strong> Server <code class="bg-blue-100 px-1 rounded">smtp.ionos.de</code>,
            Port <code class="bg-blue-100 px-1 rounded">587</code>, STARTTLS aktiviert.
            Benutzername = vollständige E-Mail-Adresse.
          </div>
        </div>
      </div>

      <!-- Tab: Demo-Daten -->
      <div v-show="activeTab === 'demo'" class="space-y-6">
        <div class="card">
          <div class="card-header">
            <h3 class="text-base font-semibold">Demo-Daten</h3>
            <p class="text-xs text-slate-500 mt-0.5">
              Beispielverein zum Ausprobieren: Sparten mit Trainingszeiten, Mitglieder,
              Vorstand, Veranstaltungen, Fotoalben und Mitgliedsanträge.
            </p>
          </div>
          <div class="card-body space-y-4">
            <AppAlert v-if="demoMsg" :type="demoMsg.type" :message="demoMsg.text" />

            <AppSpinner v-if="demoLoading" />

            <template v-else-if="demo.aktiv">
              <div class="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm">
                <Info :size="16" class="shrink-0 mt-0.5 text-amber-600" />
                <div>
                  <strong>{{ demo.anzahl }} Demo-Datensätze sind aktiv.</strong>
                  <span v-if="demoErstelltText"> Angelegt am {{ demoErstelltText }}.</span>
                  <p class="mt-1 text-amber-800">
                    Entfernt werden ausschließlich die Datensätze, die die Demo selbst angelegt hat.
                    Eigene Mitglieder, Sparten oder Veranstaltungen bleiben unangetastet.
                  </p>
                </div>
              </div>

              <div class="flex flex-wrap gap-2">
                <span v-for="(anzahl, doctype) in demo.nach_doctype" :key="doctype"
                      class="inline-flex items-center gap-1.5 bg-slate-100 text-slate-700 text-xs font-medium px-2.5 py-1 rounded-full">
                  {{ anzahl }} × {{ doctype }}
                </span>
              </div>

              <div v-if="demo.konfiguration_von_demo" class="text-xs text-slate-500">
                Auch die Vereinskonfiguration wurde von der Demo befüllt und wird beim Entfernen
                wieder geleert.
              </div>

              <div class="pt-2 border-t border-slate-200">
                <button v-if="!demoLoeschenBestaetigen" @click="demoLoeschenBestaetigen = true"
                        class="btn btn-danger" :disabled="demoBusy">
                  <Trash2 :size="16" /> Demo-Daten löschen
                </button>
                <div v-else class="flex flex-wrap items-center gap-3">
                  <span class="text-sm font-medium text-red-700">
                    {{ demo.anzahl }} Datensätze wirklich löschen?
                  </span>
                  <button @click="demoEntfernen" class="btn btn-danger btn-sm" :disabled="demoBusy">
                    {{ demoBusy ? 'Wird gelöscht …' : 'Ja, löschen' }}
                  </button>
                  <button @click="demoLoeschenBestaetigen = false" class="btn btn-secondary btn-sm"
                          :disabled="demoBusy">Abbrechen</button>
                </div>
              </div>
            </template>

            <template v-else>
              <div class="flex items-start gap-3 bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm">
                <Info :size="16" class="shrink-0 mt-0.5 text-blue-500" />
                <div>
                  Aktuell sind keine Demo-Daten hinterlegt. Angelegt werden unter anderem
                  6 Sparten mit Trainingszeiten und Spartenleitung, 12 Mitglieder, ein besetzter
                  Vorstand, Veranstaltungen, Fotoalben und offene Mitgliedsanträge.
                  <p class="mt-1 text-blue-800">
                    Bereits vorhandene Datensätze werden dabei nicht überschrieben.
                  </p>
                </div>
              </div>
              <button @click="demoAnlegen" class="btn btn-primary" :disabled="demoBusy">
                <Database :size="16" /> {{ demoBusy ? 'Wird angelegt …' : 'Demo-Daten anlegen' }}
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '@/utils/api'
import { useVereinStore } from '@/stores/verein'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { Save, Upload, Trash2, Image as ImageIcon, Eye, EyeOff, Send, Info, ExternalLink, Database } from 'lucide-vue-next'

const verein = useVereinStore()

const form = ref({})
const loading = ref(true)
const saving = ref(false)
const success = ref(false)
const error = ref('')
const activeTab = ref('allgemein')
const logoUploading = ref(false)
const logoError = ref('')
const showMapsKey = ref(false)
const mapsNutzung = ref([])
const mapsLoading = ref(false)
const pctUsed = computed(() => {
  const current = mapsNutzung.value[0]?.geocoding || 0
  return Math.round((current / 40000) * 100)
})
const pctColor = computed(() => pctUsed.value >= 80 ? 'text-red-600' : pctUsed.value >= 50 ? 'text-amber-600' : 'text-green-600')

const tabs = [
  { id: 'allgemein', label: 'Allgemein' },
  { id: 'rechtlich', label: 'Rechtliches' },
  { id: 'finanzen', label: 'Finanzen' },
  { id: 'design', label: 'Design & Portal' },
  { id: 'email', label: 'E-Mail / SMTP' },
  { id: 'demo', label: 'Demo-Daten' },
]

// ─── Demo-Daten ───────────────────────────────────────────────────────────────
const demo = ref({ aktiv: false, anzahl: 0, nach_doctype: {}, konfiguration_von_demo: false })
const demoLoading = ref(true)
const demoBusy = ref(false)
const demoMsg = ref(null)
const demoLoeschenBestaetigen = ref(false)

const demoErstelltText = computed(() => {
  const d = demo.value.erstellt_am
  if (!d) return ''
  return new Date(d.replace(' ', 'T')).toLocaleString('de-DE', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
})

async function demoStatusLaden() {
  demoLoading.value = true
  try {
    demo.value = await api.call('dms_verein.api.demo.demo_status')
  } catch (e) {
    demoMsg.value = { type: 'error', text: e.message || 'Status der Demo-Daten nicht abrufbar.' }
  } finally {
    demoLoading.value = false
  }
}

async function demoAnlegen() {
  demoBusy.value = true
  demoMsg.value = null
  try {
    demo.value = await api.call('dms_verein.api.demo.demo_anlegen')
    demoMsg.value = { type: 'success', text: `${demo.value.anzahl} Demo-Datensätze angelegt.` }
    await verein.reload?.()
  } catch (e) {
    demoMsg.value = { type: 'error', text: e.message || 'Demo-Daten konnten nicht angelegt werden.' }
  } finally {
    demoBusy.value = false
  }
}

async function demoEntfernen() {
  demoBusy.value = true
  demoMsg.value = null
  try {
    const res = await api.call('dms_verein.api.demo.demo_entfernen')
    demo.value = res.status
    demoMsg.value = res.verblieben?.length
      ? {
          type: 'warning',
          text: `${res.geloescht} Datensätze entfernt. Noch verknüpft und daher behalten: ${res.verblieben.join(', ')}`,
        }
      : { type: 'success', text: `${res.geloescht} Demo-Datensätze entfernt.` }
    await verein.reload?.()
  } catch (e) {
    demoMsg.value = { type: 'error', text: e.message || 'Demo-Daten konnten nicht entfernt werden.' }
  } finally {
    demoBusy.value = false
    demoLoeschenBestaetigen.value = false
  }
}

// ─── E-Mail ─────────────────────────────────────────────────────────
const emailForm = ref({ email_id: '', password: '', smtp_server: '', smtp_port: 587, use_tls: 1, use_ssl: 0, login_id: '' })
const emailSaving = ref(false)
const emailTestRunning = ref(false)
const emailMsg = ref(null)
const testMailEmpfaenger = ref('')
const showPw = ref(false)

const smtpPresets = [
  { name: 'IONOS', smtp_server: 'smtp.ionos.de', smtp_port: 587, use_tls: 1, use_ssl: 0 },
  { name: 'Gmail', smtp_server: 'smtp.gmail.com', smtp_port: 587, use_tls: 1, use_ssl: 0 },
  { name: 'Strato', smtp_server: 'smtp.strato.de', smtp_port: 587, use_tls: 1, use_ssl: 0 },
  { name: 'GMX', smtp_server: 'mail.gmx.net', smtp_port: 587, use_tls: 1, use_ssl: 0 },
]

function applyPreset(p) {
  emailForm.value.smtp_server = p.smtp_server
  emailForm.value.smtp_port = p.smtp_port
  emailForm.value.use_tls = p.use_tls
  emailForm.value.use_ssl = p.use_ssl
  if (!emailForm.value.login_id) emailForm.value.login_id = emailForm.value.email_id
}

async function saveEmailConfig() {
  emailSaving.value = true; emailMsg.value = null
  try {
    await api.call('dms_verein.api.verein.save_email_konfiguration', { data: emailForm.value })
    emailMsg.value = { type: 'success', text: 'SMTP-Einstellungen gespeichert.' }
  } catch (e) {
    emailMsg.value = { type: 'error', text: e.message }
  } finally { emailSaving.value = false }
}

async function sendTestMail() {
  emailTestRunning.value = true; emailMsg.value = null
  try {
    await api.call('dms_verein.api.verein.test_email_senden', { empfaenger: testMailEmpfaenger.value })
    emailMsg.value = { type: 'success', text: `Test-E-Mail an ${testMailEmpfaenger.value} gesendet.` }
  } catch (e) {
    emailMsg.value = { type: 'error', text: 'Fehler beim Senden: ' + e.message }
  } finally { emailTestRunning.value = false }
}
// ────────────────────────────────────────────────────────────────────

const bundeslaender = ['', 'Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg',
  'Bremen', 'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 'Niedersachsen',
  'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen',
  'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen']

watch(() => form.value.primaerfarbe, (val) => {
  if (val && /^#[0-9a-fA-F]{6}$/.test(val)) applyColor(val)
})

function relativeLuminance(hex) {
  const c = hex.replace('#', '')
  const r = parseInt(c.slice(0, 2), 16) / 255
  const g = parseInt(c.slice(2, 4), 16) / 255
  const b = parseInt(c.slice(4, 6), 16) / 255
  const lin = (v) => v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
}

function darkenToContrast(hex, minContrast = 4.5) {
  const lum = relativeLuminance(hex)
  if (1.05 / (lum + 0.05) >= minContrast) return hex
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  for (let f = 0.85; f >= 0.05; f -= 0.05) {
    const dr = Math.round(r * f); const dg = Math.round(g * f); const db = Math.round(b * f)
    const dark = `#${dr.toString(16).padStart(2,'0')}${dg.toString(16).padStart(2,'0')}${db.toString(16).padStart(2,'0')}`
    if (1.05 / (relativeLuminance(dark) + 0.05) >= minContrast) return dark
  }
  return '#1e293b'
}

function applyColor(hex) {
  document.documentElement.style.setProperty('--color-primary', hex)
  const textColor = relativeLuminance(hex) > 0.22 ? '#1e293b' : '#ffffff'
  document.documentElement.style.setProperty('--color-primary-text', textColor)
  document.documentElement.style.setProperty('--color-primary-on-light', darkenToContrast(hex, 4.5))
}

function applyFamilienverbandPreset() {
  form.value.struktur_singular = 'Familienstamm'
  form.value.struktur_plural = 'Familienstämme'
  form.value.struktur_leitung = 'Stammesleitung'
}

onMounted(async () => {
  try {
    const doc = await api.getDoc('Vereins Konfiguration', 'Vereins Konfiguration')
    form.value = {
      ...(doc || {}),
      oeffentliche_seite_aktiv: doc?.oeffentliche_seite_aktiv ?? 1,
      struktur_singular: doc?.struktur_singular || 'Sparte',
      struktur_plural: doc?.struktur_plural || 'Sparten',
      struktur_leitung: doc?.struktur_leitung || 'Spartenleitung',
    }
  } catch {
    form.value = {}
  } finally {
    loading.value = false
  }
  // Demo-Status laden (steuert den Tab "Demo-Daten")
  await demoStatusLaden()

  // Maps-Nutzung laden
  mapsLoading.value = true
  try {
    mapsNutzung.value = await api.call('dms_verein.api.verein.get_maps_nutzung') || []
  } catch { mapsNutzung.value = [] }
  finally { mapsLoading.value = false }

  // E-Mail-Konfiguration laden
  try {
    const acc = await api.call('dms_verein.api.verein.get_email_konfiguration')
    if (acc && acc.email_id) {
      emailForm.value = {
        name: acc.name,
        email_id: acc.email_id || '',
        password: '',
        smtp_server: acc.smtp_server || '',
        smtp_port: acc.smtp_port || 587,
        use_tls: acc.use_tls ? 1 : 0,
        use_ssl: acc.use_ssl ? 1 : 0,
        login_id: acc.login_id || '',
      }
    }
  } catch { /* ignore */ }
})

async function handleLogoUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  logoUploading.value = true
  logoError.value = ''
  try {
    const url = await api.uploadFile(file, 'Vereins Konfiguration', 'Vereins Konfiguration')
    form.value.logo = url
    if (!form.value.logo) throw new Error('Keine Datei-URL erhalten')
  } catch (e) {
    logoError.value = 'Logo-Upload fehlgeschlagen: ' + e.message
  } finally {
    logoUploading.value = false
    event.target.value = ''
  }
}

async function save() {
  saving.value = true
  success.value = false
  error.value = ''
  try {
    await api.saveDoc({ doctype: 'Vereins Konfiguration', name: 'Vereins Konfiguration', ...form.value })
    success.value = true
    setTimeout(() => success.value = false, 3000)
    await verein.reload()
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>
