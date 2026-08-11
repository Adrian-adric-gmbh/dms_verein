<template>
  <div class="flex flex-col sm:flex-row items-center gap-4">
    <!-- SVG Donut -->
    <div class="relative shrink-0" :style="`width:${size}px;height:${size}px`">
      <svg :width="size" :height="size" class="rotate-[-90deg]">
        <circle :cx="cx" :cy="cy" :r="r" fill="none" stroke="#f1f5f9" :stroke-width="stroke" />
        <circle
          v-for="(seg, i) in segments" :key="i"
          :cx="cx" :cy="cy" :r="r" fill="none"
          :stroke="seg.color"
          :stroke-width="stroke"
          :stroke-dasharray="`${seg.dash} ${circumference}`"
          :stroke-dashoffset="-seg.offset"
          class="transition-all duration-700"
        />
      </svg>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span class="text-2xl font-bold text-slate-800">{{ total }}</span>
        <span class="text-xs text-slate-500 leading-tight">Stimmen</span>
      </div>
    </div>
    <!-- Legende -->
    <div class="flex flex-col gap-2 min-w-0 flex-1">
      <div v-for="(opt, i) in optionen" :key="i" class="flex items-center gap-2">
        <span class="w-3 h-3 rounded-full shrink-0" :style="`background:${COLORS[i % COLORS.length]}`" />
        <span class="text-sm text-slate-700 truncate flex-1">{{ opt.text }}</span>
        <span class="text-sm font-semibold text-slate-800 shrink-0">{{ opt.prozent }}%</span>
        <span class="text-xs text-slate-400 shrink-0">({{ opt.count }})</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const COLORS = ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899','#06b6d4','#84cc16']

const props = defineProps({
  optionen: { type: Array, default: () => [] },
  size: { type: Number, default: 140 },
  stroke: { type: Number, default: 28 },
})

const cx = computed(() => props.size / 2)
const cy = computed(() => props.size / 2)
const r  = computed(() => (props.size - props.stroke) / 2)
const circumference = computed(() => 2 * Math.PI * r.value)
const total = computed(() => props.optionen.reduce((s, o) => s + (o.count || 0), 0))

const segments = computed(() => {
  let offset = 0
  return props.optionen.map((opt, i) => {
    const pct = total.value > 0 ? opt.count / total.value : 0
    const dash = pct * circumference.value
    const seg = { color: COLORS[i % COLORS.length], dash, offset }
    offset += dash
    return seg
  })
})
</script>
