<template>
  <main class="bg-slate-50 dark:bg-slate-900 min-h-screen px-4 py-10">
    <div class="mx-auto max-w-lg space-y-6">

      <div class="rounded-2xl border border-rose-100 dark:border-rose-900 bg-white dark:bg-slate-800 p-8 text-center shadow-sm space-y-4">
        <!-- Ícono -->
        <div class="inline-flex h-14 w-14 items-center justify-center rounded-full bg-rose-100 dark:bg-rose-900/40 mx-auto">
          <svg class="w-7 h-7 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </div>

        <!-- Título -->
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">Pedido cancelado</h1>
        <p class="text-slate-500 dark:text-slate-400">
          El pago no se completó y tu pedido
          <span v-if="pedidoId" class="font-semibold text-slate-700 dark:text-slate-300">#{{ pedidoId }}</span>
          ha sido cancelado automáticamente.
        </p>

        <!-- Estado de cancelación -->
        <div v-if="cancelando" class="flex items-center justify-center gap-2 text-sm text-slate-500 dark:text-slate-400">
          <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          Cancelando pedido…
        </div>
        <div v-else-if="cancelado" class="inline-flex items-center gap-1.5 rounded-full bg-rose-50 dark:bg-rose-900/30 border border-rose-200 dark:border-rose-800 px-3 py-1 text-sm text-rose-700 dark:text-rose-400">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
          Pedido cancelado correctamente
        </div>

        <p class="text-sm text-slate-400 dark:text-slate-500">
          No se realizó ningún cobro. Puedes intentarlo de nuevo cuando quieras.
        </p>
      </div>

      <!-- Acciones -->
      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <button
          type="button"
          @click="router.push({ name: 'checkout' })"
          class="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-white font-semibold text-sm shadow-sm transition-colors"
        >
          Intentar de nuevo
        </button>
        <button
          type="button"
          @click="router.push({ name: 'home' })"
          class="px-6 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 font-medium text-sm transition-colors"
        >
          Volver al inicio
        </button>
      </div>

    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cancelarPedidoMP } from '@/services/pedidos'

const route = useRoute()
const router = useRouter()

const pedidoId = ref(route.query.pedido || null)
const cancelando = ref(false)
const cancelado = ref(false)

onMounted(async () => {
  if (!pedidoId.value) return
  cancelando.value = true
  try {
    await cancelarPedidoMP(pedidoId.value)
    cancelado.value = true
  } catch {
    // Si ya estaba cancelado o no existe, no pasa nada
    cancelado.value = true
  } finally {
    cancelando.value = false
  }
})
</script>
