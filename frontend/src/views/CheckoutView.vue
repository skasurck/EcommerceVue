<template>
  <div class="max-w-xl mx-auto pt-10">
    <CheckoutGuestOptions
      v-if="!showSteps"
      @guest="startGuestCheckout"
      @logged-in="handleLoggedIn"
    />

    <div v-else class="space-y-6">
      <h1 class="text-2xl font-semibold text-gray-900 text-center">Finaliza tu compra</h1>
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
import CheckoutStep1 from '../components/CheckoutStep1.vue'
import CheckoutStep2 from '../components/CheckoutStep2.vue'
import CheckoutStep3 from '../components/CheckoutStep3.vue'
import { useAuthStore } from '../stores/auth'
import { useCarritoStore } from '../stores/carrito'
import { useCheckoutStore } from '../stores/checkout'
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
