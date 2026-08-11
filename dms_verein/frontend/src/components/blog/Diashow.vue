<template>
  <div class="relative overflow-hidden select-none" :class="bilder.length > 1 ? 'group' : ''">
    <!-- Slides -->
    <div class="flex transition-transform duration-500 ease-in-out"
      :style="{ transform: `translateX(-${current * 100}%)` }">
      <div v-for="(img, idx) in bilder" :key="idx"
        class="min-w-full flex items-center justify-center bg-black"
        style="max-height: 65dvh">
        <img :src="img" :alt="'Slide ' + (idx + 1)"
          class="max-h-[65dvh] max-w-full object-contain" />
      </div>
    </div>

    <!-- Prev / Next -->
    <template v-if="bilder.length > 1">
      <button @click="prev"
        class="absolute left-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-black/50 text-white
               flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/75">
        ‹
      </button>
      <button @click="next"
        class="absolute right-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-black/50 text-white
               flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/75">
        ›
      </button>

      <!-- Dots -->
      <div class="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5">
        <button v-for="(_, idx) in bilder" :key="idx"
          @click="current = idx"
          class="w-2 h-2 rounded-full transition-all"
          :class="current === idx ? 'bg-white scale-125' : 'bg-white/50'" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  bilder: { type: Array, default: () => [] },
  autoplay: { type: Boolean, default: true },
})

const current = ref(0)
let timer = null

function next() {
  current.value = (current.value + 1) % props.bilder.length
}
function prev() {
  current.value = (current.value - 1 + props.bilder.length) % props.bilder.length
}

function startAutoplay() {
  if (props.autoplay && props.bilder.length > 1) {
    timer = setInterval(next, 4000)
  }
}
function stopAutoplay() {
  if (timer) { clearInterval(timer); timer = null }
}

onMounted(startAutoplay)
onUnmounted(stopAutoplay)

watch(() => props.autoplay, (val) => {
  stopAutoplay()
  if (val) startAutoplay()
})
</script>
