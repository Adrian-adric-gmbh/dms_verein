<template>
  <nav class="sticky top-0 z-40 bg-white/90 backdrop-blur border-b border-slate-200">
    <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
      <RouterLink to="/" class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-lg flex items-center justify-center overflow-hidden shrink-0"
             :style="verein.info?.logo ? {} : { backgroundColor: verein.info?.primaerfarbe || '#2563eb' }">
          <img v-if="verein.info?.logo" :src="verein.info.logo" class="w-full h-full object-contain p-1" />
          <Building2 v-else :size="20" class="text-white" />
        </div>
        <span class="font-bold text-slate-900 hidden sm:block">{{ verein.info?.vereinsname || 'Vereinsverwaltung' }}</span>
      </RouterLink>
      <div class="flex items-center gap-2">
        <RouterLink to="/blog" class="btn btn-secondary btn-sm hidden sm:inline-flex">Blog</RouterLink>
        <RouterLink to="/kalender" class="btn btn-secondary btn-sm hidden sm:inline-flex">
          <Calendar :size="14" /> Kalender
        </RouterLink>
        <RouterLink to="/antrag" class="btn btn-secondary btn-sm hidden sm:inline-flex">Mitglied werden</RouterLink>
        <RouterLink v-if="auth.canAccessAdmin" to="/admin" class="btn btn-primary btn-sm">Verwaltung</RouterLink>
        <RouterLink v-else-if="auth.isLoggedIn" to="/portal" class="btn btn-primary btn-sm">Mein Bereich</RouterLink>
        <RouterLink v-else to="/login" class="btn btn-primary btn-sm">Anmelden</RouterLink>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useVereinStore } from '@/stores/verein'
import { useAuthStore } from '@/stores/auth'
import { Building2, Calendar } from 'lucide-vue-next'

const verein = useVereinStore()
const auth = useAuthStore()
</script>
