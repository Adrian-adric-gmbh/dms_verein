<template>
  <!-- ─── Desktop Sidebar (≥ lg): fixed links ─── -->
  <aside class="hidden lg:flex flex-col fixed left-0 top-0 h-full w-60 bg-white border-r border-slate-200 z-20">
    <div class="flex items-center gap-3 px-4 py-4 border-b border-slate-100 shrink-0">
      <div class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 overflow-hidden"
        :style="verein.info?.logo ? {} : { backgroundColor: verein.info?.primaerfarbe || '#6366f1' }">
        <img v-if="verein.info?.logo" :src="verein.info.logo" class="w-full h-full object-contain p-0.5" />
        <Building2 v-else :size="18" class="text-white" />
      </div>
      <div class="min-w-0">
        <p class="font-bold text-sm truncate text-slate-900">{{ verein.info?.vereinsname }}</p>
        <p class="text-xs text-slate-400">Mitgliederbereich</p>
      </div>
    </div>
    <nav class="flex-1 p-3 space-y-0.5 overflow-y-auto">
      <RouterLink v-for="item in navItems" :key="item.name" :to="item.to" custom v-slot="{ isActive, navigate }">
        <button @click="navigate" :class="['sidebar-link w-full', isActive ? 'active' : '']">
          <component :is="item.icon" :size="17" class="shrink-0" />
          {{ item.label }}
          <span v-if="item.badge" class="ml-auto w-5 h-5 rounded-full bg-blue-600 text-white text-[10px] font-bold flex items-center justify-center">{{ item.badge }}</span>
        </button>
      </RouterLink>
    </nav>
    <div class="p-3 border-t border-slate-100 shrink-0 space-y-1">
      <a v-if="verein.info?.website" :href="verein.info.website" target="_self"
        class="sidebar-link w-full text-slate-500 hover:text-slate-700">
        <Globe :size="17" /> Zur Vereinswebsite
      </a>
      <button @click="doLogout" class="sidebar-link w-full text-red-600 hover:bg-red-50 hover:text-red-700">
        <LogOut :size="17" /> Abmelden
      </button>
    </div>
  </aside>

  <!-- ─── Mobile Fixed Header (< lg) ─── -->
  <header class="lg:hidden fixed top-0 inset-x-0 z-30 flex items-center gap-3 px-4 h-14
                 bg-white border-b border-slate-200 shadow-sm">
    <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 overflow-hidden"
      :style="verein.info?.logo ? {} : { backgroundColor: verein.info?.primaerfarbe || '#6366f1' }">
      <img v-if="verein.info?.logo" :src="verein.info.logo" class="w-full h-full object-contain p-0.5" />
      <Building2 v-else :size="16" class="text-white" />
    </div>
    <span class="font-semibold text-sm flex-1 truncate text-slate-800">
      {{ verein.info?.vereinsname || 'Mitgliederbereich' }}
    </span>
    <a v-if="verein.info?.website" :href="verein.info.website" target="_self"
      class="shrink-0 text-slate-400 hover:text-slate-600 transition-colors p-1.5 -mr-1">
      <Globe :size="18" />
    </a>
  </header>

  <!-- ─── Haupt-Inhalt ─── -->
  <main class="pt-14 lg:pt-0 lg:ml-60 pb-20 lg:pb-0 overflow-x-hidden">
    <div class="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto">
      <RouterView />
    </div>
  </main>

  <!-- ─── Mobile Bottom-Nav (< lg): fixed unten ─── -->
  <nav class="lg:hidden fixed bottom-0 inset-x-0 z-30 bg-white border-t border-slate-200 flex h-16"
       :style="{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }">
    <!-- Primäre 4 Punkte -->
    <RouterLink v-for="item in primaryNav" :key="item.name" :to="item.to" custom v-slot="{ isActive, navigate }">
      <button @click="navigate"
        class="flex-1 flex flex-col items-center justify-center gap-0.5 transition-colors relative"
        :class="isActive ? 'text-primary-600' : 'text-slate-400 hover:text-slate-600'">
        <component :is="item.icon" :size="20" />
        <span v-if="item.badge" class="absolute top-1.5 right-[18%] w-4 h-4 rounded-full bg-green-500 text-white text-[9px] font-bold flex items-center justify-center">{{ item.badge }}</span>
        <span class="text-[10px] font-semibold leading-none">{{ item.shortLabel || item.label }}</span>
      </button>
    </RouterLink>
    <!-- Mehr-Button -->
    <button @click="showMehr = true"
      class="flex-1 flex flex-col items-center justify-center gap-0.5 transition-colors relative"
      :class="moreIsActive ? 'text-primary-600' : 'text-slate-400 hover:text-slate-600'">
      <Menu :size="20" />
      <span v-if="overflowBadgeTotal > 0" class="absolute top-1.5 right-[18%] w-4 h-4 rounded-full bg-green-500 text-white text-[9px] font-bold flex items-center justify-center">{{ overflowBadgeTotal }}</span>
      <span class="text-[10px] font-semibold leading-none">Mehr</span>
    </button>
  </nav>

  <!-- ─── Mehr-Sheet ─── -->
  <Teleport to="body">
    <Transition name="sheet">
      <div v-if="showMehr" class="lg:hidden fixed inset-0 z-50 flex flex-col justify-end"
           @click.self="showMehr = false">
        <div class="absolute inset-0 bg-black/40" @click="showMehr = false" />
        <div class="relative bg-white rounded-t-2xl shadow-xl"
             :style="{ paddingBottom: 'max(env(safe-area-inset-bottom, 0px), 8px)' }">
          <!-- Handle -->
          <div class="flex justify-center pt-3 pb-2">
            <div class="w-10 h-1 rounded-full bg-slate-200" />
          </div>
          <!-- Overflow-Items -->
          <div class="px-4 pb-2 grid grid-cols-4 gap-1">
            <RouterLink v-for="item in overflowNav" :key="item.name" :to="item.to" custom v-slot="{ isActive, navigate }">
              <button @click="navigate(); showMehr = false"
                class="flex flex-col items-center gap-1.5 py-3 px-2 rounded-xl transition-colors relative"
                :class="isActive ? 'bg-primary-50 text-primary-600' : 'text-slate-500 hover:bg-slate-50'">
                <component :is="item.icon" :size="24" />
                <span v-if="item.badge" class="absolute top-2 right-3 w-4 h-4 rounded-full bg-green-500 text-white text-[9px] font-bold flex items-center justify-center">{{ item.badge }}</span>
                <span class="text-[10px] font-medium leading-tight text-center">{{ item.shortLabel || item.label }}</span>
              </button>
            </RouterLink>
          </div>
          <!-- Abmelden -->
          <div class="px-4 pt-1 pb-2 border-t border-slate-100 mt-1">
            <button @click="doLogout"
              class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-600 hover:bg-red-50 transition-colors">
              <LogOut :size="20" />
              <span class="text-sm font-medium">Abmelden</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useVereinStore } from '@/stores/verein'
import { useChatStore } from '@/stores/chat'
import { api } from '@/utils/api'
import { Building2, Home, User, CreditCard, Calendar, Image, LogOut, Vote, Globe, PenLine, MessageSquare, Menu } from 'lucide-vue-next'
import { useRealtimeRefresh } from '@/composables/useRealtimeRefresh'

const auth = useAuthStore()
const verein = useVereinStore()
const chatStore = useChatStore()
const router = useRouter()
const route = useRoute()
const aktiveAbstimmungen = ref(0)
const showMehr = ref(false)

async function ladeBadge() {
  try {
    const abs = await api.call('dms_verein.api.verein.get_meine_abstimmungen').catch(() => [])
    aktiveAbstimmungen.value = (abs || []).filter(a => a.status === 'Aktiv' && !a.bereits_abgestimmt).length
  } catch {}
}

onMounted(ladeBadge)
useRealtimeRefresh(['Abstimmung'], ladeBadge)

const navItems = computed(() => [
  { name: 'home',          label: 'Übersicht',      shortLabel: 'Start',    to: '/portal',                  icon: Home },
  { name: 'chat',          label: 'Nachrichten',     shortLabel: 'Chat',     to: '/portal/chat',             icon: MessageSquare,
    badge: chatStore.unreadTotal > 0 ? chatStore.unreadTotal : null },
  { name: 'profil',        label: 'Mein Profil',     shortLabel: 'Profil',   to: '/portal/profil',           icon: User },
  { name: 'beitraege',     label: 'Meine Beiträge',  shortLabel: 'Beiträge', to: '/portal/beitraege',        icon: CreditCard },
  { name: 'kalender',      label: 'Veranstaltungen', shortLabel: 'Events',   to: '/portal/kalender',         icon: Calendar },
  { name: 'abstimmungen',  label: 'Abstimmungen',    shortLabel: 'Abstimm.', to: '/portal/abstimmungen',     icon: Vote,
    badge: aktiveAbstimmungen.value > 0 ? aktiveAbstimmungen.value : null },
  { name: 'alben',         label: 'Fotoalben',       shortLabel: 'Alben',    to: '/portal/alben',            icon: Image },
  ...(auth.isBlogger ? [{ name: 'blog', label: 'Mein Blog', shortLabel: 'Blog', to: '/portal/blog', icon: PenLine }] : []),
])

// Primäre 4 Punkte in der Bottom-Nav
const PRIMARY_NAMES = ['home', 'chat', 'kalender', 'profil']
const primaryNav = computed(() => navItems.value.filter(i => PRIMARY_NAMES.includes(i.name)))
const overflowNav = computed(() => navItems.value.filter(i => !PRIMARY_NAMES.includes(i.name)))
const overflowBadgeTotal = computed(() => overflowNav.value.reduce((s, i) => s + (i.badge || 0), 0))
const moreIsActive = computed(() => overflowNav.value.some(i => route.path === i.to || route.path.startsWith(i.to + '/')))

async function doLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.sheet-enter-active, .sheet-leave-active {
  transition: opacity 0.2s ease;
}
.sheet-enter-active > div:last-child, .sheet-leave-active > div:last-child {
  transition: transform 0.25s cubic-bezier(0.32, 0.72, 0, 1);
}
.sheet-enter-from, .sheet-leave-to {
  opacity: 0;
}
.sheet-enter-from > div:last-child, .sheet-leave-to > div:last-child {
  transform: translateY(100%);
}
</style>
