import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const unreadByKonv = ref({})
  const activeKonvName = ref(null)  // set by PortalChatView to suppress badge for open conversation

  const unreadTotal = computed(() =>
    Object.values(unreadByKonv.value).reduce((sum, n) => sum + n, 0)
  )

  function addUnread(konvName) {
    unreadByKonv.value = {
      ...unreadByKonv.value,
      [konvName]: (unreadByKonv.value[konvName] || 0) + 1,
    }
  }

  function clearUnread(konvName) {
    const copy = { ...unreadByKonv.value }
    delete copy[konvName]
    unreadByKonv.value = copy
  }

  function resetAll() {
    unreadByKonv.value = {}
  }

  return { unreadByKonv, unreadTotal, activeKonvName, addUnread, clearUnread, resetAll }
})
