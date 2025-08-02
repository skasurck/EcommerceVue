<template>
  <div class="max-w-xl mx-auto">
    <CheckoutStep1 v-if="store.step === 1" @next="store.step = 2" />
    <CheckoutStep2 v-else-if="store.step === 2" @next="store.step = 3" @back="store.step = 1" />
    <CheckoutStep3 v-else @back="store.step = 2" @complete="onComplete" />
  </div>
</template>

<script setup>
import { useCheckoutStore } from '../stores/checkout';
import CheckoutStep1 from '../components/CheckoutStep1.vue';
import CheckoutStep2 from '../components/CheckoutStep2.vue';
import CheckoutStep3 from '../components/CheckoutStep3.vue';

const store = useCheckoutStore();

const onComplete = () => {
  alert('Pedido creado');
};
</script>
