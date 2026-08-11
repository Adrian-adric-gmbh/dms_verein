<template>
  <div class="border border-slate-300 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-primary-400 focus-within:border-primary-400">
    <!-- Toolbar -->
    <div class="flex flex-wrap items-center gap-0.5 px-2 py-1.5 bg-slate-50 border-b border-slate-200">
      <button v-for="cmd in toolbarCmds" :key="cmd.cmd"
        type="button"
        @click.prevent="exec(cmd.cmd, cmd.val)"
        class="px-2 py-1 rounded text-sm hover:bg-slate-200 text-slate-700 transition-colors"
        :title="cmd.label">
        <component :is="cmd.icon" v-if="cmd.icon" :size="14" />
        <span v-else class="text-xs font-mono">{{ cmd.label }}</span>
      </button>
    </div>
    <!-- Editierbereich -->
    <div
      ref="editorEl"
      contenteditable="true"
      class="min-h-[120px] px-3 py-2.5 text-sm text-slate-800 outline-none prose prose-sm max-w-none"
      @input="onInput"
      @blur="onInput"
      v-html="initialHtml"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Bold, Italic, Link, List } from 'lucide-vue-next'

const props = defineProps({ modelValue: String })
const emit = defineEmits(['update:modelValue'])

const editorEl = ref(null)
const initialHtml = ref(props.modelValue || '')

const toolbarCmds = [
  { cmd: 'bold',        label: 'B',     icon: Bold },
  { cmd: 'italic',      label: 'I',     icon: Italic },
  { cmd: 'insertUnorderedList', label: 'Liste', icon: List },
  { cmd: 'createLink',  label: 'Link',  icon: Link },
  { cmd: 'formatBlock', label: 'H2',    val: 'h2' },
  { cmd: 'formatBlock', label: 'P',     val: 'p' },
  { cmd: 'removeFormat',label: '✕ Format' },
]

function exec(cmd, val) {
  if (cmd === 'createLink') {
    const url = window.prompt('URL eingeben:', 'https://')
    if (url) document.execCommand(cmd, false, url)
  } else {
    document.execCommand(cmd, false, val || null)
  }
  editorEl.value?.focus()
  onInput()
}

function onInput() {
  emit('update:modelValue', editorEl.value?.innerHTML || '')
}

onMounted(() => {
  if (editorEl.value && props.modelValue) {
    editorEl.value.innerHTML = props.modelValue
  }
})
</script>
