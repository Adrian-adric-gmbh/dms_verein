<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-slate-100 flex items-center justify-center p-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 overflow-hidden"
             :style="{ backgroundColor: verein.info?.primaerfarbe || '#2563eb' }">
          <img v-if="verein.info?.logo" :src="verein.info.logo" class="w-full h-full object-contain p-2" />
          <Building2 v-else :size="32" class="text-white" />
        </div>
        <h1 class="text-2xl font-bold text-slate-900">{{ verein.info?.vereinsname || 'Vereinsverwaltung' }}</h1>
        <p class="text-slate-500 mt-1">Melden Sie sich an</p>
      </div>

      <div class="card">
        <div class="card-body">
          <form @submit.prevent="doLogin" class="space-y-4">
            <AppAlert v-if="error" type="error" :message="error" />
            <div class="form-group">
              <label class="label">E-Mail / Benutzername</label>
              <input v-model="email" type="text" class="input" autocomplete="username" required />
            </div>
            <div class="form-group">
              <label class="label">Passwort</label>
              <input v-model="password" type="password" class="input" autocomplete="current-password" required />
            </div>
            <button type="submit" :disabled="auth.loading" class="btn btn-primary w-full btn-lg">
              <span v-if="auth.loading">Wird angemeldet...</span>
              <span v-else>Anmelden</span>
            </button>
          </form>
        </div>
      </div>

      <div v-if="verein.oeffentlicheSeiteAktiv" class="mt-6 text-center">
        <RouterLink to="/" class="text-sm text-slate-500 hover:text-primary-600">← Zur Vereinsseite</RouterLink>
        <span class="mx-3 text-slate-300">·</span>
        <RouterLink to="/antrag" class="text-sm text-primary-600 hover:underline">Mitglied werden</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useVereinStore } from '@/stores/verein'
import AppAlert from '@/components/ui/AppAlert.vue'
import { Building2 } from 'lucide-vue-next'

const auth = useAuthStore()
const verein = useVereinStore()
const router = useRouter()
const route = useRoute()
const email = ref('')
const password = ref('')
const error = ref('')

async function doLogin() {
  error.value = ''
  try {
    await auth.login(email.value, password.value)
    const redirect = route.query.redirect
    if (redirect) { router.push(redirect); return }
    // Desktop (≥1024px): Admins → Verwaltung, sonst Portal
    if (auth.canAccessAdmin && window.innerWidth >= 1024) router.push('/admin')
    else if (auth.isMitglied) router.push('/portal')
    else router.push('/')
  } catch (e) {
    error.value = 'Falsche E-Mail oder falsches Passwort.'
  }
}
</script>
