<template>
  <div class="space-y-4">
    <!-- Gemeinsame Felder: Hintergrund -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="form-group">
        <label class="label">Hintergrund</label>
        <select v-model="form.hintergrund" class="input" @change="emit">
          <option value="Weiß">Weiß</option>
          <option value="Hellgrau">Hellgrau</option>
          <option value="Primärfarbe">Primärfarbe</option>
          <option value="Dunkel">Dunkel</option>
        </select>
      </div>
    </div>

    <!-- HELD-BANNER -->
    <template v-if="form.typ === 'Held-Banner'">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="form-group">
          <label class="label">Headline</label>
          <input v-model="form.titel" class="input" placeholder="Große Überschrift" @input="emit" />
        </div>
        <div class="form-group">
          <label class="label">Untertitel</label>
          <input v-model="form.untertitel" class="input" placeholder="Kurze Beschreibung" @input="emit" />
        </div>
        <div class="form-group">
          <label class="label">Button-Text</label>
          <input v-model="form.cta_text" class="input" placeholder="z.B. Mehr erfahren" @input="emit" />
        </div>
        <div class="form-group">
          <label class="label">Button-Link</label>
          <input v-model="form.cta_link" class="input" placeholder="https://…" @input="emit" />
        </div>
      </div>
      <FileUploadField label="Hintergrundbild" v-model="form.bild" @update:modelValue="emit" />
    </template>

    <!-- TEXT -->
    <template v-else-if="form.typ === 'Text'">
      <div class="form-group">
        <label class="label">Überschrift (optional)</label>
        <input v-model="form.titel" class="input" placeholder="Abschnittstitel" @input="emit" />
      </div>
      <div class="form-group">
        <label class="label">Text</label>
        <RichTextEditor v-model="form.text" @update:modelValue="emit" />
      </div>
    </template>

    <!-- TEXT & BILD -->
    <template v-else-if="form.typ === 'Text & Bild'">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="form-group">
          <label class="label">Überschrift</label>
          <input v-model="form.titel" class="input" @input="emit" />
        </div>
        <div class="form-group">
          <label class="label">Bild-Position</label>
          <select v-model="form.bild_ausrichtung" class="input" @change="emit">
            <option value="Rechts">Bild rechts</option>
            <option value="Links">Bild links</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label class="label">Text</label>
        <RichTextEditor v-model="form.text" @update:modelValue="emit" />
      </div>
      <FileUploadField label="Bild" v-model="form.bild" @update:modelValue="emit" />
    </template>

    <!-- BILDERGALERIE -->
    <template v-else-if="form.typ === 'Bildergalerie'">
      <div class="form-group">
        <label class="label">Überschrift (optional)</label>
        <input v-model="form.titel" class="input" @input="emit" />
      </div>
      <GalerieEditor v-model="form.galerie_bilder" @update:modelValue="emit" />
    </template>

    <!-- VERANSTALTUNGEN / KONTAKTKARTE — keine eigenen Felder -->
    <template v-else-if="form.typ === 'Veranstaltungen' || form.typ === 'Kontaktkarte'">
      <div class="form-group">
        <label class="label">Überschrift (optional)</label>
        <input v-model="form.titel" class="input" @input="emit" />
      </div>
      <p class="text-sm text-slate-400 bg-slate-50 rounded-lg p-3 border border-slate-200">
        Die Daten werden automatisch aus dem Frappe-System geladen — keine weitere Konfiguration nötig.
      </p>
    </template>

    <!-- TRENNER -->
    <template v-else-if="form.typ === 'Trenner'">
      <div class="form-group">
        <label class="label">Beschriftung (optional)</label>
        <input v-model="form.titel" class="input" placeholder="z.B. ✦" @input="emit" />
      </div>
    </template>

    <!-- HTML-BLOCK -->
    <template v-else-if="form.typ === 'HTML-Block'">
      <div class="form-group">
        <label class="label">HTML / Embed-Code</label>
        <textarea v-model="form.html_inhalt" class="input font-mono text-xs"
          rows="6" placeholder="<div>…</div>" @input="emit" />
        <p class="text-xs text-orange-600 mt-1">Nur vertrauenswürdigen HTML-Code einfügen.</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import FileUploadField from '@/components/builder/FileUploadField.vue'
import RichTextEditor from '@/components/builder/RichTextEditor.vue'
import GalerieEditor from '@/components/builder/GalerieEditor.vue'

const props = defineProps({ sektion: Object })
const emit_ = defineEmits(['update'])

const form = reactive({ ...props.sektion })

watch(() => props.sektion, (val) => Object.assign(form, val), { deep: true })

function emit() {
  emit_('update', { ...form })
}
</script>
