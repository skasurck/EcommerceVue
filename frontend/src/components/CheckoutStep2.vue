<template>
  <div class="space-y-5">

    <!-- Métodos de envío -->
    <div>
      <h3 class="text-base font-semibold text-slate-800 dark:text-slate-100 mb-3">Método de envío</h3>

      <div v-if="metodos.length" class="grid gap-3">
        <label
          v-for="m in metodos"
          :key="m.id"
          class="flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-colors"
          :class="metodo?.id === m.id
            ? 'border-cyan-500 bg-cyan-50 dark:bg-cyan-900/20'
            : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'"
        >
          <input type="radio" :value="m" v-model="metodo" class="sr-only" />
          <div
            class="shrink-0 w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors"
            :class="metodo?.id === m.id ? 'border-cyan-500 bg-cyan-500' : 'border-slate-300 dark:border-slate-600'"
          >
            <div v-if="metodo?.id === m.id" class="w-1.5 h-1.5 rounded-full bg-white"></div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-sm text-slate-800 dark:text-slate-100">{{ m.nombre }}</p>
            <p v-if="m.descripcion" class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{{ m.descripcion }}</p>
          </div>
          <span class="shrink-0 font-semibold text-sm" :class="m.costo === 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-800 dark:text-slate-100'">
            {{ m.costo === 0 ? 'Gratis' : fmt(m.costo) }}
          </span>
        </label>
      </div>

      <div v-else class="rounded-xl border border-slate-200 dark:border-slate-700 p-6 text-center text-sm text-slate-400 dark:text-slate-500">
        No hay métodos de envío disponibles.
      </div>
    </div>

    <!-- Indicaciones del pedido -->
    <div class="space-y-1">
      <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">
        Indicaciones del pedido <span class="text-xs text-slate-400">(opcional)</span>
      </label>
      <textarea
        v-model="indicaciones"
        placeholder="Instrucciones especiales para tu pedido o entrega…"
        rows="2"
        class="w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 resize-none transition-colors"
      />
    </div>

    <!-- Cupón de descuento -->
    <CuponInput />

    <!-- Resumen de totales -->
    <div class="rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-4 text-sm space-y-1.5">
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
        <span :class="envio === 0 ? 'text-emerald-600 dark:text-emerald-400 font-medium' : ''">
          {{ envio === 0 ? 'Gratis' : fmt(envio) }}
        </span>
      </div>
      <div class="flex justify-between font-bold text-base text-slate-900 dark:text-slate-50 pt-1.5 border-t border-slate-200 dark:border-slate-700">
        <span>Total</span>
        <span>{{ fmt(total) }}</span>
      </div>
    </div>

    <!-- Botones -->
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
        @click="onSubmit"
        :disabled="!metodo"
        class="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold transition-colors shadow-sm"
        :class="metodo
          ? 'bg-cyan-500 hover:bg-cyan-400 text-white'
          : 'bg-slate-200 dark:bg-slate-700 text-slate-400 dark:text-slate-500 cursor-not-allowed'"
      >
        Continuar
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/>
        </svg>
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { obtenerMetodosEnvio } from '@/services/checkout'
import { useCheckoutStore } from '@/stores/checkout'
import { useCarritoStore } from '@/stores/carrito'
import CuponInput from '@/components/CuponInput.vue'

const emit = defineEmits(['next', 'back'])
const store   = useCheckoutStore()
const carrito = useCarritoStore()

const metodos     = ref([])
const metodo      = ref(store.metodoEnvio)
const indicaciones = ref(store.indicaciones)

onMounted(async () => {
  try {
    const { data } = await obtenerMetodosEnvio()
    metodos.value = Array.isArray(data) ? data : (data?.results ?? [])
    if (metodos.value.length > 0) {
      const stored = store.metodoEnvio
      metodo.value = stored
        ? (metodos.value.find(m => m.id === stored.id) ?? metodos.value[0])
        : metodos.value[0]
    }
  } catch {
    metodos.value = []
  }
})

const onSubmit = () => {
  if (!metodo.value) return
  store.metodoEnvio  = metodo.value
  store.indicaciones = indicaciones.value
  store.step = 3
  emit('next')
}

const fmt      = (n) => Number(n).toLocaleString('es-MX', { style: 'currency', currency: 'MXN' })
const subtotal = computed(() => Number(carrito.subtotal))
const envio    = computed(() => Number(metodo.value?.costo ?? 0))
const total    = computed(() => subtotal.value - store.descuento + envio.value)
</script>
