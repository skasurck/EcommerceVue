<template>
  <div>
    <h3 class="font-medium">Precios Escalonados</h3>
    <div v-for="(tier, i) in tiers" :key="i" class="flex gap-2 mt-2">
      <input type="number" v-model.number="tier.cantidad_minima" placeholder="Cantidad mínima" class="border p-1 w-1/2" />
      <input type="number" v-model.number="tier.precio_unitario" placeholder="Precio unitario" class="border p-1 w-1/2" />
      <button @click="eliminar(i)" class="text-red-500">✕</button>
    </div>
    <button @click="agregar" class="mt-2 text-blue-600">+ Agregar Escalón</button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: Array
})

const emit = defineEmits(['update:modelValue'])
const tiers = ref([...props.modelValue])

function agregar() {
  tiers.value.push({ cantidad_minima: 1, precio_unitario: 0 })
}

function eliminar(i) {
  tiers.value.splice(i, 1)
}

watch(tiers, val => emit('update:modelValue', val), { deep: true })
</script>
