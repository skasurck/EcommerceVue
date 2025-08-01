<template>
  <div class="max-w-3xl mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Tu carrito</h1>
    <div v-if="carrito.items.length === 0">El carrito está vacío.</div>
    <div v-else class="space-y-4">
      <div v-for="item in carrito.items" :key="item.id" class="flex justify-between items-center border p-2 rounded">
        <div>
          <p class="font-semibold">{{ item.producto.nombre }}</p>
          <p>Cantidad: {{ item.cantidad }}</p>
        </div>
        <div class="space-x-2">
          <button @click="cambiar(item, item.cantidad - 1)" class="px-2 py-1 bg-gray-200 rounded">-</button>
          <button @click="cambiar(item, item.cantidad + 1)" class="px-2 py-1 bg-gray-200 rounded">+</button>
          <button @click="carrito.eliminar(item.id)" class="px-2 py-1 bg-red-500 text-white rounded">x</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCarritoStore } from '../stores/carrito'

defineOptions({ name: 'CarritoView' })
const carrito = useCarritoStore()

onMounted(() => {
  carrito.cargar()
})

const cambiar = (item, cantidad) => {
  if (cantidad <= 0) {
    carrito.eliminar(item.id)
  } else {
    carrito.actualizar(item.id, cantidad)
  }
}
</script>