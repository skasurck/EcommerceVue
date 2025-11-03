<template>
  <div>
    <h3 class="font-medium">Precios Escalonados</h3>
    <div v-for="(tier, i) in tiers" :key="i" class="flex gap-2 mt-2">
      <input type="number" v-model.number="tier.cantidad_minima" placeholder="Cantidad mínima" class="border p-1 w-1/2" />
      <input type="number" v-model.number="tier.precio_unitario" placeholder="Precio unitario" class="border p-1 w-1/2" />
      <button type="button" @click="eliminar(i)" class="text-red-500">✕</button>
    </div>
    <button type="button" @click="agregar" class="mt-2 text-blue-600">+ Agregar Escalón</button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])
const tiers = ref([])

// Sincroniza el estado interno con el prop `modelValue` del padre
watch(
  () => props.modelValue,
  (newVal) => {
    // Compara con el estado interno para evitar bucles de actualización
    if (JSON.stringify(newVal) !== JSON.stringify(tiers.value)) {
      // Usa una copia profunda para desacoplar los objetos
      tiers.value = JSON.parse(JSON.stringify(newVal || []))
    }
  },
  { deep: true, immediate: true }
)

// Observa cambios en el estado interno (ej. inputs del usuario) para aplicar lógica y notificar al padre
watch(
  tiers,
  (currentTiers) => {
    // Crea una copia profunda para aplicar la lógica de negocio sin mutar el origen
    const processedTiers = JSON.parse(JSON.stringify(currentTiers))

    // Ordena los escalones por cantidad mínima
    processedTiers.sort((a, b) => a.cantidad_minima - b.cantidad_minima)

    // Asegura que los precios sean descendentes
    for (let i = 1; i < processedTiers.length; i++) {
      if (processedTiers[i].precio_unitario > processedTiers[i - 1].precio_unitario) {
        processedTiers[i].precio_unitario = processedTiers[i - 1].precio_unitario
      }
    }

    // Emite el evento solo si hay una diferencia real para romper el bucle
    if (JSON.stringify(processedTiers) !== JSON.stringify(props.modelValue)) {
      emit('update:modelValue', processedTiers)
    }
  },
  { deep: true }
)

function agregar() {
  const last = tiers.value[tiers.value.length - 1]
  const nextCantidad = last ? (Number(last.cantidad_minima) || 0) + 1 : 1
  const nextPrecio = last ? last.precio_unitario : 0
  tiers.value.push({ cantidad_minima: nextCantidad, precio_unitario: nextPrecio })
}

function eliminar(i) {
  tiers.value.splice(i, 1)
}

</script>
