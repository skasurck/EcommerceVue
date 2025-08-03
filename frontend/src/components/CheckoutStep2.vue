<template>
  <div>
    <div v-for="m in metodos" :key="m.id">
      <label>
        <input type="radio" v-model="metodo" :value="m" />
        {{ m.nombre }} - ${{ m.costo }} MXN
      </label>
    </div>
    <textarea v-model="indicaciones" placeholder="Indicaciones del pedido"></textarea>
    <div class="mt-4 p-4 border rounded">
      <div class="flex justify-between">
        <span>Subtotal</span>
        <span>${{ subtotal.toFixed(2) }}</span>
      </div>
      <div class="flex justify-between">
        <span>Envío</span>
        <span>${{ envio.toFixed(2) }}</span>
      </div>
      <div class="flex justify-between font-bold">
        <span>Total</span>
        <span>${{ total.toFixed(2) }}</span>
      </div>
    </div>
    <div class="flex gap-2 mt-2">
      <button type="button" @click="emit('back')">Atrás</button>
      <button type="button" @click="onSubmit">Continuar</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { obtenerMetodosEnvio } from '../services/checkout';
import { useCheckoutStore } from '../stores/checkout';
import { useCarritoStore } from '../stores/carrito';

const emit = defineEmits(['next', 'back']);
const store = useCheckoutStore();
const carrito = useCarritoStore();

const metodos = ref([]);
const metodo = ref(store.metodoEnvio);
const indicaciones = ref(store.indicaciones);

onMounted(async () => {
  try {
    const { data } = await obtenerMetodosEnvio();
    metodos.value = data;
  } catch {
    metodos.value = [];
  }
});

const onSubmit = () => {
  store.metodoEnvio = metodo.value;
  store.indicaciones = indicaciones.value;
  store.step = 3;
  emit('next');
};

const subtotal = computed(() => Number(carrito.subtotal));
const envio = computed(() => Number(metodo.value?.costo ?? 0));
const total = computed(() => subtotal.value + envio.value);
</script>
