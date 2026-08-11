<template>
  <footer class="bg-slate-900 text-slate-400 py-8 px-4 text-center text-sm">
    <p>{{ verein.info?.vereinsname }} {{ verein.info?.rechtsform }} · {{ verein.info?.ort }}</p>
    <div class="flex justify-center gap-4 mt-3 flex-wrap">
      <RouterLink to="/" class="hover:text-white">Startseite</RouterLink>
      <RouterLink to="/blog" class="hover:text-white">Blog</RouterLink>
      <RouterLink to="/kalender" class="hover:text-white">Veranstaltungen</RouterLink>
      <RouterLink to="/antrag" class="hover:text-white">Mitglied werden</RouterLink>
      <RouterLink to="/impressum" class="hover:text-white">Impressum</RouterLink>
      <a v-if="verein.info?.datenschutz_url" :href="verein.info.datenschutz_url" class="hover:text-white">Datenschutz</a>
      <RouterLink v-else to="/datenschutz" class="hover:text-white">Datenschutz</RouterLink>
      <RouterLink to="/login" class="hover:text-white">Mitglieder-Login</RouterLink>
    </div>
  </footer>
</template>

<script setup>
import { useVereinStore } from '@/stores/verein'
const verein = useVereinStore()
</script>
