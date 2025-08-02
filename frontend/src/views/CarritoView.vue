<template>
  <div class="max-w-3xl mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Tu carrito</h1>
    <div v-if="carrito.items.length === 0">El carrito está vacío.</div>
    <div v-else class="space-y-4">
       <div
        v-for="item in carrito.items"
        :key="item.id"
        class="flex items-center justify-between border p-2 rounded"
      >
        <img
          v-if="item.producto.miniatura_url || item.producto.imagen_principal"
          :src="item.producto.miniatura_url || item.producto.imagen_principal"
          class="w-16 h-16 object-cover rounded mr-4"
          alt="Miniatura"
        />
        <div class="flex-1">
          <p class="font-semibold">{{ item.producto.nombre }}</p>
          <p class="text-sm">Cantidad: {{ item.cantidad }}</p>
          <p class="text-sm">Precio unitario: ${{ precioUnitario(item).toFixed(2) }}</p>
          <p class="font-semibold">Subtotal: ${{ subtotalItem(item).toFixed(2) }}</p>
        </div>
        <div class="flex items-center space-x-2">
          <button @click="cambiar(item, item.cantidad - 1)" class="px-2 py-1 bg-gray-200 rounded">
            -
          </button>
          <button @click="cambiar(item, item.cantidad + 1)" class="px-2 py-1 bg-gray-200 rounded">
            +
          </button>
          <button @click="carrito.eliminar(item.id)" class="text-red-500 hover:text-red-700">
            <IconTrash class="w-5 h-5" />
          </button>
        </div>
      </div>
      <div class="p-4 border rounded bg-gray-50 space-y-1">
        <h2 class="font-semibold mb-2">Resumen del carrito</h2>
        <div class="flex justify-between">
          <span>Subtotal</span>
          <span>${{ totalCarrito.toFixed(2) }}</span>
        </div>
        <div class="flex justify-between">
          <span>Envío</span>
          <span>${{ COSTO_ENVIO.toFixed(2) }}</span>
        </div>
        <div class="flex justify-between font-bold">
          <span>Total</span>
          <span>${{ totalConEnvio.toFixed(2) }}</span>
        </div>
        <button
          class="mt-3 w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded"
          @click="finalizarCompra"
        >
          Finalizar compra
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCarritoStore } from '../stores/carrito'
import IconTrash from '../components/icons/IconTrash.vue'

defineOptions({ name: 'CarritoView' })
const router = useRouter()
const carrito = useCarritoStore()

onMounted(() => {
  carrito.cargar()
})
const COSTO_ENVIO = 79

const precioUnitario = (item) => {
  if (!item.producto) return 0
  let precio = +(item.producto.precio_rebajado ?? item.producto.precio_normal)
  const tiers = item.producto.precios_escalonados || []
  for (const tier of tiers) {
    if (item.cantidad >= tier.cantidad_minima) {
      const p = +tier.precio_unitario
      if (p < precio) precio = p
    }
  }
  return precio
}

const subtotalItem = (item) => precioUnitario(item) * item.cantidad

const totalCarrito = computed(() => carrito.items.reduce((sum, i) => sum + subtotalItem(i), 0))

const totalConEnvio = computed(() => totalCarrito.value + COSTO_ENVIO)

const cambiar = (item, cantidad) => {
  if (cantidad <= 0) {
    carrito.eliminar(item.id)
  } else {
    carrito.actualizar(item.id, cantidad)
  }
}
const finalizarCompra = () => {
  router.push('/checkout')
}
</script>