<template>
  <div class="space-y-4">
    <!-- Gemeinsame Felder -->
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

    <!-- TEXT -->
    <template v-if="form.typ === 'Text'">
      <div class="form-group">
        <label class="label">Überschrift (optional)</label>
        <input v-model="form.titel" class="input" placeholder="Abschnittstitel" @input="emit" />
      </div>
      <div class="form-group">
        <label class="label">Text</label>
        <RichTextEditor v-model="form.text" @update:modelValue="emit" />
      </div>
    </template>

    <!-- BILD -->
    <template v-else-if="form.typ === 'Bild'">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FileUploadField label="Bild" v-model="form.bild" @update:modelValue="emit" />
        <div class="space-y-3">
          <div class="form-group">
            <label class="label">Bildunterschrift</label>
            <input v-model="form.bildunterschrift" class="input" placeholder="Optionale Beschriftung" @input="emit" />
          </div>
          <div class="form-group">
            <label class="label">Ausrichtung</label>
            <select v-model="form.bild_ausrichtung" class="input" @change="emit">
              <option value="Mitte">Zentriert</option>
              <option value="Links">Linksbündig</option>
              <option value="Rechts">Rechtsbündig</option>
            </select>
          </div>
        </div>
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

    <!-- DIASHOW -->
    <template v-else-if="form.typ === 'Diashow'">
      <div class="form-group">
        <label class="label">Überschrift (optional)</label>
        <input v-model="form.titel" class="input" @input="emit" />
      </div>
      <GalerieEditor v-model="form.bilder" @update:modelValue="emit" />
      <label class="flex items-center gap-2 cursor-pointer select-none">
        <input type="checkbox" :checked="!!form.autoplay" @change="form.autoplay = $event.target.checked ? 1 : 0; emit()" class="w-4 h-4" />
        <span class="text-sm text-slate-700">Automatisch abspielen</span>
      </label>
    </template>

    <!-- GALERIE -->
    <template v-else-if="form.typ === 'Galerie'">
      <div class="form-group">
        <label class="label">Überschrift (optional)</label>
        <input v-model="form.titel" class="input" @input="emit" />
      </div>
      <GalerieEditor v-model="form.bilder" @update:modelValue="emit" />
    </template>

    <!-- VIDEO -->
    <template v-else-if="form.typ === 'Video'">
      <div class="form-group">
        <label class="label">Überschrift (optional)</label>
        <input v-model="form.titel" class="input" @input="emit" />
      </div>
      <div class="form-group">
        <label class="label">Video-URL</label>
        <input v-model="form.video_url" class="input" placeholder="https://youtube.com/watch?v=… oder https://vimeo.com/…" @input="emit" />
        <p class="text-xs text-slate-400 mt-1">YouTube oder Vimeo-Links werden automatisch eingebettet.</p>
      </div>
    </template>

    <!-- ZITAT -->
    <template v-else-if="form.typ === 'Zitat'">
      <div class="form-group">
        <label class="label">Zitat-Text</label>
        <textarea v-model="form.text" class="input" rows="3" placeholder="»Hier steht das Zitat…«" @input="emit" />
      </div>
      <div class="form-group">
        <label class="label">Autor / Quelle (optional)</label>
        <input v-model="form.zitat_autor" class="input" placeholder="Max Mustermann" @input="emit" />
      </div>
    </template>

    <!-- INFO-BOX -->
    <template v-else-if="form.typ === 'Info-Box'">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="form-group">
          <label class="label">Überschrift (optional)</label>
          <input v-model="form.titel" class="input" @input="emit" />
        </div>
        <div class="form-group">
          <label class="label">Typ / Farbe</label>
          <select v-model="form.info_typ" class="input" @change="emit">
            <option value="Info">ℹ️ Info (blau)</option>
            <option value="Erfolg">✅ Erfolg (grün)</option>
            <option value="Warnung">⚠️ Warnung (gelb)</option>
            <option value="Hinweis">💡 Hinweis (lila)</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label class="label">Text</label>
        <textarea v-model="form.text" class="input" rows="3" @input="emit" />
      </div>
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
          rows="8" placeholder="<div>…</div> oder Embed-Code" @input="emit" />
        <p class="text-xs text-amber-600 mt-1 flex items-center gap-1">
          ⚠️ Nur vertrauenswürdigen HTML-Code einfügen — wird ungefiltert ausgegeben.
        </p>
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
