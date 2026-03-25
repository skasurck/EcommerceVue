<template>
  <div class="mt-4 border rounded p-3 bg-gray-50">
    <p class="text-sm font-medium text-gray-700 mb-2">¿Tienes un cupón de descuento?</p>

    <!-- Cupón ya aplicado -->
    <div v-if="store.cupon" class="flex items-center justify-between bg-emerald-50 border border-emerald-200 rounded px-3 py-2">
      <div>
        <span class="font-mono font-semibold text-emerald-700">{{ store.cupon.codigo }}</span>
        <span class="ml-2 text-sm text-emerald-600">
          — Descuento: -${{ Number(store.descuento).toFixed(2) }}
          <span v-if="store.cupon.descripcion" class="text-gray-500">({{ store.cupon.descripcion }})</span>
        </span>
      </div>
      <button
        type="button"
        class="ml-3 text-xs text-red-500 hover:text-red-700 underline"
        @click="quitar"
      >Quitar</button>
    </div>

    <!-- Input para ingresar código -->
    <div v-else class="flex gap-2">
      <input
        v-model="codigo"
        type="text"
        placeholder="Código de cupón"
        class="flex-1 border rounded px-3 py-1.5 text-sm uppercase tracking-wider focus:outline-none focus:ring-1 focus:ring-slate-400"
        :disabled="cargando"
        @keyup.enter="aplicar"
      />
      <button
        type="button"
        class="px-4 py-1.5 bg-slate-800 text-white text-sm rounded hover:bg-slate-700 disabled:opacity-50"
        :disabled="!codigo.trim() || cargando"
        @click="aplicar"
      >
        {{ cargando ? '...' : 'Aplicar' }}
      </button>
    </div>

    <p v-if="error" class="mt-1 text-xs text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCheckoutStore } from '@/stores/checkout'
import { useCarritoStore } from '@/stores/carrito'
import { validarCupon } from '@/services/checkout'

const store = useCheckoutStore()
const carrito = useCarritoStore()

const codigo = ref('')
const error = ref('')
const cargando = ref(false)

const aplicar = async () => {
  const cod = codigo.value.trim()
  if (!cod) return
  error.value = ''
  cargando.value = true
  try {
    const subtotal = Number(carrito.subtotal)
    const { data } = await validarCupon(cod, subtotal)
    store.aplicarCupon(data)
    codigo.value = ''
  } catch (e) {
    error.value = e.response?.data?.detail || 'Cupón inválido'
  } finally {
    cargando.value = false
  }
}

const quitar = () => {
  store.quitarCupon()
  error.value = ''
}
</script>
