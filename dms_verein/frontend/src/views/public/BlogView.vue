<template>
  <div class="min-h-screen bg-white">
    <PublicNav />

    <!-- Hero -->
    <section class="text-white py-14 px-4 bg-gradient-to-br from-primary-600 to-primary-800">
      <div class="max-w-4xl mx-auto text-center">
        <div class="text-4xl mb-3">📰</div>
        <h1 class="text-4xl font-bold mb-2">Blog</h1>
        <p class="text-primary-100">Neuigkeiten, Berichte und Wissenswertes aus dem Verein</p>
      </div>
    </section>

    <div class="max-w-6xl mx-auto px-4 sm:px-6 py-10">
      <!-- Kategorien-Filter -->
      <div v-if="kategorien.length" class="flex flex-wrap gap-2 mb-8">
        <button @click="aktiveKategorie = ''"
          :class="aktiveKategorie === '' ? 'btn-primary' : 'btn-secondary'"
          class="btn btn-sm">Alle</button>
        <button v-for="k in kategorien" :key="k.name"
          @click="aktiveKategorie = k.name"
          :class="aktiveKategorie === k.name ? 'btn-primary' : 'btn-secondary'"
          class="btn btn-sm">{{ k.bezeichnung }}</button>
      </div>

      <!-- Beiträge -->
      <div v-if="loading" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i"
          class="rounded-2xl border border-slate-200 bg-slate-50 animate-pulse h-72" />
      </div>

      <div v-else-if="beitraege.length" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <RouterLink v-for="b in beitraege" :key="b.name"
          :to="`/blog/${b.slug || b.name}`"
          class="group rounded-2xl border border-slate-200 bg-white hover:shadow-lg hover:border-primary-200 transition-all overflow-hidden flex flex-col">
          <div class="aspect-video bg-slate-100 overflow-hidden">
            <img v-if="b.beitragsbild" :src="b.beitragsbild"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
            <div v-else class="w-full h-full flex items-center justify-center text-4xl text-slate-300">📰</div>
          </div>
          <div class="flex-1 p-5 flex flex-col">
            <div class="flex items-center gap-2 mb-3 flex-wrap">
              <span v-if="b.kategorie"
                class="text-xs px-2 py-0.5 bg-primary-50 text-primary-700 rounded-full font-medium">{{ b.kategorie_bezeichnung || b.kategorie }}</span>
              <span class="text-xs text-slate-400">{{ formatDatum(b.veroeffentlicht_am) }}</span>
            </div>
            <h3 class="font-bold text-slate-900 group-hover:text-primary-700 transition-colors mb-2 line-clamp-2">
              {{ b.titel }}
            </h3>
            <p v-if="b.zusammenfassung"
              class="text-sm text-slate-500 line-clamp-3 flex-1">{{ b.zusammenfassung }}</p>
            <div class="mt-4 flex items-center gap-2">
              <div class="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center text-xs text-primary-700 font-bold shrink-0">
                {{ b.autor_name?.[0] || '?' }}
              </div>
              <span class="text-xs text-slate-500">{{ b.autor_name || b.autor }}</span>
              <span class="ml-auto text-primary-600 text-xs font-medium group-hover:translate-x-1 transition-transform">
                Lesen →
              </span>
            </div>
          </div>
        </RouterLink>
      </div>

      <div v-else class="text-center py-16">
        <div class="text-5xl mb-4">📭</div>
        <p class="text-slate-500 font-medium">Noch keine Beiträge veröffentlicht</p>
        <p class="text-slate-400 text-sm mt-1">Schau bald wieder vorbei!</p>
      </div>

      <!-- Paginierung -->
      <div v-if="total > limit" class="flex justify-center mt-10 gap-2">
        <button @click="offset -= limit; load()" :disabled="offset <= 0"
          class="btn btn-secondary btn-sm disabled:opacity-40">← Zurück</button>
        <span class="text-sm text-slate-500 self-center">
          {{ offset + 1 }}–{{ Math.min(offset + limit, total) }} von {{ total }}
        </span>
        <button @click="offset += limit; load()" :disabled="offset + limit >= total"
          class="btn btn-secondary btn-sm disabled:opacity-40">Weiter →</button>
      </div>
    </div>

    <PublicFooter />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useApi } from '@/utils/api'
import { RouterLink } from 'vue-router'
import PublicNav from '@/components/public/PublicNav.vue'
import PublicFooter from '@/components/public/PublicFooter.vue'

const api = useApi()
const beitraege = ref([])
const kategorien = ref([])
const loading = ref(true)
const aktiveKategorie = ref('')
const limit = 12
const offset = ref(0)
const total = ref(0)

watch(aktiveKategorie, () => { offset.value = 0; load() })

async function load() {
  loading.value = true
  try {
    const res = await api.call('dms_verein.api.verein.get_blog_liste', {
      kategorie: aktiveKategorie.value,
      limit,
      offset: offset.value,
    })
    beitraege.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function formatDatum(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: 'long', year: 'numeric' })
}

onMounted(async () => {
  kategorien.value = await api.call('dms_verein.api.verein.get_blog_kategorien')
  await load()
})
</script>
