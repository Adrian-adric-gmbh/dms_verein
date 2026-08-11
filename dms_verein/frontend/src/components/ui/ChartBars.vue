<template>
  <div class="space-y-2.5">
    <div v-for="(opt, i) in optionen" :key="i">
      <div class="flex items-center justify-between text-sm mb-1">
        <span class="text-slate-700 font-medium truncate mr-2">{{ opt.text }}</span>
        <span class="text-slate-500 shrink-0 text-xs">{{ opt.count }} Stimme{{ opt.count !== 1 ? 'n' : '' }} · {{ opt.prozent }}%</span>
      </div>
      <div class="h-7 bg-slate-100 rounded-lg overflow-hidden">
        <div
          class="h-full rounded-lg flex items-center justify-end pr-2 transition-all duration-700 ease-out"
          :style="`width:${Math.max(opt.prozent, opt.count > 0 ? 4 : 0)}%; background:${COLORS[i % COLORS.length]}`"
        >
          <span v-if="opt.prozent >= 15" class="text-white text-xs font-bold">{{ opt.prozent }}%</span>
        </div>
      </div>
    </div>
    <p v-if="!optionen.length" class="text-slate-400 text-sm text-center py-4">Noch keine Stimmen</p>
  </div>
</template>

<script setup>
const COLORS = ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899','#06b6d4','#84cc16']
defineProps({ optionen: { type: Array, default: () => [] } })
</script>
