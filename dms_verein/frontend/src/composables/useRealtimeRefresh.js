import { onMounted, onUnmounted } from 'vue'

/**
 * Lauscht auf frappe:dms_update und ruft callback auf, wenn ein relevanter Doctype geändert wurde.
 * @param {string[]} doctypes - DocType-Namen, auf die reagiert werden soll (leer = alle)
 * @param {function} callback - wird mit dem Event-Detail aufgerufen
 */
export function useRealtimeRefresh(doctypes, callback) {
  function handler(e) {
    if (!doctypes?.length || doctypes.includes(e.detail?.doctype)) {
      callback(e.detail)
    }
  }
  onMounted(() => window.addEventListener('frappe:dms_update', handler))
  onUnmounted(() => window.removeEventListener('frappe:dms_update', handler))
}
