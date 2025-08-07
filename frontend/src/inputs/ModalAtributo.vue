<template>
  <div v-if="visible" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
    <div class="bg-white p-6 rounded shadow-lg w-full max-w-md">
      <h3 class="text-lg font-semibold mb-4">{{ label }}</h3>
      <input v-model="nombre" type="text" class="border w-full p-2 rounded mb-2" placeholder="Nombre del atributo" />
      <input v-model="valor" type="text" class="border w-full p-2 rounded" placeholder="Valor" />
      <div class="flex justify-end gap-2 mt-4">
        <button @click="$emit('update:visible', false)" class="px-4 py-2 bg-gray-300 rounded">Cancelar</button>
        <button @click="guardar" class="px-4 py-2 bg-blue-600 text-white rounded">Guardar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  label: String,
  visible: Boolean
})
const emit = defineEmits(['save', 'update:visible'])

const nombre = ref('')
const valor = ref('')

const guardar = () => {
  if (nombre.value.trim() && valor.value.trim()) {
    emit('save', { nombre: nombre.value.trim(), valor: valor.value.trim() })
    nombre.value = ''
    valor.value = ''
    emit('update:visible', false)
  }
}
</script>
