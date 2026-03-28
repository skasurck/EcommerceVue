<template>
  <div class="space-y-6">

    <!-- Método de pago -->
    <div>
      <h3 class="text-base font-semibold text-slate-800 dark:text-slate-100 mb-3">Método de pago</h3>
      <div class="grid gap-3">

        <!-- Mercado Pago -->
        <label
          class="relative flex items-start gap-4 p-4 rounded-xl border-2 cursor-pointer transition-colors"
          :class="metodoPago === 'mercadopago'
            ? 'border-cyan-500 bg-cyan-50 dark:bg-cyan-900/20'
            : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'">
          <input type="radio" value="mercadopago" v-model="metodoPago" class="sr-only" />
          <div class="shrink-0 w-10 h-10 rounded-lg bg-[#009ee3] flex items-center justify-center">
            <svg viewBox="0 0 48 48" class="w-6 h-6 fill-white" xmlns="http://www.w3.org/2000/svg">
              <path d="M24 4C12.95 4 4 12.95 4 24s8.95 20 20 20 20-8.95 20-20S35.05 4 24 4zm0 6c7.73 0 14 6.27 14 14 0 2.35-.58 4.56-1.62 6.5L13.5 11.62C15.44 10.58 17.65 10 20 10h4zm0 28c-7.73 0-14-6.27-14-14 0-2.35.58-4.56 1.62-6.5l22.88 22.88A13.94 13.94 0 0 1 28 38h-4z"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-slate-800 dark:text-slate-100">Mercado Pago</p>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Tarjeta, OXXO, transferencia y más. Pago 100% seguro.</p>
          </div>
          <div v-if="metodoPago === 'mercadopago'" class="shrink-0 w-5 h-5 rounded-full bg-cyan-500 flex items-center justify-center">
            <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
        </label>

        <!-- Transferencia -->
        <label
          class="relative flex items-start gap-4 p-4 rounded-xl border-2 cursor-pointer transition-colors"
          :class="metodoPago === 'transferencia'
            ? 'border-cyan-500 bg-cyan-50 dark:bg-cyan-900/20'
            : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'">
          <input type="radio" value="transferencia" v-model="metodoPago" class="sr-only" />
          <div class="shrink-0 w-10 h-10 rounded-lg bg-emerald-500 flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-slate-800 dark:text-slate-100">Transferencia bancaria</p>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Envía el pago directamente a nuestra cuenta.</p>
          </div>
          <div v-if="metodoPago === 'transferencia'" class="shrink-0 w-5 h-5 rounded-full bg-cyan-500 flex items-center justify-center">
            <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
        </label>

        <!-- Datos de transferencia (dinámicos desde el admin) -->
        <div v-if="metodoPago === 'transferencia'" class="rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 p-4 text-sm space-y-1.5">
          <p class="font-semibold text-slate-700 dark:text-slate-300 mb-2">Datos para transferencia</p>
          <template v-if="datosBanco">
            <div v-if="datosBanco.banco" class="flex justify-between">
              <span class="text-slate-500 dark:text-slate-400">Banco</span>
              <span class="font-medium text-slate-800 dark:text-slate-100">{{ datosBanco.banco }}</span>
            </div>
            <div v-if="datosBanco.clabe" class="flex justify-between">
              <span class="text-slate-500 dark:text-slate-400">CLABE</span>
              <span class="font-mono font-medium text-slate-800 dark:text-slate-100">{{ datosBanco.clabe }}</span>
            </div>
            <div v-if="datosBanco.numero_cuenta" class="flex justify-between">
              <span class="text-slate-500 dark:text-slate-400">Núm. cuenta</span>
              <span class="font-mono font-medium text-slate-800 dark:text-slate-100">{{ datosBanco.numero_cuenta }}</span>
            </div>
            <div v-if="datosBanco.beneficiario" class="flex justify-between">
              <span class="text-slate-500 dark:text-slate-400">Beneficiario</span>
              <span class="font-medium text-slate-800 dark:text-slate-100">{{ datosBanco.beneficiario }}</span>
            </div>
            <p v-if="datosBanco.instrucciones" class="text-xs text-amber-600 dark:text-amber-400 pt-1 border-t border-slate-200 dark:border-slate-700 mt-1">
              {{ datosBanco.instrucciones }}
            </p>
          </template>
          <p v-else class="text-slate-400 dark:text-slate-500 text-xs">Cargando datos bancarios…</p>
        </div>

      </div>
    </div>

    <!-- Estado: preparando pago -->
    <div v-if="metodoPago === 'mercadopago' && creatingPreference" class="rounded-xl border border-cyan-200 dark:border-cyan-800 bg-cyan-50 dark:bg-cyan-900/20 p-4 flex items-center gap-3">
      <svg class="w-5 h-5 animate-spin text-cyan-500 shrink-0" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
      <span class="text-sm text-cyan-700 dark:text-cyan-300">Preparando tu pago seguro, serás redirigido en un momento…</span>
    </div>

    <!-- Resumen del pedido -->
    <div class="rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="px-4 py-3 bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700">
        <p class="font-semibold text-sm text-slate-700 dark:text-slate-300">Resumen del pedido</p>
      </div>
      <div class="divide-y divide-slate-100 dark:divide-slate-800">
        <div v-for="item in carrito.items" :key="item.id" class="flex items-center gap-3 px-4 py-3">
          <img
            v-if="item.producto?.miniatura || item.producto?.imagen_principal"
            :src="item.producto.miniatura || item.producto.imagen_principal"
            :alt="item.producto.nombre"
            class="h-12 w-12 rounded-lg object-cover shrink-0 bg-slate-100 dark:bg-slate-800"
          />
          <div class="w-12 h-12 rounded-lg bg-slate-100 dark:bg-slate-800 shrink-0 flex items-center justify-center" v-else>
            <svg class="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 00-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 00-16.536-1.84M7.5 14.25L5.106 5.272M6 20.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm12.75 0a.75.75 0 11-1.5 0 .75.75 0 011.5 0z" /></svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">{{ item.producto?.nombre }}</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">Cant. {{ item.cantidad }}</p>
          </div>
          <p class="text-sm font-semibold text-slate-800 dark:text-slate-100 shrink-0">
            {{ fmt((Number(item.producto?.precio_rebajado ?? item.producto?.precio_normal ?? 0) * item.cantidad)) }}
          </p>
        </div>
      </div>

      <!-- Totales -->
      <div class="px-4 py-3 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-700 space-y-1.5 text-sm">
        <div class="flex justify-between text-slate-600 dark:text-slate-400">
          <span>Subtotal</span>
          <span>{{ fmt(subtotal) }}</span>
        </div>
        <div v-if="store.descuento > 0" class="flex justify-between text-emerald-600 dark:text-emerald-400">
          <span>Descuento <span class="font-mono text-xs">({{ store.cupon?.codigo }})</span></span>
          <span>-{{ fmt(store.descuento) }}</span>
        </div>
        <div class="flex justify-between text-slate-600 dark:text-slate-400">
          <span>Envío</span>
          <span>{{ envio > 0 ? fmt(envio) : 'Gratis' }}</span>
        </div>
        <div class="flex justify-between font-bold text-base text-slate-900 dark:text-slate-50 pt-1 border-t border-slate-200 dark:border-slate-700">
          <span>Total</span>
          <span>{{ fmt(total) }}</span>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="rounded-lg bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800 p-3 flex items-start gap-2">
      <svg class="w-4 h-4 text-rose-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/>
      </svg>
      <p class="text-sm text-rose-600 dark:text-rose-400">{{ error }}</p>
    </div>

    <!-- Acciones -->
    <div class="flex gap-3 pt-1">
      <button
        type="button"
        @click="emit('back')"
        class="flex items-center gap-1.5 px-5 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"/>
        </svg>
        Atrás
      </button>
      <button
        type="button"
        @click="finalizar"
        :disabled="disableFinalizeButton"
        class="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold transition-colors"
        :class="disableFinalizeButton
          ? 'bg-slate-200 dark:bg-slate-700 text-slate-400 dark:text-slate-500 cursor-not-allowed'
          : 'bg-cyan-500 hover:bg-cyan-400 text-white shadow-sm'"
      >
        <svg v-if="creatingPreference" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
        </svg>
        {{ finalizarLabel }}
        <svg v-if="!creatingPreference" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/>
        </svg>
      </button>
    </div>

  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCheckoutStore } from '@/stores/checkout'
import { useCarritoStore } from '@/stores/carrito'
import { crearPedido } from '@/services/checkout'
import { createMercadoPagoPreference } from '@/services/pagos'
import axios from '@/axios'

const emit = defineEmits(['back', 'complete'])
const router = useRouter()
const store = useCheckoutStore()
const carrito = useCarritoStore()
const auth = useAuthStore()
const metodoPago = ref(store.metodoPago || 'mercadopago')
const error = ref('')
const creatingPreference = ref(false)

// Datos bancarios dinámicos
const datosBanco = ref(null)
onMounted(async () => {
  try {
    const { data } = await axios.get('/pagos/transferencia/config/')
    datosBanco.value = data
  } catch { /* silencioso */ }
})

const fmt = (n) => Number(n).toLocaleString('es-MX', { style: 'currency', currency: 'MXN' })

const buildItemsSnapshot = () => {
  if (!Array.isArray(carrito.items)) return []
  return carrito.items.map((item) => {
    const product = item.producto || {}
    const price = Number(product.precio_rebajado ?? product.precio_normal ?? product.precio ?? 0) || carrito.precioUnitario?.(item) || 0
    return {
      id: product.id ?? item.id,
      sku: product.sku ?? null,
      name: product.nombre ?? product.name ?? `Producto ${product.id ?? item.id}`,
      image: product.miniatura ?? product.imagen_principal ?? null,
      quantity: Number(item.cantidad ?? 0),
      price,
      producto: item.producto,
    }
  })
}


const finalizar = async () => {
  store.metodoPago = metodoPago.value
  error.value = ''

  const { save, ...direccion } = store.direccion || {}
  const saveAddress = auth.isAuthenticated && save

  if (metodoPago.value === 'mercadopago') {
    try {
      creatingPreference.value = true
      const pedidoRes = await crearPedido({
        direccion,
        metodo_envio: store.metodoEnvio?.id,
        metodo_pago: 'mercadopago',
        indicaciones: store.indicaciones,
        save_address: saveAddress,
        ...(store.cupon ? { cupon_codigo: store.cupon.codigo } : {}),
      })
      const pedidoId = pedidoRes.data.id
      const origin = window.location?.origin || 'https://mktska.net'
      const prefRes = await createMercadoPagoPreference({
        items: carrito.items,
        external_reference: pedidoId,
        back_urls: {
          success: `${origin}/gracias`,
          failure: `${origin}/pedido-cancelado?pedido=${pedidoId}`,
          pending: `${origin}/checkout?status=pending`,
        },
        success_url: `${origin}/gracias`,
        failure_url: `${origin}/pedido-cancelado?pedido=${pedidoId}`,
        pending_url: `${origin}/checkout?status=pending`,
      })
      const { init_point } = prefRes.data || {}
      if (init_point) {
        window.location.href = init_point
        return
      }
      throw new Error('Mercado Pago no devolvió la URL de pago')
    } catch (e) {
      console.error(e)
      error.value = e.response?.data?.error || e.response?.data?.detail || e.message || 'No se pudo procesar el pago'
      creatingPreference.value = false
    }
    return
  }

  // Transferencia / Tarjeta
  const snapshotItems = buildItemsSnapshot()
  const fallbackShipping = Number(store.metodoEnvio?.costo ?? 0)
  const fallbackSubtotal = Number(carrito.subtotal)
  const fallbackDescuento = Number(store.descuento ?? 0)
  const fallbackTotal = fallbackSubtotal - fallbackDescuento + fallbackShipping
  try {
    const response = await crearPedido({
      direccion,
      metodo_envio: store.metodoEnvio?.id,
      metodo_pago: store.metodoPago,
      indicaciones: store.indicaciones,
      save_address: saveAddress,
      ...(store.cupon ? { cupon_codigo: store.cupon.codigo } : {}),
    })
    const pedido = response?.data || {}
    const resumen = {
      id: pedido.id ?? null,
      folio: pedido.numero ?? pedido.folio ?? null,
      total: Number(pedido.total ?? fallbackTotal),
      subtotal: Number(pedido.subtotal ?? fallbackSubtotal),
      descuento: Number(pedido.descuento ?? fallbackDescuento),
      cuponCodigo: store.cupon?.codigo ?? null,
      shipping: Number(pedido.costo_envio ?? fallbackShipping),
      tax: Number(pedido.impuestos ?? 0),
      currency: pedido.moneda ?? 'MXN',
      paymentMethod: store.metodoPago,
      items: Array.isArray(pedido.detalles) && pedido.detalles.length
        ? pedido.detalles.map((item) => ({
            id: item.producto,
            sku: item.producto_sku ?? null,
            name: item.producto_nombre ?? 'Producto',
            image: item.producto_imagen ?? null,
            price: Number(item.precio_unitario ?? 0),
            quantity: Number(item.cantidad ?? 0),
          }))
        : snapshotItems,
    }
    await carrito.cargar()
    const payload = { ...resumen, timestamp: Date.now() }
    try { sessionStorage.setItem('lastOrderSummary', JSON.stringify(payload)) } catch { /* silencioso */ }
    emit('complete', resumen)
    store.reset()
    await router.push({ name: 'gracias', query: payload.id ? { pedido: payload.id } : {} })
  } catch (e) {
    console.error(e)
    error.value = e.response?.data?.detail || 'No se pudo crear el pedido'
  }
}

const subtotal = computed(() => Number(carrito.subtotal))
const envio = computed(() => Number(store.metodoEnvio?.costo ?? 0))
const total = computed(() => subtotal.value - store.descuento + envio.value)

const disableFinalizeButton = computed(() => creatingPreference.value)

const finalizarLabel = computed(() => {
  if (creatingPreference.value) return 'Procesando...'
  if (metodoPago.value === 'mercadopago') return 'Ir a Mercado Pago →'
  return 'Confirmar pedido'
})

watch(() => metodoPago.value, (nuevo) => {
  store.metodoPago = nuevo
  if (nuevo !== 'mercadopago') error.value = ''
})
</script>
