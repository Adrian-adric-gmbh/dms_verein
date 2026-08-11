<template>
  <RouterView />

  <!-- Globale Toast-Benachrichtigungen (Frappe Socket + App-Updates) -->
  <Teleport to="body">
    <div class="fixed bottom-24 lg:bottom-6 right-4 z-[9999] flex flex-col gap-2 items-end pointer-events-none">
      <TransitionGroup name="toast">
        <div
          v-for="t in socketStore.toasts"
          :key="t.id"
          class="pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl shadow-lg max-w-xs w-full"
          :class="{
            'bg-blue-600 text-white': t.type === 'info',
            'bg-green-600 text-white': t.type === 'success',
            'bg-red-600 text-white':  t.type === 'error',
            'bg-amber-500 text-white': t.type === 'warning',
          }"
        >
          <component :is="toastIcon(t.type)" :size="18" class="shrink-0 mt-0.5" />
          <div class="flex-1 min-w-0">
            <div v-if="t.title" class="font-semibold text-sm leading-tight">{{ t.title }}</div>
            <div class="text-sm leading-snug" :class="t.title ? 'text-white/90' : ''">{{ t.text }}</div>
          </div>
          <button @click="socketStore.removeToast(t.id)" class="shrink-0 opacity-70 hover:opacity-100">
            <X :size="16" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { Info, CheckCircle, AlertCircle, AlertTriangle, X } from 'lucide-vue-next'
import { useVereinStore } from '@/stores/verein'
import { useAuthStore } from '@/stores/auth'
import { useSocketStore } from '@/stores/socket'
import { useChatStore } from '@/stores/chat'

const vereinStore = useVereinStore()
const auth = useAuthStore()
const socketStore = useSocketStore()
const chatStore = useChatStore()

function toastIcon(type) {
  return { info: Info, success: CheckCircle, error: AlertCircle, warning: AlertTriangle }[type] || Info
}

onMounted(() => {
  vereinStore.load()

  // Service Worker: neue App-Version → Toast
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', (e) => {
      if (e.data?.type === 'SW_UPDATED') {
        socketStore.addToast({
          type: 'info',
          title: 'App aktualisiert',
          text: 'Eine neue Version wurde geladen.',
          duration: 8000,
        })
      }
    })
  }

  // Frappe list_update → Toast für Admins bei neuen Anträgen
  window.addEventListener('frappe:list_update', (e) => {
    if (!auth.canAccessAdmin) return
    const { doctype } = e.detail || {}
    if (doctype === 'Mitgliedsantrag') {
      socketStore.addToast({
        type: 'info',
        title: 'Neuer Antrag',
        text: 'Ein neuer Mitgliedsantrag ist eingegangen.',
      })
    }
  })

  // Globaler Chat-Listener: Badge-Zähler und ggf. Toast — aktiv auf ALLEN Seiten
  window.addEventListener('chat:chat_message', (e) => {
    const data = e.detail
    if (!data?.konversation) return
    // activeKonvName is set by PortalChatView when a conversation is open
    if (data.konversation !== chatStore.activeKonvName) {
      chatStore.addUnread(data.konversation)
      if (data.absender !== auth.user) {
        socketStore.addToast({
          type: 'info',
          title: data.absender_name || 'Neue Nachricht',
          text: data.inhalt ? (data.inhalt.length > 60 ? data.inhalt.slice(0, 60) + '…' : data.inhalt)
               : data.typ === 'Bild' ? '📷 Foto' : '📎 Datei',
          duration: 4000,
        })
      }
    }
  })
})

// Socket-Verbindung reaktiv bei Login/Logout verwalten
// immediate: true → feuert auch wenn auth.user beim Mount schon gesetzt ist
watch(() => auth.user, (newUser) => {
  if (newUser && newUser !== 'Guest') {
    socketStore.connect(newUser)
  } else {
    socketStore.disconnect()
  }
}, { immediate: true })
</script>

<style>
.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.25s ease; }
.toast-enter-from  { opacity: 0; transform: translateX(100%); }
.toast-leave-to    { opacity: 0; transform: translateX(100%); }
.toast-move        { transition: transform 0.25s ease; }
</style>
