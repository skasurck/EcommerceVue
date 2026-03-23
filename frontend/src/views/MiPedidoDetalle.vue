<template>
  <div class="max-w-3xl mx-auto px-4 py-6">
    <router-link to="/mis-pedidos" class="text-sm text-blue-700 hover:underline">&larr; Mis pedidos</router-link>

    <p v-if="cargando" class="mt-6 text-gray-600">Cargando pedido…</p>
    <p v-else-if="errorMsg" class="mt-6 text-red-700">{{ errorMsg }}</p>

    <template v-else-if="pedido">
      <div class="mt-4 flex items-center justify-between">
        <h1 class="text-2xl font-bold">Pedido #{{ pedido.id }}</h1>
        <span class="rounded-full px-3 py-1 text-sm font-medium" :class="estadoClase">
          {{ pedido.estado }}
        </span>
      </div>

      <div class="mt-6 grid sm:grid-cols-2 gap-4">
        <!-- Artículos -->
        <div class="sm:col-span-2 bg-white border rounded-lg p-4">
          <h2 class="font-semibold mb-3">Artículos</h2>
          <ul class="divide-y">
            <li
              v-for="(it, i) in pedido.detalles ?? []"
              :key="it.producto ?? `det-${i}`"
              class="py-3 flex items-center gap-3 text-sm"
            >
              <img
                v-if="it.producto_imagen"
                :src="it.producto_imagen"
                :alt="it.producto_nombre"
                class="h-14 w-14 rounded object-cover shrink-0 border"
              />
              <div v-else class="h-14 w-14 rounded border bg-slate-100 shrink-0" />
              <div class="flex-1 min-w-0">
                <p class="font-medium text-slate-900 leading-snug">{{ it.producto_nombre ?? '—' }}</p>
                <p class="text-slate-500 text-xs mt-0.5">SKU: {{ it.producto_sku ?? 'N/D' }} · Cant. {{ it.cantidad }}</p>
              </div>
              <p class="font-semibold shrink-0">${{ Number(it.subtotal).toFixed(2) }}</p>
            </li>
          </ul>
          <div class="mt-3 border-t pt-3 space-y-1 text-sm">
            <div class="flex justify-between text-gray-600">
              <span>Subtotal</span><span>${{ Number(pedido.subtotal).toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-gray-600">
              <span>Envío</span><span>${{ Number(pedido.costo_envio).toFixed(2) }}</span>
            </div>
            <div class="flex justify-between font-bold text-base">
              <span>Total</span><span>${{ Number(pedido.total).toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <!-- Dirección -->
        <div class="bg-white border rounded-lg p-4">
          <h2 class="font-semibold mb-2">Dirección de envío</h2>
          <p class="text-sm text-gray-700">
            {{ pedido.direccion?.nombre }} {{ pedido.direccion?.apellidos }}<br />
            {{ pedido.direccion?.calle }} {{ pedido.direccion?.numero_exterior }}<br />
            {{ pedido.direccion?.colonia }}, {{ pedido.direccion?.ciudad }}<br />
            {{ pedido.direccion?.estado }}, {{ pedido.direccion?.codigo_postal }}
          </p>
        </div>

        <!-- Pago -->
        <div class="bg-white border rounded-lg p-4">
          <h2 class="font-semibold mb-2">Método de pago</h2>
          <p class="text-sm text-gray-700">{{ pedido.metodo_pago_display ?? '—' }}</p>
          <h2 class="font-semibold mt-4 mb-2">Fecha del pedido</h2>
          <p class="text-sm text-gray-700">{{ fechaFormateada }}</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { obtenerPedido } from '@/services/account'

const route = useRoute()
const pedido = ref(null)
const cargando = ref(false)
const errorMsg = ref('')

const estadoClase = computed(() => {
  const mapa = {
    pendiente:  'bg-yellow-100 text-yellow-800',
    pagado:     'bg-blue-100 text-blue-800',
    confirmado: 'bg-blue-100 text-blue-800',
    enviado:    'bg-purple-100 text-purple-800',
    entregado:  'bg-green-100 text-green-800',
    cancelado:  'bg-red-100 text-red-800',
  }
  return mapa[pedido.value?.estado] ?? 'bg-gray-100 text-gray-700'
})

const fechaFormateada = computed(() => {
  if (!pedido.value?.creado) return '—'
  return new Date(pedido.value.creado).toLocaleDateString('es-MX', {
    year: 'numeric', month: 'long', day: 'numeric',
  })
})

onMounted(async () => {
  cargando.value = true
  try {
    const { data } = await obtenerPedido(route.params.id)
    pedido.value = data
  } catch (e) {
    const code = e?.response?.status
    errorMsg.value = code === 404 ? 'Pedido no encontrado.' : 'No se pudo cargar el pedido.'
  } finally {
    cargando.value = false
  }
})
</script>
