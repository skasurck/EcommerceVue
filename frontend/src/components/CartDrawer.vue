<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition name="fade">
      <div
        v-if="carrito.drawerOpen"
        class="fixed inset-0 z-40 bg-black/30 backdrop-blur-[2px]"
        @click="cerrar"
      />
    </Transition>

    <!-- Drawer -->
    <Transition name="slide-right">
      <div
        v-if="carrito.drawerOpen"
        class="fixed right-0 top-0 z-50 flex h-full w-full max-w-sm flex-col bg-white dark:bg-slate-900 shadow-2xl"
      >
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 px-5 py-4">
          <div class="flex items-center gap-2.5">
            <span class="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-500/20">
              <svg class="h-4 w-4 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
              </svg>
            </span>
            <span class="font-semibold text-slate-800 dark:text-slate-100 text-sm">Agregado al carrito</span>
          </div>
          <button
            @click="cerrar"
            class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
            aria-label="Cerrar"
          >
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Error del carrito -->
        <Transition name="fade">
          <div
            v-if="carrito.error"
            class="flex items-start gap-2 bg-rose-50 dark:bg-rose-900/20 border-b border-rose-200 dark:border-rose-800 px-5 py-3 text-sm text-rose-700 dark:text-rose-400"
          >
            <svg class="h-4 w-4 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/>
            </svg>
            <span>{{ carrito.error }}</span>
          </div>
        </Transition>

        <!-- Added product -->
        <div v-if="carrito.lastAdded" class="flex gap-4 border-b border-slate-100 dark:border-slate-800 px-5 py-4">
          <img
            :src="carrito.lastAdded.miniatura_url || carrito.lastAdded.imagen_principal || ''"
            :alt="carrito.lastAdded.nombre"
            class="h-20 w-20 shrink-0 rounded-xl object-cover bg-slate-100 dark:bg-slate-800"
          />
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-slate-800 dark:text-slate-100 line-clamp-2 break-words leading-snug">
              {{ carrito.lastAdded.nombre }}
            </p>
            <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Cantidad: {{ carrito.lastAdded.cantidadAgregada }}
            </p>
            <p class="mt-1 font-semibold text-slate-900 dark:text-white text-sm">
              {{ formatMoney(precioProducto(carrito.lastAdded)) }}
            </p>
          </div>
        </div>

        <!-- Cart summary -->
        <div class="flex-1 overflow-y-auto px-5 py-3 space-y-2">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500 mb-3">
            En tu carrito ({{ carrito.totalCantidad }} {{ carrito.totalCantidad === 1 ? 'artículo' : 'artículos' }})
          </p>
          <div
            v-for="item in otrosItems"
            :key="item.id"
            class="flex items-center gap-3"
          >
            <img
              :src="item.producto?.miniatura_url || item.producto?.imagen_principal || ''"
              :alt="item.producto?.nombre"
              class="h-12 w-12 shrink-0 rounded-lg object-cover bg-slate-100 dark:bg-slate-800"
            />
            <div class="flex-1 min-w-0">
              <p class="text-xs text-slate-700 dark:text-slate-300 line-clamp-1">{{ item.producto?.nombre }}</p>
              <p class="text-xs text-slate-400 dark:text-slate-500">×{{ item.cantidad }}</p>
            </div>
            <p class="text-xs font-medium text-slate-800 dark:text-slate-200 shrink-0">
              {{ formatMoney(precioItem(item)) }}
            </p>
          </div>
        </div>

        <!-- Footer: totals + actions -->
        <div class="border-t border-slate-100 dark:border-slate-800 px-5 py-4 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-slate-600 dark:text-slate-400">Subtotal</span>
            <span class="font-bold text-slate-900 dark:text-white">{{ formatMoney(carrito.subtotal) }}</span>
          </div>
          <RouterLink
            to="/carrito"
            @click="cerrar"
            class="flex w-full items-center justify-center gap-2 rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-transparent px-4 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-200 hover:border-slate-300 dark:hover:border-slate-600 transition-colors"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 00-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 00-16.536-1.84M7.5 14.25L5.106 5.272M6 20.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm12.75 0a.75.75 0 11-1.5 0 .75.75 0 011.5 0z"/>
            </svg>
            Ver carrito
          </RouterLink>
          <RouterLink
            to="/checkout"
            @click="cerrar"
            class="flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 dark:bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-cyan-400 transition-colors shadow-sm"
          >
            Finalizar compra
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/>
            </svg>
          </RouterLink>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useCarritoStore } from '@/stores/carrito'

const carrito = useCarritoStore()
const curr = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' })
const formatMoney = (v) => curr.format(Number(v || 0))

const precioProducto = (p) => {
  if (!p) return 0
  return +(p.precio_rebajado ?? p.precio_normal ?? 0)
}

const precioItem = (item) => {
  const p = item?.producto
  if (!p) return 0
  let precio = +(p.precio_rebajado ?? p.precio_normal ?? 0)
  const tiers = Array.isArray(p.precios_escalonados) ? p.precios_escalonados : []
  for (const tier of tiers) {
    const pu = Number(tier?.precio_unitario ?? NaN)
    if (item.cantidad >= Number(tier?.cantidad_minima ?? 0) && !Number.isNaN(pu) && pu < precio) precio = pu
  }
  return precio * item.cantidad
}

// Other cart items (not the last added)
const otrosItems = computed(() =>
  carrito.items.filter((i) => i.producto?.id !== carrito.lastAdded?.id)
)

const cerrar = () => { carrito.drawerOpen = false }

// Auto-close after 5 seconds
let timer = null
watch(() => carrito.drawerOpen, (open) => {
  clearTimeout(timer)
  if (open) {
    timer = setTimeout(cerrar, 5000)
  }
})
</script>

<style scoped>
/* Backdrop */
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Drawer slide */
.slide-right-enter-active, .slide-right-leave-active { transition: transform 0.3s cubic-bezier(0.4,0,0.2,1); }
.slide-right-enter-from, .slide-right-leave-to { transform: translateX(100%); }
</style>
