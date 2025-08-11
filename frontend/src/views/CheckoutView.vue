<template>
  <div class="max-w-xl mx-auto pt-10">
    <CheckoutStep1 v-if="store.step === 1" />
    <CheckoutStep2 v-else-if="store.step === 2" @back="store.step = 1" />
    <CheckoutStep3 v-else @back="store.step = 2" @complete="onComplete" />
  </div>
</template>

<script setup>
import { useCheckoutStore } from '../stores/checkout';
import { useCarritoStore } from '../stores/carrito';
import CheckoutStep1 from '../components/CheckoutStep1.vue';
import CheckoutStep2 from '../components/CheckoutStep2.vue';
import CheckoutStep3 from '../components/CheckoutStep3.vue';

const store = useCheckoutStore();
const carrito = useCarritoStore();

carrito.cargar();

const onComplete = () => {
  alert('Pedido creado');
};
</script>
