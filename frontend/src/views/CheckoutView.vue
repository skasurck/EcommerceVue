<template>
  <div class="max-w-xl mx-auto pt-10">
    <CheckoutGuestOptions
      v-if="!showSteps"
      @guest="startGuestCheckout"
      @logged-in="handleLoggedIn"
    />

    <div v-else class="space-y-6">
      <h1 class="text-2xl font-semibold text-gray-900 text-center">Finaliza tu compra</h1>

      <!-- Stepper -->
      <nav v-if="hasItems" class="flex items-center justify-center gap-0">
        <template v-for="(label, i) in ['Dirección', 'Envío', 'Pago']" :key="i">
          <div class="flex flex-col items-center">
            <div
              class="flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold transition-colors"
              :class="store.step === i + 1
                ? 'bg-slate-900 text-white'
                : store.step > i + 1
                  ? 'bg-emerald-500 text-white'
                  : 'bg-slate-200 text-slate-500'"
            >
              <span v-if="store.step > i + 1">✓</span>
              <span v-else>{{ i + 1 }}</span>
            </div>
            <span
              class="mt-1 text-xs"
              :class="store.step === i + 1 ? 'font-semibold text-slate-900' : 'text-slate-400'"
            >{{ label }}</span>
          </div>
          <div
            v-if="i < 2"
            class="mb-4 h-px w-12 transition-colors"
            :class="store.step > i + 1 ? 'bg-emerald-500' : 'bg-slate-200'"
          />
        </template>
      </nav>

      <div v-if="!hasItems" class="text-center text-gray-600">
        Tu carrito está vacío. Agrega productos para continuar.
      </div>
      <template v-else>
        <CheckoutStep1 v-if="store.step === 1" />
        <CheckoutStep2 v-else-if="store.step === 2" @back="store.step = 1" />
        <CheckoutStep3 v-else @back="store.step = 2" @complete="onComplete" />
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'

import CheckoutGuestOptions from '../components/CheckoutGuestOptions.vue'
import CheckoutStep1 from '@/components/CheckoutStep1.vue'
import CheckoutStep2 from '@/components/CheckoutStep2.vue'
import CheckoutStep3 from '@/components/CheckoutStep3.vue'
import { useAuthStore } from '@/stores/auth'
import { useCarritoStore } from '@/stores/carrito'
import { useCheckoutStore } from '@/stores/checkout'
const store = useCheckoutStore()
const carrito = useCarritoStore()
const auth = useAuthStore()

const guestCheckout = ref(false)

onMounted(async () => {
  store.step = 1
  await carrito.cargar()
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
