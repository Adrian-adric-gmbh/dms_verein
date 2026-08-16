<template>
  <div class="min-h-screen bg-white">
    <!-- Nav -->
    <nav class="sticky top-0 z-40 bg-white/90 backdrop-blur border-b border-slate-200">
      <div :class="[containerClass, 'px-4 py-4 flex items-center justify-between']">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center overflow-hidden shrink-0"
               :style="verein.info?.logo ? {} : { backgroundColor: verein.info?.primaerfarbe || '#2563eb' }">
            <img v-if="verein.info?.logo" :src="verein.info.logo" class="w-full h-full object-contain p-1" />
            <Building2 v-else :size="20" class="text-white" />
          </div>
          <span class="font-bold text-slate-900">{{ verein.info?.vereinsname || 'Vereinsverwaltung' }}</span>
        </div>
        <div class="flex items-center gap-2">
          <!-- Breiten-Toggle — nur Desktop xl+ -->
          <div class="hidden xl:flex items-center gap-0.5 bg-slate-100 rounded-lg p-0.5 mr-2" title="Seitenbreite">
            <button v-for="w in widthOptions" :key="w.key" @click="setWidth(w.key)"
              :title="w.label"
              :class="['w-7 h-7 rounded-md flex items-center justify-center transition-all',
                layoutWidth === w.key ? 'bg-white shadow text-slate-800' : 'text-slate-400 hover:text-slate-600']">
              <component :is="w.icon" :size="14" />
            </button>
          </div>
          <RouterLink to="/kalender" class="btn btn-secondary btn-sm hidden sm:inline-flex">
            <Calendar :size="14" /> Kalender
          </RouterLink>
          <RouterLink to="/antrag" class="btn btn-secondary btn-sm hidden sm:inline-flex">Mitglied werden</RouterLink>
          <!-- Desktop only: Verwaltung für Admins -->
          <RouterLink v-if="auth.canAccessAdmin" to="/admin" class="btn btn-primary btn-sm hidden lg:inline-flex">Verwaltung</RouterLink>
          <!-- Mobile/Tablet für Admins: Mitglieder-App statt Verwaltung -->
          <RouterLink v-if="auth.isLoggedIn" to="/portal" :class="['btn btn-primary btn-sm', auth.canAccessAdmin ? 'lg:hidden' : '']">Mein Bereich</RouterLink>
          <RouterLink v-if="!auth.isLoggedIn" to="/login" class="btn btn-primary btn-sm">Anmelden</RouterLink>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-24 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <p v-if="verein.info?.vereinsmotto" class="text-primary-200 uppercase tracking-widest text-sm mb-3">{{ verein.info.vereinsmotto }}</p>
        <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 sm:mb-6">{{ verein.info?.vereinsname || 'Willkommen im Verein' }}</h1>
        <p v-if="verein.info?.willkommenstext" class="text-primary-100 text-base sm:text-lg max-w-2xl mx-auto mb-6 sm:mb-8">{{ verein.info.willkommenstext }}</p>
        <div class="flex flex-wrap gap-3 justify-center">
          <RouterLink to="/antrag" class="btn btn-lg bg-white text-primary-700 hover:bg-primary-50">
            Jetzt Mitglied werden
          </RouterLink>
          <RouterLink to="/kalender" class="btn btn-lg bg-white/20 text-white hover:bg-white/30 border border-white/30">
            <Calendar :size="18" /> Veranstaltungen
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- Sparten-Section: Grid ODER Detailansicht — IN-PLACE -->
    <section v-if="sparten.length" ref="spartenSection" class="py-16 px-4 bg-slate-50 min-h-[320px]">
      <div :class="containerClass">

        <!-- Kopfzeile: wechselt zwischen Übersicht und Detail -->
        <div class="flex items-center gap-3 mb-8">
          <Transition name="fade" mode="out-in">
            <div v-if="!selectedSparte" key="overview-head" class="w-full text-center">
              <h2 class="mb-2">Unsere {{ verein.strukturPlural }}</h2>
              <p class="text-slate-500">Entdecke unsere Gemeinschaften</p>
            </div>
            <div v-else key="detail-head" class="flex items-center gap-3 w-full">
              <button @click="closeSparte"
                class="flex items-center gap-1.5 text-sm text-slate-500 hover:text-primary-700 transition-colors shrink-0">
                <ChevronLeft :size="16" /> Alle {{ verein.strukturPlural }}
              </button>
              <div class="h-4 w-px bg-slate-300" />
              <span v-if="sparteData?.icon" class="text-2xl leading-none">{{ sparteData.icon }}</span>
              <h2 class="text-xl font-bold text-slate-900 m-0">{{ sparteData?.name_sparte || '…' }}</h2>
            </div>
          </Transition>
        </div>

        <!-- GRID-Ansicht -->
        <Transition name="slide-fade" mode="out-in">
          <div v-if="!selectedSparte" key="grid"
            class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            <button v-for="s in sparten" :key="s.name"
              @click="openSparte(s)"
              class="bg-white rounded-xl overflow-hidden border border-slate-200 hover:shadow-md hover:border-primary-200 transition-all group text-left cursor-pointer w-full">
              <div v-if="s.bild" class="w-full aspect-video overflow-hidden">
                <img :src="s.bild" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
              </div>
              <div class="p-5 text-center">
                <div class="text-4xl mb-3">{{ s.icon || '🏃' }}</div>
                <h3 class="text-sm font-semibold group-hover:text-primary-700 transition-colors">{{ s.name_sparte }}</h3>
                <p v-if="s.treffpunkt" class="text-xs text-slate-400 mt-1">{{ s.treffpunkt }}</p>
                <div v-if="s.beitrag" class="text-xs text-primary-600 font-medium mt-1.5">
                  + {{ formatBetrag(s.beitrag) }} {{ s.beitrag_intervall }}
                </div>
              </div>
            </button>
          </div>

          <!-- DETAIL-Ansicht (in-place) -->
          <div v-else key="detail" class="space-y-0">
            <div v-if="sparteLoading" class="py-16 flex justify-center">
              <div class="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
            </div>

            <template v-else-if="sparteData">
              <!-- Titelbild der Sparte -->
              <div v-if="sparteData.bild" class="w-full rounded-2xl overflow-hidden mb-6" style="max-height:360px">
                <img :src="sparteData.bild" class="w-full h-full object-cover" style="max-height:360px" />
              </div>

              <!-- Beitragsbanner -->
              <div v-if="sparteData.beitrag"
                class="flex items-center gap-3 px-5 py-3 bg-primary-50 border border-primary-100 rounded-xl mb-4 text-sm">
                <span class="text-primary-600 font-bold">
                  {{ formatBetrag(sparteData.beitrag) }} {{ sparteData.beitrag_intervall }}
                </span>
                <span v-if="sparteData.beitrag_bezeichnung" class="text-primary-500">— {{ sparteData.beitrag_bezeichnung }}</span>
                <span v-else class="text-primary-500">Zusatzbeitrag</span>
              </div>

              <!-- Kurzbeschreibung wenn kein Held-Banner Block -->
              <div v-if="sparteData.beschreibung && !hasHeroBlock"
                class="prose prose-slate max-w-none text-slate-600 mb-6"
                v-html="sparteData.beschreibung" />

              <!-- Sektionen -->
              <template v-for="(sektion, idx) in sparteData.sektionen" :key="idx">

                <div v-if="sektion.typ === 'Held-Banner'"
                  class="relative rounded-2xl overflow-hidden mb-4"
                  :class="sectionBg(sektion)"
                  style="min-height:220px">
                  <div v-if="sektion.bild" class="absolute inset-0">
                    <img :src="sektion.bild" class="w-full h-full object-cover" />
                    <div class="absolute inset-0 bg-black/50" />
                  </div>
                  <div class="relative z-10 p-8 text-white text-center flex flex-col items-center justify-center min-h-[220px]">
                    <h3 v-if="sektion.titel" class="text-2xl font-bold mb-2">{{ sektion.titel }}</h3>
                    <p v-if="sektion.untertitel" class="opacity-90 mb-4">{{ sektion.untertitel }}</p>
                    <a v-if="sektion.cta_text && sektion.cta_link" :href="sektion.cta_link"
                      class="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-slate-900 font-semibold rounded-xl text-sm hover:bg-slate-100 transition-colors">
                      {{ sektion.cta_text }} <ArrowRight :size="14" />
                    </a>
                  </div>
                </div>

                <div v-else-if="sektion.typ === 'Text'"
                  class="rounded-2xl mb-4 px-6 py-6" :class="sectionBg(sektion)">
                  <h3 v-if="sektion.titel" class="text-lg font-bold mb-3"
                    :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">{{ sektion.titel }}</h3>
                  <div class="prose prose-sm max-w-none"
                    :class="sektion.hintergrund === 'Dunkel' ? 'prose-invert' : ''"
                    v-html="sektion.text" />
                </div>

                <div v-else-if="sektion.typ === 'Text & Bild'"
                  class="rounded-2xl mb-4 px-6 py-6" :class="sectionBg(sektion)">
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 items-center">
                    <div :class="sektion.bild_ausrichtung === 'Links' ? 'sm:order-2' : ''">
                      <h3 v-if="sektion.titel" class="text-lg font-bold mb-3"
                        :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">{{ sektion.titel }}</h3>
                      <div class="prose prose-sm max-w-none"
                        :class="sektion.hintergrund === 'Dunkel' ? 'prose-invert' : ''"
                        v-html="sektion.text" />
                    </div>
                    <div :class="sektion.bild_ausrichtung === 'Links' ? 'sm:order-1' : ''">
                      <img v-if="sektion.bild" :src="sektion.bild" class="w-full rounded-xl shadow object-cover aspect-video" />
                    </div>
                  </div>
                </div>

                <div v-else-if="sektion.typ === 'Bildergalerie'"
                  class="rounded-2xl mb-4 px-6 py-6" :class="sectionBg(sektion)">
                  <h3 v-if="sektion.titel" class="text-lg font-bold mb-4"
                    :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">{{ sektion.titel }}</h3>
                  <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                    <div v-for="(img, i) in parsedGalerie(sektion)" :key="i"
                      class="aspect-square rounded-xl overflow-hidden cursor-pointer hover:opacity-90 transition-opacity"
                      @click="lightboxImg = img; lightboxOpen = true">
                      <img :src="img" class="w-full h-full object-cover" />
                    </div>
                  </div>
                </div>

                <div v-else-if="sektion.typ === 'Veranstaltungen'"
                  class="rounded-2xl mb-4 px-6 py-6" :class="sectionBg(sektion)">
                  <h3 class="text-lg font-bold mb-4"
                    :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">
                    {{ sektion.titel || 'Nächste Veranstaltungen' }}
                  </h3>
                  <div v-if="sparteData.veranstaltungen?.length" class="space-y-2">
                    <div v-for="ev in sparteData.veranstaltungen" :key="ev.name"
                      class="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-100 shadow-sm">
                      <div class="w-10 h-10 rounded-lg bg-primary-50 flex flex-col items-center justify-center shrink-0">
                        <span class="text-sm font-bold text-primary-700 leading-none">{{ new Date(ev.datum_von).getDate() }}</span>
                        <span class="text-xs text-primary-500">{{ new Date(ev.datum_von).toLocaleDateString('de-DE',{month:'short'}) }}</span>
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="font-medium text-sm truncate">{{ ev.titel }}</div>
                        <div v-if="ev.veranstaltungsort" class="text-xs text-slate-400">{{ ev.veranstaltungsort }}</div>
                      </div>
                    </div>
                  </div>
                  <p v-else class="text-sm text-slate-400">Keine Veranstaltungen geplant.</p>
                </div>

                <div v-else-if="sektion.typ === 'Kontaktkarte'"
                  class="rounded-2xl mb-4 px-6 py-6" :class="sectionBg(sektion)">
                  <h3 class="text-lg font-bold mb-4"
                    :class="sektion.hintergrund === 'Dunkel' ? 'text-white' : 'text-slate-900'">
                    {{ sektion.titel || 'Ansprechpartner' }}
                  </h3>
                  <div v-if="sparteData.spartenleiter"
                    class="flex items-center gap-4 p-4 bg-white rounded-xl border border-slate-100 shadow-sm max-w-sm">
                    <img v-if="sparteData.spartenleiter.foto" :src="sparteData.spartenleiter.foto"
                      class="w-14 h-14 rounded-full object-cover shrink-0" />
                    <div v-else class="w-14 h-14 rounded-full bg-primary-100 flex items-center justify-center shrink-0">
                      <User :size="22" class="text-primary-600" />
                    </div>
                    <div>
                      <div class="font-semibold">{{ sparteData.spartenleiter.vorname }} {{ sparteData.spartenleiter.nachname }}</div>
                      <div class="text-sm text-slate-500">{{ verein.strukturLeitung }}</div>
                      <a v-if="sparteData.spartenleiter.email" :href="`mailto:${sparteData.spartenleiter.email}`"
                        class="text-sm text-primary-600 hover:underline">{{ sparteData.spartenleiter.email }}</a>
                    </div>
                  </div>
                </div>

                <div v-else-if="sektion.typ === 'Trenner'" class="mb-4 flex items-center gap-3">
                  <div class="flex-1 h-px bg-slate-200" />
                  <span v-if="sektion.titel" class="text-slate-400 text-sm">{{ sektion.titel }}</span>
                  <div class="flex-1 h-px bg-slate-200" />
                </div>

                <div v-else-if="sektion.typ === 'HTML-Block'"
                  class="rounded-2xl mb-4 px-6 py-6" :class="sectionBg(sektion)"
                  v-html="sektion.html_inhalt" />

              </template>

              <!-- Fallback: keine Sektionen aber Infos vorhanden -->
              <div v-if="!sparteData.sektionen?.length" class="grid sm:grid-cols-2 gap-4 text-sm text-slate-600">
                <div v-if="sparteData.treffpunkt" class="bg-white rounded-xl p-4 border border-slate-200">
                  <div class="font-semibold text-slate-800 mb-1 flex items-center gap-1.5"><MapPin :size="13" /> Treffpunkt</div>
                  <p>{{ sparteData.treffpunkt }}</p>
                </div>
                <div v-if="sparteData.email" class="bg-white rounded-xl p-4 border border-slate-200">
                  <div class="font-semibold text-slate-800 mb-1 flex items-center gap-1.5"><Mail :size="13" /> Kontakt</div>
                  <a :href="`mailto:${sparteData.email}`" class="text-primary-600 hover:underline">{{ sparteData.email }}</a>
                </div>
                <div v-if="sparteData.gruendungsjahr" class="bg-white rounded-xl p-4 border border-slate-200">
                  <div class="font-semibold text-slate-800 mb-1">Gegründet</div>
                  <p>{{ sparteData.gruendungsjahr }}</p>
                </div>
                <div v-if="sparteData.spartenleiter" class="bg-white rounded-xl p-4 border border-slate-200">
                  <div class="font-semibold text-slate-800 mb-1 flex items-center gap-1.5"><User :size="13" /> {{ verein.strukturLeitung }}</div>
                  <p>{{ sparteData.spartenleiter.vorname }} {{ sparteData.spartenleiter.nachname }}</p>
                </div>
              </div>
            </template>
          </div>
        </Transition>
      </div>
    </section>

    <!-- Lightbox -->
    <Transition name="fade">
      <div v-if="lightboxOpen" class="fixed inset-0 z-50 bg-black/95 flex items-center justify-center p-4"
        @click.self="lightboxOpen = false">
        <img :src="lightboxImg" class="max-w-full max-h-full rounded-xl object-contain" />
        <button @click="lightboxOpen = false"
          class="absolute top-4 right-4 text-white/70 hover:text-white bg-black/30 hover:bg-black/50 rounded-full p-2 transition-colors">
          <X :size="20" />
        </button>
      </div>
    </Transition>

    <!-- Nächste Events -->
    <section v-if="events.length" class="py-16 px-4">
      <div :class="containerClass">
        <div class="flex items-center justify-between mb-8">
          <h2>Nächste Veranstaltungen</h2>
          <RouterLink to="/kalender" class="text-primary-600 hover:underline text-sm">Alle anzeigen →</RouterLink>
        </div>
        <div class="space-y-3">
          <div v-for="ev in events.slice(0,5)" :key="ev.name"
               class="flex items-center gap-4 p-4 bg-white rounded-xl border border-slate-200 hover:shadow-sm transition-all">
            <div class="w-14 h-14 rounded-xl bg-primary-50 flex flex-col items-center justify-center shrink-0">
              <div class="text-xl font-bold text-primary-700 leading-none">{{ new Date(ev.datum_von).getDate() }}</div>
              <div class="text-xs text-primary-500 uppercase">{{ monthShort(ev.datum_von) }}</div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold truncate">{{ ev.titel }}</p>
              <p class="text-sm text-slate-500">{{ ev.veranstaltungsort || 'Ort wird bekanntgegeben' }}</p>
            </div>
            <span v-if="ev.uhrzeit_von" class="text-sm text-slate-500 shrink-0">{{ ev.uhrzeit_von?.slice(0,5) }} Uhr</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Fotoalben -->
    <section v-if="alben.length" class="py-16 px-4 bg-slate-50">
      <div :class="[containerClass]">
        <div class="text-center mb-10">
          <h2 class="text-3xl font-bold mb-2">Fotoalben</h2>
          <p class="text-slate-500">Einblicke in unser Vereinsleben</p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <div v-for="a in alben" :key="a.name"
            class="card overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
            @click="openAlbum(a)">
            <div class="h-40 bg-slate-200 relative overflow-hidden">
              <img v-if="a.titelbild" :src="a.titelbild" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
              <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-200 to-slate-300">
                <Camera :size="36" class="text-slate-400" />
              </div>
              <div class="absolute bottom-2 right-2 bg-black/50 text-white text-xs px-2 py-0.5 rounded-full">
                {{ a.foto_count || 0 }} Fotos
              </div>
            </div>
            <div class="p-4">
              <h3 class="font-semibold text-sm truncate">{{ a.titel }}</h3>
              <p class="text-xs text-slate-400 mt-0.5">{{ formatDate(a.datum) }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Album Lightbox Modal -->
    <Transition name="fade">
      <div v-if="albumModal" class="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4" @click.self="albumModal = null">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
          <div class="flex items-center justify-between p-5 border-b border-slate-100">
            <div>
              <h3 class="text-lg font-bold">{{ albumModal.titel }}</h3>
              <p class="text-sm text-slate-400">{{ formatDate(albumModal.datum) }} · {{ albumFotos.length }} Fotos</p>
            </div>
            <button @click="albumModal = null" class="text-slate-400 hover:text-slate-700 p-1">
              <X :size="22" />
            </button>
          </div>
          <div class="overflow-y-auto p-5">
            <div v-if="albumLoading" class="flex justify-center py-12">
              <div class="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
            </div>
            <div v-else-if="albumFotos.length" class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div v-for="f in albumFotos" :key="f.name"
                class="aspect-square rounded-xl overflow-hidden bg-slate-100 cursor-pointer group relative"
                @click="lightboxImg = f.datei; lightboxOpen = true">
                <img :src="f.datei" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" :alt="f.titel" />
                <div v-if="f.titel" class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <p class="text-white text-xs truncate">{{ f.titel }}</p>
                </div>
              </div>
            </div>
            <p v-else class="text-center text-slate-400 py-12">Keine Fotos in diesem Album.</p>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Foto Lightbox -->
    <Transition name="fade">
      <div v-if="lightboxOpen" class="fixed inset-0 z-[60] bg-black/95 flex items-center justify-center p-4" @click.self="lightboxOpen = false">
        <button @click="lightboxOpen = false" class="absolute top-4 right-4 text-white/70 hover:text-white">
          <X :size="28" />
        </button>
        <img :src="lightboxImg" class="max-w-full max-h-[90vh] object-contain rounded-lg" />
      </div>
    </Transition>

    <!-- Blog-Teaser -->
    <section v-if="blogBeitraege.length" class="py-16 px-4">
      <div class="max-w-6xl mx-auto">
        <div class="flex items-end justify-between mb-8">
          <div>
            <h2 class="text-3xl font-bold text-slate-900">Aktuelles aus dem Verein</h2>
            <p class="text-slate-500 mt-1">Neuigkeiten und Berichte unserer Mitglieder</p>
          </div>
          <RouterLink to="/blog"
            class="text-sm font-medium text-primary-600 hover:text-primary-700 flex items-center gap-1 shrink-0 ml-4">
            Alle Beiträge →
          </RouterLink>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <RouterLink v-for="b in blogBeitraege" :key="b.name"
            :to="`/blog/${b.slug || b.name}`"
            class="group rounded-2xl border border-slate-100 bg-white overflow-hidden shadow-sm hover:shadow-md transition-all hover:-translate-y-0.5">
            <div class="aspect-[16/9] bg-slate-100 overflow-hidden">
              <img v-if="b.beitragsbild" :src="b.beitragsbild"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              <div v-else class="w-full h-full flex items-center justify-center text-4xl text-slate-300">📰</div>
            </div>
            <div class="p-5">
              <div class="flex items-center gap-2 mb-2">
                <span v-if="b.kategorie_bezeichnung"
                  class="text-xs px-2 py-0.5 bg-primary-50 text-primary-700 rounded-full font-medium">
                  {{ b.kategorie_bezeichnung }}
                </span>
                <span class="text-xs text-slate-400">{{ formatDate(b.veroeffentlicht_am) }}</span>
              </div>
              <h3 class="font-bold text-slate-900 text-lg leading-snug mb-2 line-clamp-2 group-hover:text-primary-700 transition-colors">
                {{ b.titel }}
              </h3>
              <p v-if="b.zusammenfassung" class="text-sm text-slate-500 line-clamp-2 leading-relaxed">
                {{ b.zusammenfassung }}
              </p>
            </div>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-16 px-4 bg-primary-600 text-white text-center">
      <h2 class="text-3xl font-bold mb-3">Werde Teil unseres Vereins</h2>
      <p class="text-primary-100 mb-8 max-w-xl mx-auto">Fülle einfach unser Online-Formular aus und wir melden uns schnellstmöglich bei dir.</p>
      <RouterLink to="/antrag" class="btn btn-lg bg-white text-primary-700 hover:bg-primary-50">Mitgliedsantrag stellen</RouterLink>
    </section>

    <!-- Footer -->
    <footer class="bg-slate-900 text-slate-400 py-8 px-4 text-center text-sm">
      <p>{{ verein.info?.vereinsname }} {{ verein.info?.rechtsform }} · {{ verein.info?.ort }}</p>
      <div class="flex justify-center gap-4 mt-3">
        <RouterLink to="/impressum" class="hover:text-white">Impressum</RouterLink>
        <a v-if="verein.info?.datenschutz_url" :href="verein.info.datenschutz_url" class="hover:text-white">Datenschutz</a>
        <RouterLink v-else to="/datenschutz" class="hover:text-white">Datenschutz</RouterLink>
        <RouterLink to="/login" class="hover:text-white">Mitglieder-Login</RouterLink>
      </div>
      <p class="mt-4 text-slate-600 text-xs">
        <RouterLink to="/produkt" target="_blank" class="hover:text-slate-400 transition-colors">Powered by {{ ANBIETER.produkt }}</RouterLink>
        <span class="mx-1">·</span>
        <a :href="ANBIETER.impressumUrl" target="_blank" rel="noopener" class="hover:text-slate-400 transition-colors">{{ ANBIETER.firma }}</a>
      </p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useVereinStore } from '@/stores/verein'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/utils/api'
import { Building2, Calendar, ChevronLeft, MapPin, Mail, User, ArrowRight, X, Camera } from 'lucide-vue-next'
import { ANBIETER } from '@/utils/anbieter'

const verein = useVereinStore()
const auth = useAuthStore()
const sparten = ref([])
const events = ref([])
const alben = ref([])
const blogBeitraege = ref([])
const selectedSparte = ref(null)
const sparteData = ref(null)
const sparteLoading = ref(false)
const spartenSection = ref(null)
const lightboxOpen = ref(false)
const lightboxImg = ref('')
const albumModal = ref(null)
const albumFotos = ref([])
const albumLoading = ref(false)

// ── Breiten-Toggle (nur Desktop) ──────────────────────────────────────────
const STORAGE_KEY = 'verein_layout_width'
const layoutWidth = ref(localStorage.getItem(STORAGE_KEY) || 'normal')

function setWidth(w) {
  layoutWidth.value = w
  localStorage.setItem(STORAGE_KEY, w)
}

// Inline-Komponenten für Breiten-Icons (3 Balken mit unterschiedlicher Breite)
const IconNormal = { setup: () => () => h('svg', { width: 14, height: 14, viewBox: '0 0 14 14', fill: 'currentColor' }, [
  h('rect', { x: 2, y: 2, width: 10, height: 2, rx: 1 }),
  h('rect', { x: 3, y: 6, width: 8, height: 2, rx: 1 }),
  h('rect', { x: 2, y: 10, width: 10, height: 2, rx: 1 }),
]) }
const IconBreit = { setup: () => () => h('svg', { width: 14, height: 14, viewBox: '0 0 14 14', fill: 'currentColor' }, [
  h('rect', { x: 1, y: 2, width: 12, height: 2, rx: 1 }),
  h('rect', { x: 1, y: 6, width: 12, height: 2, rx: 1 }),
  h('rect', { x: 1, y: 10, width: 12, height: 2, rx: 1 }),
]) }
const IconVoll = { setup: () => () => h('svg', { width: 14, height: 14, viewBox: '0 0 14 14', fill: 'currentColor' }, [
  h('rect', { x: 0, y: 2, width: 14, height: 2, rx: 0 }),
  h('rect', { x: 0, y: 6, width: 14, height: 2, rx: 0 }),
  h('rect', { x: 0, y: 10, width: 14, height: 2, rx: 0 }),
]) }

const widthOptions = [
  { key: 'normal', label: 'Normal (1152px)', icon: IconNormal },
  { key: 'breit',  label: 'Breit (1400px)',  icon: IconBreit },
  { key: 'voll',   label: 'Vollbild',         icon: IconVoll },
]

const containerClass = computed(() => ({
  normal: 'max-w-6xl mx-auto',
  breit:  'max-w-[1400px] mx-auto',
  voll:   'max-w-[1800px] mx-auto',
}[layoutWidth.value] ?? 'max-w-6xl mx-auto'))

onMounted(async () => {
  const [s, e, a, blog] = await Promise.all([
    api.getSparten(),
    api.getVeranstaltungen({ limit: 6 }),
    api.call('dms_verein.api.verein.get_oeffentliche_alben'),
    api.call('dms_verein.api.verein.get_blog_liste', { limit: 3 }).catch(() => ({ items: [] })),
  ])
  sparten.value = s || []
  events.value = e || []
  alben.value = a || []
  blogBeitraege.value = blog?.items || []
})

async function openAlbum(a) {
  albumModal.value = a
  albumFotos.value = []
  albumLoading.value = true
  try {
    const detail = await api.call('dms_verein.api.verein.get_oeffentliches_album', { name: a.name })
    albumFotos.value = detail?.fotos || []
  } finally { albumLoading.value = false }
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('de-DE', { day: 'numeric', month: 'long', year: 'numeric' }) : ''

async function openSparte(s) {
  selectedSparte.value = s.name
  sparteData.value = null
  sparteLoading.value = true
  spartenSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  try {
    sparteData.value = await api.call('dms_verein.api.verein.get_sparte_detail', { name: s.name })
  } finally { sparteLoading.value = false }
}

function closeSparte() {
  selectedSparte.value = null
  sparteData.value = null
}

const hasHeroBlock = computed(() => sparteData.value?.sektionen?.some(s => s.typ === 'Held-Banner'))

function sectionBg(sektion) {
  const map = { 'Hellgrau': 'bg-slate-50', 'Primärfarbe': 'bg-primary-600 text-white', 'Dunkel': 'bg-slate-900 text-white' }
  return map[sektion.hintergrund] || 'bg-white'
}

function parsedGalerie(sektion) {
  if (!sektion?.galerie_bilder) return []
  try { return JSON.parse(sektion.galerie_bilder) } catch { return [] }
}

const monthShort = (d) => new Date(d).toLocaleDateString('de-DE', { month: 'short' })
const formatBetrag = (val) => Number(val).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
</script>

<style scoped>
.slide-fade-enter-active { transition: all 0.25s ease-out; }
.slide-fade-leave-active { transition: all 0.2s ease-in; }
.slide-fade-enter-from { opacity: 0; transform: translateY(16px); }
.slide-fade-leave-to   { opacity: 0; transform: translateY(-8px); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
