import { defineStore } from 'pinia'
import { ref } from 'vue'
import { io } from 'socket.io-client'

export const useSocketStore = defineStore('socket', () => {
  const connected = ref(false)
  const toasts = ref([])          // { id, type, title, text, timeout }
  let socket = null
  let toastCounter = 0

  // ─── Verbindung ──────────────────────────────────────────────────────────────

  let _siteName = null

  async function _getSiteName() {
    if (_siteName) return _siteName
    try {
      const res = await fetch('/api/method/dms_verein.api.verein.get_site_name',
        { credentials: 'include' })
      const json = await res.json()
      _siteName = json.message?.sitename || window.location.hostname
    } catch {
      _siteName = window.location.hostname
    }
    return _siteName
  }

  async function connect(user) {
    if (socket?.connected) return
    if (!user || user === 'Guest') return

    // Frappe publishes events to namespace /{sitename}.
    // The external domain (verein.dms-iot.de) ≠ internal sitename (mysite.localhost),
    // so we must fetch the real sitename from Frappe.
    const sitename = await _getSiteName()
    const url = `${window.location.origin}/${sitename}`
    console.log('[Socket] Connecting to', url, 'sitename:', sitename)

    socket = io(url, {
      path: '/socket.io/',
      withCredentials: true,
    })

    socket.on('connect', () => {
      connected.value = true
      console.log('[Socket] Connected, id=', socket.id, 'nsp=', socket.nsp)
    })

    socket.on('disconnect', (reason) => {
      connected.value = false
      console.log('[Socket] Disconnected:', reason)
    })

    socket.on('connect_error', (err) => {
      connected.value = false
      console.error('[Socket] connect_error:', err.message)
    })

    // Log ALL incoming events for debugging
    socket.onAny((event, ...args) => {
      console.log('[Socket] Event received:', event, args)
    })

    // Frappe-Events ────────────────────────────────────────────────────────────

    socket.on('list_update', (data) => {
      window.dispatchEvent(new CustomEvent('frappe:list_update', { detail: data }))
    })

    socket.on('doc_update', (data) => {
      window.dispatchEvent(new CustomEvent('frappe:doc_update', { detail: data }))
    })

    socket.on('sepa_mandat_update', (data) => {
      window.dispatchEvent(new CustomEvent('frappe:sepa_mandat_update', { detail: data }))
    })

    socket.on('dms_update', (data) => {
      window.dispatchEvent(new CustomEvent('frappe:dms_update', { detail: data }))
    })

    // Chat events
    socket.on('chat_message', (data) => {
      console.log('[Socket] chat_message received:', data)
      window.dispatchEvent(new CustomEvent('chat:chat_message', { detail: data }))
    })
    socket.on('chat_deleted', (data) => {
      window.dispatchEvent(new CustomEvent('chat:chat_deleted', { detail: data }))
    })
    socket.on('chat_konv_update', (data) => {
      window.dispatchEvent(new CustomEvent('chat:chat_konv_update', { detail: data }))
    })
    socket.on('chat_test', (data) => {
      console.log('[Socket] *** REALTIME TEST OK ***', data)
    })

    // Frappe msgprint (Server-seitige Meldungen)
    socket.on('msgprint', (data) => {
      if (data?.message) {
        addToast({ type: 'info', title: 'Hinweis', text: data.message })
      }
    })
  }

  function disconnect() {
    socket?.disconnect()
    socket = null
    connected.value = false
  }

  // Subscribe to a chat event; returns an unsubscribe function
  function on(event, handler) {
    const key = `chat:${event}`
    const listener = (e) => handler(e.detail)
    window.addEventListener(key, listener)
    return () => window.removeEventListener(key, listener)
  }

  // ─── Toast-Benachrichtigungen ─────────────────────────────────────────────

  function addToast({ type = 'info', title = '', text = '', duration = 5000 }) {
    const id = ++toastCounter
    toasts.value.push({ id, type, title, text })
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration)
    }
    return id
  }

  function removeToast(id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return { connected, toasts, connect, disconnect, addToast, removeToast, on }
})
