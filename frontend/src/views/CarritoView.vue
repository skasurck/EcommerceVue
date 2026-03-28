<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950">
    <div class="mx-auto max-w-5xl px-4 py-8">
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-6">Tu carrito</h1>

      <!-- Timer reserva -->
      <div v-if="carrito.reservaExpira" class="mb-5 flex items-center gap-3 rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/30 px-4 py-3">
        <svg class="h-5 w-5 shrink-0 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p class="text-sm text-amber-800 dark:text-amber-300">
          Reservado temporalmente · Tiempo restante:
          <span class="font-bold font-mono">{{ minutos }}:{{ segundos }}</span>
        </p>
      </div>

      <!-- Vacío -->
      <div v-if="carrito.items.length === 0" class="flex flex-col items-center justify-center py-24 text-center">
        <div class="mb-5 flex h-20 w-20 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
          <svg class="h-10 w-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 00-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 00-16.536-1.84M7.5 14.25L5.106 5.272M6 20.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm12.75 0a.75.75 0 11-1.5 0 .75.75 0 011.5 0z"/>
          </svg>
        </div>
        <p class="text-lg font-semibold text-slate-700 dark:text-slate-300">Tu carrito está vacío</p>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Agrega productos para comenzar tu compra.</p>
        <RouterLink to="/productos" class="mt-6 inline-flex items-center gap-2 rounded-full bg-slate-900 dark:bg-cyan-500 px-6 py-2.5 text-sm font-semibold text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-cyan-400 transition-colors">
          Ver productos
        </RouterLink>
      </div>

      <!-- Con items -->
      <div v-else class="grid grid-cols-1 gap-6 lg:grid-cols-3">

        <!-- Lista de productos -->
        <div class="lg:col-span-2 space-y-3">
          <div
            v-for="item in carrito.items"
            :key="item.id"
            class="flex gap-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 p-3 sm:p-4 shadow-sm"
          >
            <!-- Imagen -->
            <RouterLink :to="{ name: 'producto', params: { id: item.producto?.id } }" class="shrink-0">
              <img
                :src="item.producto?.miniatura_url || item.producto?.imagen_principal || ''"
                :alt="item.producto?.nombre"
                class="h-20 w-20 sm:h-24 sm:w-24 rounded-xl object-cover bg-slate-100 dark:bg-slate-800"
              />
            </RouterLink>

            <!-- Info -->
            <div class="flex flex-1 flex-col min-w-0 gap-2">
              <!-- Nombre + badge + delete -->
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                  <RouterLink :to="{ name: 'producto', params: { id: item.producto?.id } }">
                    <p class="text-sm font-semibold text-slate-800 dark:text-slate-100 line-clamp-2 leading-snug hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">
                      {{ item.producto?.nombre }}
                    </p>
                  </RouterLink>
                  <span v-if="item.producto?.stock <= 0" class="mt-1 inline-flex items-center rounded-full bg-red-50 dark:bg-red-500/10 px-2 py-0.5 text-xs font-medium text-red-600 dark:text-red-400">
                    Agotado
                  </span>
                </div>
                <button
                  @click="carrito.eliminar(item.id)"
                  class="shrink-0 rounded-lg p-1.5 text-slate-300 dark:text-slate-600 hover:bg-red-50 dark:hover:bg-red-500/10 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                  aria-label="Eliminar"
                >
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/>
                  </svg>
                </button>
              </div>

              <!-- Precio + controles cantidad -->
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs text-slate-400 dark:text-slate-500">Precio unitario</p>
                  <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ formatMoney(precioUnitario(item)) }}</p>
                </div>

                <!-- Qty controls -->
                <div class="flex items-center gap-1 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 p-0.5">
                  <button
                    @click="cambiar(item, item.cantidad - 1)"
                    class="flex h-8 w-8 items-center justify-center rounded-lg text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white transition-colors font-bold"
                    :disabled="item.producto?.stock <= 0"
                  >
                    <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14"/></svg>
                  </button>
                  <span class="min-w-[2rem] text-center text-sm font-semibold text-slate-900 dark:text-white">{{ item.cantidad }}</span>
                  <button
                    @click="cambiar(item, item.cantidad + 1)"
                    class="flex h-8 w-8 items-center justify-center rounded-lg text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white transition-colors font-bold"
                    :disabled="item.producto?.stock <= 0"
                  >
                    <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/></svg>
                  </button>
                </div>
              </div>

              <!-- Subtotal item -->
              <div class="flex justify-end">
                <p class="text-xs text-slate-500 dark:text-slate-400">
                  Subtotal: <span class="font-semibold text-slate-800 dark:text-slate-200">{{ formatMoney(subtotalItem(item)) }}</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Resumen -->
        <div class="lg:col-span-1">
          <div class="sticky top-24 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 shadow-sm p-5 space-y-4">
            <h2 class="font-semibold text-slate-900 dark:text-white text-base">Resumen del pedido</h2>

            <div class="space-y-2 text-sm">
              <div class="flex justify-between text-slate-600 dark:text-slate-400">
                <span>Subtotal ({{ carrito.totalCantidad }} art.)</span>
                <span>{{ formatMoney(totalCarrito) }}</span>
              </div>
              <div class="flex justify-between text-slate-600 dark:text-slate-400">
                <span>Envío estimado</span>
                <span>{{ formatMoney(COSTO_ENVIO) }}</span>
              </div>
              <div class="border-t border-slate-100 dark:border-slate-800 pt-2 flex justify-between font-bold text-slate-900 dark:text-white text-base">
                <span>Total</span>
                <span>{{ formatMoney(totalConEnvio) }}</span>
              </div>
            </div>

            <button
              class="w-full rounded-xl bg-slate-900 dark:bg-cyan-500 py-3 text-sm font-semibold text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-cyan-400 transition-colors shadow-sm"
              @click="finalizarCompra"
            >
              Finalizar compra
            </button>

            <RouterLink to="/productos" class="flex items-center justify-center gap-1.5 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"/></svg>
              Seguir comprando
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, ref, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCarritoStore } from '@/stores/carrito'

defineOptions({ name: 'CarritoView' })
const router = useRouter()
const carrito = useCarritoStore()

const curr = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' })
const formatMoney = (v) => curr.format(Number(v || 0))

const tiempoRestante = ref(0)
let timer

const actualizarTiempo = () => {
  if (!carrito.reservaExpira) return
  const diff = new Date(carrito.reservaExpira) - Date.now()
  if (diff <= 0) {
    tiempoRestante.value = 0
    clearInterval(timer)
    carrito.cargar()
  } else {
    tiempoRestante.value = Math.floor(diff / 1000)
  }
}

onMounted(async () => {
  await carrito.cargar()
  if (carrito.reservaExpira) {
    actualizarTiempo()
    timer = setInterval(actualizarTiempo, 1000)
  }
})

watch(() => carrito.reservaExpira, () => {
  clearInterval(timer)
  if (carrito.reservaExpira) {
    actualizarTiempo()
    timer = setInterval(actualizarTiempo, 1000)
  }
})

onUnmounted(() => clearInterval(timer))

const minutos  = computed(() => Math.floor(tiempoRestante.value / 60))
const segundos = computed(() => ('0' + (tiempoRestante.value % 60)).slice(-2))

const COSTO_ENVIO = 79

const precioUnitario = (item) => {
  const p = item?.producto
  if (!p) return 0
  let precio = +(p.precio_rebajado ?? p.precio_normal ?? 0)
  const tiers = Array.isArray(p.precios_escalonados) ? p.precios_escalonados : []
  for (const tier of tiers) {
    const pu = Number(tier?.precio_unitario ?? NaN)
    if (item.cantidad >= Number(tier?.cantidad_minima ?? 0) && !Number.isNaN(pu) && pu < precio) precio = pu
  }
  return precio
}

const subtotalItem  = (item) => precioUnitario(item) * item.cantidad
const totalCarrito  = computed(() => carrito.items.reduce((s, i) => s + subtotalItem(i), 0))
const totalConEnvio = computed(() => totalCarrito.value + COSTO_ENVIO)

const cambiar = (item, cantidad) => {
  const max = item.cantidad + item.producto.stock
  if (cantidad <= 0) {
    carrito.eliminar(item.id)
  } else if (cantidad <= max) {
    carrito.actualizar(item.id, cantidad)
  }
}

const finalizarCompra = () => router.push('/checkout')
</script>
