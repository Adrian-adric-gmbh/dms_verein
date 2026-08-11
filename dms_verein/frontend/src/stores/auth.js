import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const roles = ref([])
  const loading = ref(false)

  const isLoggedIn = computed(() => !!user.value && user.value !== 'Guest')
  const isAdmin = computed(() => roles.value.includes('Vereins Admin') || roles.value.includes('System Manager'))
  const isKassenwart = computed(() => roles.value.includes('Kassenwart'))
  const isSpartenleiter = computed(() => roles.value.includes('Spartenleiter'))
  const isVorstand = computed(() => roles.value.includes('Vorstand'))
  const isMitglied = computed(() => roles.value.includes('Mitglied'))
  const isBlogger = computed(() => roles.value.includes('Blogger'))
  const canAccessAdmin = computed(() => isAdmin.value || isKassenwart.value || isSpartenleiter.value || isVorstand.value)

  async function init() {
    try {
      const resp = await api.getSession()
      user.value = resp || 'Guest'
      if (user.value && user.value !== 'Guest') {
        await loadRoles()
      }
    } catch {
      user.value = 'Guest'
    }
  }

  // fromApi = true: window.frappe_user_roles umgehen (nach Login nötig, da Wert veraltet)
  async function loadRoles(fromApi = false) {
    const preloaded = window.frappe_user_roles
    if (!fromApi && Array.isArray(preloaded) && preloaded.length > 0) {
      roles.value = preloaded
      return
    }
    try {
      const resp = await api.call('dms_verein.api.verein.get_meine_rollen')
      roles.value = resp || []
      // Gecachten Wert aktualisieren für spätere Aufrufe in derselben Sitzung
      window.frappe_user_roles = roles.value
    } catch {
      roles.value = []
    }
  }

  async function login(usr, pwd) {
    loading.value = true
    try {
      await api.login(usr, pwd)
      const resp = await api.getSession()
      user.value = resp || 'Guest'
      if (user.value && user.value !== 'Guest') {
        // fromApi = true: stale window.frappe_user_roles nach Login ignorieren
        await loadRoles(true)
      }
      return true
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    await api.logout()
    user.value = 'Guest'
    roles.value = []
    window.frappe_user_roles = []
  }

  return { user, roles, loading, isLoggedIn, isAdmin, isKassenwart, isSpartenleiter,
           isVorstand, isMitglied, isBlogger, canAccessAdmin, init, login, logout }
})
