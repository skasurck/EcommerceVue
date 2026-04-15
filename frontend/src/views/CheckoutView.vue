<template>
  <div class="mx-auto pt-10 px-4 transition-all duration-300" :class="showSteps ? 'max-w-xl' : 'max-w-4xl'">

    <!-- Cargando -->
    <div v-if="loading" class="flex justify-center py-20">
      <svg class="w-8 h-8 animate-spin text-cyan-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <template v-else>
      <CheckoutGuestOptions
        v-if="!showSteps"
        @guest="startGuestCheckout"
        @logged-in="handleLoggedIn"
      />

      <div v-else class="space-y-6">
        <h1 class="text-2xl font-semibold text-gray-900 dark:text-slate-100 text-center">Finaliza tu compra</h1>

        <!-- Mensaje de retorno MP -->
        <div v-if="mpStatusMessage" class="rounded-lg border p-3 text-sm flex items-start gap-2"
          :class="mpStatus === 'failure'
            ? 'bg-rose-50 dark:bg-rose-900/20 border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-400'
            : 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400'">
          <svg class="w-4 h-4 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/>
          </svg>
          {{ mpStatusMessage }}
        </div>

        <!-- Stepper -->
        <nav
          v-if="hasItems"
          class="flex items-center justify-center gap-0"
          aria-label="Pasos del proceso de compra"
        >
          <template v-for="(label, i) in ['Dirección', 'Envío', 'Pago']" :key="i">
            <div
              class="flex flex-col items-center"
              :aria-current="store.step === i + 1 ? 'step' : undefined"
            >
              <div
                class="flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold transition-colors"
                :class="store.step === i + 1
                  ? 'bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900'
                  : store.step > i + 1
                    ? 'bg-emerald-500 text-white'
                    : 'bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400'"
                :aria-label="store.step > i + 1 ? `${label} completado` : `Paso ${i + 1}: ${label}`"
              >
                <span v-if="store.step > i + 1" aria-hidden="true">✓</span>
                <span v-else aria-hidden="true">{{ i + 1 }}</span>
              </div>
              <span
                class="mt-1 text-xs"
                :class="store.step === i + 1 ? 'font-semibold text-slate-900 dark:text-slate-100' : 'text-slate-400'"
                aria-hidden="true"
              >{{ label }}</span>
            </div>
            <div
              v-if="i < 2"
              class="mb-4 h-px w-12 transition-colors"
              :class="store.step > i + 1 ? 'bg-emerald-500' : 'bg-slate-200 dark:bg-slate-700'"
              role="presentation"
            />
          </template>
        </nav>

        <div v-if="!hasItems" class="text-center py-10">
          <p class="text-slate-500 dark:text-slate-400 mb-4">Tu carrito está vacío.</p>
          <RouterLink to="/" class="text-cyan-600 dark:text-cyan-400 font-medium hover:underline">Ir a la tienda →</RouterLink>
        </div>
        <template v-else>
          <CheckoutStep1 v-if="store.step === 1" />
          <CheckoutStep2 v-else-if="store.step === 2" @back="store.step = 1" />
          <CheckoutStep3 v-else @back="store.step = 2" @complete="onComplete" />
        </template>
      </div>
    </template>

  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import CheckoutGuestOptions from '../components/CheckoutGuestOptions.vue'
import CheckoutStep1 from '@/components/CheckoutStep1.vue'
import CheckoutStep2 from '@/components/CheckoutStep2.vue'
import CheckoutStep3 from '@/components/CheckoutStep3.vue'
import { useAuthStore } from '@/stores/auth'
import { useCarritoStore } from '@/stores/carrito'
import { useCheckoutStore } from '@/stores/checkout'

const route = useRoute()
const store = useCheckoutStore()
const carrito = useCarritoStore()
const auth = useAuthStore()

const guestCheckout = ref(false)
const loading = ref(true)

// Mensaje de retorno de Mercado Pago
const mpStatus = computed(() => route.query.status || null)
const mpStatusMessage = computed(() => {
  if (mpStatus.value === 'failure') return 'El pago no se pudo completar. Puedes intentarlo de nuevo.'
  if (mpStatus.value === 'pending') return 'Tu pago está pendiente de confirmación. Si ya pagaste, espera unos minutos.'
  return null
})

onMounted(async () => {
  store.reset()
  await carrito.cargar()
  loading.value = false
})

watch(
  () => auth.isAuthenticated,
  (isAuth) => {
    if (isAuth) {
      guestCheckout.value = false
    }
  }
)

const showSteps = computed(() => auth.isAuthenticated || guestCheckout.value)
const hasItems = computed(() => carrito.items.length > 0)

const startGuestCheckout = () => {
  guestCheckout.value = true
  store.step = 1
  store.direccion.save = false
}

const handleLoggedIn = async () => {
  guestCheckout.value = false
  store.step = 1
  await carrito.cargar()
}

const onComplete = () => {
  guestCheckout.value = false
}
</script>
