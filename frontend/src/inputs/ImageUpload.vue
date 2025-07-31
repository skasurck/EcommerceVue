<template>
  <div>
    <InputLabel :label="label" :error="error" />
    <input type="file" :multiple="multiple" accept="image/*" @change="onFileChange" />
    <div class="mt-2" v-if="previewUrl">
      <img :src="previewUrl" class="w-40 h-40 object-cover rounded border" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import InputLabel from './InputLabel.vue'

const props = defineProps({
  label: String,
  error: String,
  multiple: Boolean
})

const emit = defineEmits(['cambio'])
const previewUrl = ref(null)

function onFileChange(e) {
  const files = e.target.files

  // Previsualización solo de la primera imagen (para UI simple)
  if (files.length > 0) previewUrl.value = URL.createObjectURL(files[0])

  // Emite correctamente dependiendo si es multiple o no
  emit('cambio', props.multiple ? Array.from(files) : files[0])
}
</script>
