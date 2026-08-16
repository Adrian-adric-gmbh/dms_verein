<template>
  <div class="min-h-screen bg-slate-50">

    <!-- ─── Sidebar Desktop (≥ md): fixed ─── -->
    <aside :class="['hidden md:flex flex-col fixed left-0 top-0 h-full bg-white border-r border-slate-200 transition-all duration-200 z-20',
                    sidebarOpen ? 'w-60' : 'w-14']">
      <!-- Logo -->
      <div class="flex items-center gap-3 px-3 py-4 border-b border-slate-100 shrink-0 overflow-hidden">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 overflow-hidden"
          :style="verein.info?.logo ? {} : { backgroundColor: verein.info?.primaerfarbe || '#6366f1' }">
          <img v-if="verein.info?.logo" :src="verein.info.logo" class="w-full h-full object-cover" />
          <Building2 v-else :size="16" class="text-white" />
        </div>
        <span v-if="sidebarOpen" class="font-bold text-slate-900 truncate text-sm">
          {{ verein.info?.vereinsname || 'Vereinsverwaltung' }}
        </span>
      </div>
      <!-- Nav -->
      <nav class="flex-1 p-2 space-y-0.5 overflow-y-auto">
        <template v-for="item in navItems" :key="item.name">
          <RouterLink :to="item.to" custom v-slot="{ isActive, navigate }">
            <button @click="navigate"
              :class="['sidebar-link w-full', isActive ? 'active' : '', !sidebarOpen ? 'justify-center px-0' : '']"
              :title="!sidebarOpen ? item.label : ''">
              <component :is="item.icon" :size="17" class="shrink-0" />
              <span v-if="sidebarOpen" class="truncate">{{ item.label }}</span>
              <span v-if="sidebarOpen && item.badge" class="ml-auto badge badge-red text-xs">{{ item.badge }}</span>
            </button>
          </RouterLink>
        </template>
      </nav>
      <!-- Bottom -->
      <div class="p-2 border-t border-slate-100 space-y-1 shrink-0">
        <RouterLink v-if="verein.oeffentlicheSeiteAktiv" to="/" custom v-slot="{ navigate }">
          <button @click="navigate"
            :class="['sidebar-link w-full', !sidebarOpen ? 'justify-center px-0' : '']"
            title="Zur Vereinsseite">
            <ExternalLink :size="17" class="shrink-0" />
            <span v-if="sidebarOpen">Vereinsseite</span>
          </button>
        </RouterLink>
        <button @click="doLogout"
          :class="['sidebar-link w-full text-red-600 hover:bg-red-50 hover:text-red-700', !sidebarOpen ? 'justify-center px-0' : '']">
          <LogOut :size="17" class="shrink-0" />
          <span v-if="sidebarOpen">Abmelden</span>
        </button>
      </div>
    </aside>

    <!-- ─── Mobile Drawer ─── -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-200"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0">
        <div v-if="mobileOpen" class="fixed inset-0 z-[60] md:hidden flex">
          <div class="absolute inset-0 bg-black/40" @click="mobileOpen = false" />
          <aside class="relative w-60 bg-white flex flex-col shadow-2xl overflow-y-auto">
            <div class="flex items-center gap-3 px-4 py-4 border-b border-slate-100 shrink-0">
              <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 overflow-hidden"
                :style="verein.info?.logo ? {} : { backgroundColor: verein.info?.primaerfarbe || '#6366f1' }">
                <img v-if="verein.info?.logo" :src="verein.info.logo" class="w-full h-full object-cover" />
                <Building2 v-else :size="16" class="text-white" />
              </div>
              <span class="font-bold text-sm truncate flex-1">{{ verein.info?.vereinsname || 'Verwaltung' }}</span>
              <button @click="mobileOpen = false" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100">
                <X :size="18" />
              </button>
            </div>
            <nav class="flex-1 p-3 space-y-0.5">
              <template v-for="item in navItems" :key="item.name">
                <RouterLink :to="item.to" custom v-slot="{ isActive, navigate }">
                  <button @click="() => { navigate(); mobileOpen = false }"
                    :class="['sidebar-link w-full', isActive ? 'active' : '']">
                    <component :is="item.icon" :size="17" class="shrink-0" />
                    <span class="truncate">{{ item.label }}</span>
                  </button>
                </RouterLink>
              </template>
            </nav>
            <div class="p-3 border-t border-slate-100 space-y-1 shrink-0">
              <button @click="doLogout" class="sidebar-link w-full text-red-600 hover:bg-red-50">
                <LogOut :size="17" /> Abmelden
              </button>
            </div>
          </aside>
        </div>
      </Transition>
    </Teleport>

    <!-- ─── Haupt-Bereich: Offset für fixe Sidebar ─── -->
    <div :class="['flex-1 min-w-0 flex flex-col transition-all duration-200',
                  sidebarOpen ? 'md:ml-60' : 'md:ml-14']">
      <!-- Topbar: fixed, Content bekommt pt-14 -->
      <header class="fixed top-0 right-0 z-30 h-14 flex items-center gap-3 px-4 bg-white border-b border-slate-200"
              :style="{ left: headerLeft }">
        <button @click="mobileOpen = true" class="md:hidden text-slate-500 hover:text-slate-800 p-1.5 rounded-lg hover:bg-slate-100">
          <Menu :size="20" />
        </button>
        <button @click="sidebarOpen = !sidebarOpen" class="hidden md:block text-slate-500 hover:text-slate-800 p-1 rounded">
          <Menu :size="20" />
        </button>
        <h1 class="text-base font-semibold text-slate-900 flex-1 truncate">{{ currentTitle }}</h1>
        <div class="flex items-center gap-2 shrink-0">
          <span class="hidden sm:block text-sm text-slate-500 truncate max-w-[180px]">{{ auth.user }}</span>
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold shrink-0"
            :style="{ backgroundColor: verein.info?.primaerfarbe || '#6366f1' }">
            {{ initials }}
          </div>
        </div>
      </header>
      <!-- Content: pt-14 für fixen Header -->
      <main class="pt-14 px-4 pb-4 sm:px-6 sm:pb-6 flex-1">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useVereinStore } from '@/stores/verein'
import { useChatStore } from '@/stores/chat'
import {
  LayoutDashboard, Users, FileText, Layers, Calendar, Image,
  Shield, Wallet, BookOpen, Settings, Building2, Menu, X,
  LogOut, ExternalLink, Rss, Receipt, Tags, Mail, Landmark, Vote, MessageSquare
} from 'lucide-vue-next'

const auth = useAuthStore()
const verein = useVereinStore()
const chatStore = useChatStore()
const route = useRoute()
const router = useRouter()
const sidebarOpen = ref(true)
const mobileOpen = ref(false)

// Hilfsfunktion: Hat der User mindestens eine der Rollen?
function hasRole(...rollen) {
  return rollen.some(r => auth.roles.includes(r))
}
const ADMIN   = ['Vereins Admin', 'System Manager']
const KASSENWART = [...ADMIN, 'Kassenwart']
const VORSTAND   = [...ADMIN, 'Vorstand']
const ALLE    = [...ADMIN, 'Kassenwart', 'Vorstand', 'Spartenleiter']
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)
function onResize() { windowWidth.value = window.innerWidth }
onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))
const headerLeft = computed(() =>
  windowWidth.value >= 768 ? (sidebarOpen.value ? '240px' : '56px') : '0px'
)

const ALL_NAV = [
  { name: 'dashboard',       label: 'Dashboard',         to: '/admin',                  icon: LayoutDashboard, rollen: ALLE },
  { name: 'mitglieder',      label: 'Mitglieder',        to: '/admin/mitglieder',       icon: Users,           rollen: ALLE },
  { name: 'antraege',        label: 'Anträge',           to: '/admin/antraege',         icon: FileText,        rollen: ADMIN },
  { name: 'sparten',         label: 'Sparten',           to: '/admin/sparten',          icon: Layers,          rollen: [...ADMIN, 'Spartenleiter'] },
  { name: 'events',          label: 'Veranstaltungen',   to: '/admin/veranstaltungen',  icon: Calendar,        rollen: ALLE },
  { name: 'alben',           label: 'Fotoalben',         to: '/admin/fotoalben',        icon: Image,           rollen: ALLE },
  { name: 'vorstand',        label: 'Vorstand',          to: '/admin/vorstand',         icon: Shield,          rollen: [...ADMIN, ...VORSTAND] },
  { name: 'finanzen',        label: 'Finanzen',          to: '/admin/finanzen',         icon: Wallet,          rollen: KASSENWART },
  { name: 'beitragsklassen', label: 'Beitragsklassen',  to: '/admin/beitragsklassen',  icon: Tags,            rollen: KASSENWART },
  { name: 'rechnungen',      label: 'Rechnungen',        to: '/admin/rechnungen',       icon: Receipt,         rollen: KASSENWART },
  { name: 'sepa',            label: 'SEPA Lastschrift',  to: '/admin/sepa',             icon: Landmark,        rollen: KASSENWART },
  { name: 'mailing',         label: 'Mailing',           to: '/admin/mailing',          icon: Mail,            rollen: [...ADMIN, ...VORSTAND] },
  { name: 'protokolle',      label: 'Protokolle',        to: '/admin/protokolle',       icon: BookOpen,        rollen: [...ADMIN, ...VORSTAND] },
  { name: 'abstimmungen',    label: 'Abstimmungen',      to: '/admin/abstimmungen',     icon: Vote,            rollen: [...ADMIN, ...VORSTAND] },
  { name: 'blog',            label: 'Blog',              to: '/admin/blog',             icon: Rss,             rollen: [...ADMIN, 'Spartenleiter'] },
  { name: 'chat',            label: 'Nachrichten',       to: '/portal/chat',            icon: MessageSquare,   rollen: ALLE },
  { name: 'config',          label: 'Konfiguration',     to: '/admin/konfiguration',    icon: Settings,        rollen: ADMIN },
]

const navItems = computed(() =>
  ALL_NAV.filter(item => hasRole(...item.rollen))
    .map(item => item.name === 'sparten' ? { ...item, label: verein.strukturPlural } : item)
    .map(item => item.name === 'chat'
      ? { ...item, badge: chatStore.unreadTotal > 0 ? chatStore.unreadTotal : null }
      : item)
)

const titleMap = {
  'admin-dashboard': 'Dashboard', 'admin-mitglieder': 'Mitglieder',
  'admin-mitglieder-import': 'Mitglieder importieren',
  'admin-mitglied-detail': 'Mitglied', 'admin-antraege': 'Mitgliedsanträge',
  'admin-sparten': 'Sparten', 'admin-events': 'Veranstaltungen',
  'admin-alben': 'Fotoalben', 'admin-vorstand': 'Vorstand',
  'admin-finanzen': 'Finanzen', 'admin-protokolle': 'Protokolle',
  'admin-abstimmungen': 'Abstimmungen', 'admin-config': 'Vereinskonfiguration', 'admin-blog': 'Blog-Verwaltung',
  'admin-sparten-builder': 'Seiten-Baukasten', 'admin-beitragsklassen': 'Beitragsklassen',
  'admin-rechnungen': 'Beitragsrechnungen', 'admin-mailing': 'Massen-E-Mail',
  'admin-sepa': 'SEPA Lastschrift',
  'portal-chat': 'Nachrichten',
}

const currentTitle = computed(() => route.name === 'admin-sparten' ? verein.strukturPlural : titleMap[route.name] || 'Verwaltung')
const initials = computed(() => (auth.user || '').split('@')[0].substring(0, 2).toUpperCase())

async function doLogout() {
  await auth.logout()
  router.push('/login')
}
</script>
