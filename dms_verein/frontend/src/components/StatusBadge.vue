<template>
  <span :class="cls">{{ status }}</span>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ status: String })
const cls = computed(() => {
  const map = {
    'Aktiv': 'badge badge-green',
    'Passiv': 'badge badge-gray',
    'Gesperrt': 'badge badge-red',
    'Ausgetreten': 'badge badge-yellow',
    'Verstorben': 'badge badge-gray',
    'Neu': 'badge badge-blue',
    'In Prüfung': 'badge badge-yellow',
    'Angenommen': 'badge badge-green',
    'Abgelehnt': 'badge badge-red',
    'Geplant': 'badge badge-blue',
    'Bestätigt': 'badge badge-green',
    'Abgesagt': 'badge badge-red',
    'Abgeschlossen': 'badge badge-gray',
    'Offen': 'badge badge-yellow',
    'Bezahlt': 'badge badge-green',
  }
  return map[props.status] || 'badge badge-gray'
})
</script>
