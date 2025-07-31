<template>
  <div>
    <h3 class="font-medium">Atributos</h3>
    <div v-for="attr in atributos" :key="attr.id" class="mt-1">
      <label>
        <input type="checkbox" :value="attr.id" v-model="seleccionados" />
        {{ attr.atributo }}: {{ attr.valor }}
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  atributos: Array,
  modelValue: Array
})

const emit = defineEmits(['update:modelValue'])
const seleccionados = ref([...props.modelValue])

watch(seleccionados, val => emit('update:modelValue', val), { deep: true })
</script>