<template>
  <div class="max-w-6xl mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-4">Mis pedidos</h1>

    <div v-if="detalle" class="mb-4 border rounded p-4 bg-white">
      <h3 class="font-semibold mb-2">Pedido #{{ detalle.id }}</h3>
      <p class="mb-2">Total: {{ detalle.total }} — Estado: {{ detalle.estado }}</p>
      <div class="grid sm:grid-cols-2 gap-4 text-sm">
        <div>
          <h4 class="font-medium">Productos</h4>
          <ul class="list-disc ml-5">
            <li v-for="it in detalle.detalles" :key="it.producto">
              {{ it.producto_nombre }} — {{ it.cantidad }} × {{ it.precio_unitario }} = {{ it.subtotal }}
            </li>
          </ul>
        </div>
        <div>
          <h4 class="font-medium">Envío</h4>
          <p>{{ detalle.direccion.calle }} {{ detalle.direccion.numero_exterior }}, {{ detalle.direccion.ciudad }}</p>
          <h4 class="mt-2 font-medium">Pago</h4>
          <p>{{ detalle.metodo_pago_display }}</p>
        </div>
      </div>
    </div>

    <ul class="space-y-2">
      <li v-for="p in pedidos" :key="p.id" class="flex items-center justify-between border p-3 rounded bg-white">
        <div>
          <div>Pedido #{{ p.id }} · <span class="text-gray-600">Estado:</span> {{ p.estado }}</div>
          <div class="text-sm text-gray-600">Total: {{ p.total }}</div>
        </div>
        <button class="text-blue-700 hover:underline" @click="ver(p.id)">Ver detalle</button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { obtenerPedidos, obtenerPedido } from '@/services/account'

const pedidos = ref([])
const detalle = ref(null)

const ver = async (id) => {
  const r = await obtenerPedido(id)
  detalle.value = r.data
  // opcional: window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(async () => {
  const r = await obtenerPedidos()
  pedidos.value = r.data
})
</script>
