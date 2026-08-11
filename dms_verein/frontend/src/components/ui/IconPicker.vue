<template>
  <div class="relative" ref="wrapperEl">
    <!-- Trigger -->
    <div class="flex items-center gap-2">
      <button type="button" @click="open = !open"
        class="w-12 h-12 text-2xl rounded-xl border-2 transition-all flex items-center justify-center
               hover:border-primary-400 hover:bg-primary-50"
        :class="open ? 'border-primary-400 bg-primary-50' : 'border-slate-200 bg-white'">
        {{ modelValue || '?' }}
      </button>
      <div class="flex-1">
        <p class="text-sm font-medium text-slate-700">{{ modelValue || 'Kein Icon' }}</p>
        <button type="button" v-if="modelValue" @click="$emit('update:modelValue', '')"
          class="text-xs text-slate-400 hover:text-red-500 transition-colors">entfernen</button>
      </div>
    </div>

    <!-- Picker Dropdown -->
    <Transition
      enter-active-class="transition-all duration-150 ease-out"
      enter-from-class="opacity-0 scale-95 -translate-y-1"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition-all duration-100 ease-in"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 -translate-y-1">
      <div v-if="open"
        class="absolute z-50 top-14 left-0 w-80 bg-white rounded-2xl shadow-2xl border border-slate-200 p-3"
        style="max-height: 360px; overflow-y: auto;">

        <!-- Suche -->
        <input v-model="suche" type="text" placeholder="Emoji suchen…"
          class="input input-sm w-full mb-3 text-sm" ref="sucheEl" />

        <!-- Kategorien -->
        <div v-if="!suche">
          <div v-for="kat in KATEGORIEN" :key="kat.label" class="mb-3">
            <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-1">{{ kat.label }}</p>
            <div class="grid grid-cols-8 gap-0.5">
              <button v-for="icon in kat.icons" :key="icon"
                type="button"
                @click="select(icon)"
                class="w-8 h-8 text-lg rounded-lg flex items-center justify-center
                       hover:bg-primary-100 transition-colors"
                :class="modelValue === icon ? 'bg-primary-200 ring-2 ring-primary-400' : ''"
                :title="icon">
                {{ icon }}
              </button>
            </div>
          </div>
        </div>

        <!-- Suchergebnisse -->
        <div v-else>
          <div class="grid grid-cols-8 gap-0.5">
            <button v-for="icon in suchergebnisse" :key="icon"
              type="button"
              @click="select(icon)"
              class="w-8 h-8 text-lg rounded-lg flex items-center justify-center
                     hover:bg-primary-100 transition-colors"
              :class="modelValue === icon ? 'bg-primary-200 ring-2 ring-primary-400' : ''"
              :title="icon">
              {{ icon }}
            </button>
          </div>
          <p v-if="suchergebnisse.length === 0" class="text-sm text-slate-400 text-center py-4">
            Keine Treffer — tippe ein Emoji direkt ein
          </p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({ modelValue: String })
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const suche = ref('')
const wrapperEl = ref(null)
const sucheEl = ref(null)

watch(open, (val) => {
  if (val) {
    suche.value = ''
    nextTick(() => sucheEl.value?.focus())
  }
})

function select(icon) {
  emit('update:modelValue', icon)
  open.value = false
}

// Klick außerhalb schließt Picker
function onClickOutside(e) {
  if (wrapperEl.value && !wrapperEl.value.contains(e.target)) {
    open.value = false
  }
}
onMounted(() => document.addEventListener('mousedown', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside))

// Alle Icons flach für Suche
const ALLE_ICONS = []

const KATEGORIEN = [
  {
    label: 'Feuerwehr & Rettung',
    icons: ['🚒', '🔥', '🧯', '⛑️', '🚨', '🪣', '🚑', '🏥', '🩺', '🩹', '💊', '🛟', '🔦', '🪝', '⚓', '🚔', '🛡️', '🪖'],
  },
  {
    label: 'Handwerk & Technik',
    icons: ['🔧', '⚙️', '🛠️', '🏗️', '🔩', '⚡', '💡', '🔌', '🪚', '🔨', '🪛', '📐', '📏', '🧰', '🏚️', '🚜'],
  },
  {
    label: 'Ballsport',
    icons: ['⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎳', '🏓', '🏸', '🥅', '🏒', '🥌', '🎱'],
  },
  {
    label: 'Kampfsport & Fitness',
    icons: ['🥊', '🥋', '🤸', '🏋️', '🤼', '🤺', '🤾', '💪', '🧘', '🧗'],
  },
  {
    label: 'Wasser & Winter',
    icons: ['🏊', '🤽', '🏄', '🚣', '⛷️', '🏂', '🛷', '⛸️', '🌊', '⚓'],
  },
  {
    label: 'Rad, Lauf & Motor',
    icons: ['🚴', '🏃', '🚵', '🛹', '🛼', '🏇', '🏎️', '🏍️', '🚗', '✈️', '🛩️', '🚁', '⛵'],
  },
  {
    label: 'Jagd, Natur & Tiere',
    icons: ['🏹', '🎣', '🌱', '🌲', '🌍', '⛺', '🏕️', '🦅', '🐾', '🌿', '🌻', '🍀', '🏔️', '🦌', '🐗', '🐟', '🦆', '🐝', '🌾'],
  },
  {
    label: 'Musik & Kultur',
    icons: ['🎵', '🎸', '🎹', '🥁', '🎺', '🎻', '🎤', '🎭', '🎬', '🎪', '💃', '🕺', '🎼', '🪗', '🪘', '🎷'],
  },
  {
    label: 'Brauchtum & Tradition',
    icons: ['🎠', '🎡', '🎪', '🏰', '⛪', '🕍', '🌹', '🍺', '🥨', '🥳', '🎊', '🎭', '👑', '🗿', '🪄'],
  },
  {
    label: 'Wissen, Bildung & Digital',
    icons: ['📚', '📸', '🔬', '💻', '🎮', '✏️', '🔭', '🎲', '🧩', '📡', '🛸', '📰', '🖊️', '🏫'],
  },
  {
    label: 'Gemeinschaft & Soziales',
    icons: ['🤝', '🌟', '🏅', '🏆', '👥', '❤️', '🎁', '🎉', '🏠', '🌈', '🙌', '💫', '✨', '🫶', '🕊️', '♻️'],
  },
]

// Alle Icons für Suche zusammenführen
KATEGORIEN.forEach(k => ALLE_ICONS.push(...k.icons))

const suchergebnisse = computed(() => {
  if (!suche.value) return []
  const q = suche.value.toLowerCase()
  // Einfache Durchsuchung aller Icons (kein Stichwort-Matching — nur direkte Eingabe)
  return ALLE_ICONS.filter(i => i.includes(suche.value))
})
</script>
