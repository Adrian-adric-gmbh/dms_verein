import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '@/utils/api'

export const useVereinStore = defineStore('verein', () => {
  const info = ref(null)
  const loaded = ref(false)
  const strukturSingular = computed(() => info.value?.struktur_singular || 'Sparte')
  const strukturPlural = computed(() => info.value?.struktur_plural || 'Sparten')
  const strukturLeitung = computed(() => info.value?.struktur_leitung || 'Spartenleitung')
  const oeffentlicheSeiteAktiv = computed(() => info.value?.oeffentliche_seite_aktiv !== false)

  function relativeLuminance(hex) {
    const c = hex.replace('#', '')
    const r = parseInt(c.slice(0, 2), 16) / 255
    const g = parseInt(c.slice(2, 4), 16) / 255
    const b = parseInt(c.slice(4, 6), 16) / 255
    const lin = (v) => v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
  }

  function darkenToContrast(hex, minContrast = 4.5) {
    const lum = relativeLuminance(hex)
    if (1.05 / (lum + 0.05) >= minContrast) return hex   // schon lesbar
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    for (let f = 0.85; f >= 0.05; f -= 0.05) {
      const dr = Math.round(r * f)
      const dg = Math.round(g * f)
      const db = Math.round(b * f)
      const dark = `#${dr.toString(16).padStart(2, '0')}${dg.toString(16).padStart(2, '0')}${db.toString(16).padStart(2, '0')}`
      if (1.05 / (relativeLuminance(dark) + 0.05) >= minContrast) return dark
    }
    return '#1e293b'
  }

  function applyColors(data) {
    if (data?.primaerfarbe) {
      const hex = data.primaerfarbe
      document.documentElement.style.setProperty('--color-primary', hex)
      // Textfarbe auf farbigem Hintergrund (Buttons): hell oder dunkel
      const lum = relativeLuminance(hex)
      const textColor = lum > 0.22 ? '#1e293b' : '#ffffff'
      document.documentElement.style.setProperty('--color-primary-text', textColor)
      // Textfarbe auf weißem Hintergrund (Sidebar-Links): mindestens 4.5:1 Kontrast
      const onLight = darkenToContrast(hex, 4.5)
      document.documentElement.style.setProperty('--color-primary-on-light', onLight)
    }
    if (data?.sekundaerfarbe) {
      document.documentElement.style.setProperty('--color-secondary', data.sekundaerfarbe)
    }
  }

  async function load() {
    if (loaded.value) return
    try {
      info.value = await api.getVereinInfo()
      loaded.value = true
      applyColors(info.value)
    } catch {
      info.value = { vereinsname: 'Vereinsverwaltung' }
    }
  }

  async function reload() {
    loaded.value = false
    await load()
  }

  return { info, loaded, strukturSingular, strukturPlural, strukturLeitung, oeffentlicheSeiteAktiv, load, reload, applyColors }
})
