<template>
  <div class="min-h-screen bg-white">
    <PublicNav />

    <div v-if="loading" class="flex items-center justify-center py-24">
      <div class="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <template v-else-if="beitrag">
      <!-- Titelbild -->
      <div v-if="beitrag.beitragsbild" class="w-full max-h-[55vh] overflow-hidden">
        <img :src="beitrag.beitragsbild" class="w-full h-full object-cover" />
      </div>

      <!-- Header-Block -->
      <div class="max-w-3xl mx-auto px-4 sm:px-6 pt-10" :class="beitrag.sektionen?.length ? 'pb-8' : 'pb-12'">
        <!-- Zurück + Kategorie + Datum -->
        <div class="flex flex-wrap items-center gap-2 mb-6 text-sm">
          <RouterLink to="/blog" class="text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1">
            ← Alle Beiträge
          </RouterLink>
          <span v-if="beitrag.kategorie_bezeichnung"
            class="px-2.5 py-0.5 bg-primary-50 text-primary-700 rounded-full font-medium text-xs">
            {{ beitrag.kategorie_bezeichnung }}
          </span>
          <span class="text-slate-400">{{ formatDatum(beitrag.veroeffentlicht_am) }}</span>
        </div>

        <!-- Titel -->
        <h1 class="text-3xl sm:text-4xl font-bold text-slate-900 leading-tight mb-6">{{ beitrag.titel }}</h1>

        <!-- Autor -->
        <div class="flex items-center gap-3 pb-6 border-b border-slate-100">
          <div class="w-9 h-9 rounded-full bg-primary-100 flex items-center justify-center text-sm text-primary-700 font-bold shrink-0">
            {{ (beitrag.autor_name || beitrag.autor || '?')[0].toUpperCase() }}
          </div>
          <div>
            <div class="font-medium text-slate-800 text-sm">{{ beitrag.autor_name || beitrag.autor }}</div>
            <div class="text-xs text-slate-400">Autor</div>
          </div>
        </div>

        <!-- Teaser -->
        <div v-if="beitrag.zusammenfassung"
          class="mt-6 text-base text-slate-600 leading-relaxed p-4 bg-primary-50 rounded-xl border-l-4 border-primary-400">
          {{ beitrag.zusammenfassung }}
        </div>

        <!-- Inhalt (Legacy — nur wenn keine Sektionen) -->
        <div v-if="!beitrag.sektionen?.length && beitrag.inhalt"
          class="mt-8 prose prose-lg max-w-none prose-headings:text-slate-900 prose-a:text-primary-600"
          v-html="beitrag.inhalt" />
      </div>

      <!-- Baukasten-Sektionen -->
      <BlogSektionenRenderer v-if="beitrag.sektionen?.length" :sektionen="beitrag.sektionen" />

      <!-- Abstand + Footer-Trennlinie -->
      <div class="border-t border-slate-100 mt-12 py-8 max-w-3xl mx-auto px-4 sm:px-6">
        <RouterLink to="/blog" class="text-sm text-primary-600 hover:text-primary-700 font-medium">
          ← Zurück zu allen Beiträgen
        </RouterLink>
      </div>
    </template>

    <div v-else class="max-w-xl mx-auto px-4 py-20 text-center">
      <div class="text-5xl mb-4">🔍</div>
      <h2 class="text-2xl font-bold text-slate-800 mb-2">Beitrag nicht gefunden</h2>
      <RouterLink to="/blog" class="btn btn-primary mt-4">Zum Blog</RouterLink>
    </div>

    <PublicFooter />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useApi } from '@/utils/api'
import PublicNav from '@/components/public/PublicNav.vue'
import PublicFooter from '@/components/public/PublicFooter.vue'
import BlogSektionenRenderer from '@/components/blog/BlogSektionenRenderer.vue'

const route = useRoute()
const api = useApi()
const beitrag = ref(null)
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    beitrag.value = await api.call('dms_verein.api.verein.get_blog_beitrag', { slug: route.params.slug })
  } catch {
    beitrag.value = null
  } finally {
    loading.value = false
  }
}

function formatDatum(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: 'long', year: 'numeric' })
}

onMounted(load)
</script>
