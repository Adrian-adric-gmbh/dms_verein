<template>
  <TransitionRoot appear :show="show" as="template">
    <Dialog as="div" class="relative z-50" @close="$emit('close')">

      <!-- Backdrop -->
      <TransitionChild
        enter="ease-out duration-200" enter-from="opacity-0" enter-to="opacity-100"
        leave="ease-in duration-150" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" />
      </TransitionChild>

      <!-- Modal Container – scrollable, centers vertically on desktop, bottom-sheet on mobile -->
      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-end sm:items-center justify-center p-0 sm:p-6">

          <TransitionChild
            enter="ease-out duration-250"
            enter-from="opacity-0 translate-y-full sm:translate-y-4 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-150"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-full sm:translate-y-4 sm:scale-95">

            <DialogPanel
              :class="['bg-white w-full flex flex-col',
                       'rounded-t-2xl sm:rounded-2xl shadow-2xl',
                       'max-h-[92vh] sm:max-h-[88vh]',
                       panelWidthClass]">

              <!-- Header (fixed) -->
              <div class="flex-none flex items-center justify-between px-5 py-4 border-b border-slate-200">
                <DialogTitle class="text-lg font-semibold text-slate-900 leading-tight pr-4">{{ title }}</DialogTitle>
                <button @click="$emit('close')"
                  class="flex-none text-slate-400 hover:text-slate-700 hover:bg-slate-100 p-1.5 rounded-lg transition-colors">
                  <X :size="20" />
                </button>
              </div>

              <!-- Body (scrollable) -->
              <div class="flex-1 overflow-y-auto px-5 py-5 min-h-0">
                <slot />
              </div>

              <!-- Footer (fixed) -->
              <div v-if="$slots.footer"
                class="flex-none px-5 py-4 border-t border-slate-100 flex flex-wrap items-center justify-end gap-2 bg-slate-50 rounded-b-2xl">
                <slot name="footer" />
              </div>

            </DialogPanel>
          </TransitionChild>
        </div>
      </div>

    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { computed } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { X } from 'lucide-vue-next'

const props = defineProps({
  show: Boolean,
  title: String,
  size: { type: String, default: 'md' },
})
defineEmits(['close'])

const panelWidthClass = computed(() => ({
  sm:   'sm:w-[92vw] sm:max-w-md',
  md:   'sm:w-[85vw] sm:max-w-2xl',
  lg:   'sm:w-[82vw] sm:max-w-4xl',
  xl:   'sm:w-[88vw] sm:max-w-6xl',
  full: 'sm:w-[95vw]',
}[props.size] ?? 'sm:w-[82vw] sm:max-w-4xl'))
</script>
