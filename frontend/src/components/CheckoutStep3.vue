<template>
  <div>
    <div>
      <label>
        <input type="radio" value="transferencia" v-model="metodoPago" />
        Transferencia directa
      </label>
      <div v-if="metodoPago === 'transferencia'" class="border p-2 mt-2">
        <p>Banco: 0000</p>
        <p>CLABE: 000000000000000000</p>
      </div>
    </div>
    <div class="mt-2">
      <label>
        <input type="radio" value="tarjeta" v-model="metodoPago" />
        Pago con tarjeta
      </label>
      <div v-if="metodoPago === 'tarjeta'" class="border p-2 mt-2">
        <p>El pago se procesará mediante la pasarela seleccionada.</p>
      </div>
    </div>
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
    <div class="flex gap-2 mt-4">
      <button type="button" @click="emit('back')">Atrás</button>
      <button type="button" @click="finalizar">Finalizar</button>
    </div>
    <p v-if="error" class="text-red-600 mt-2">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useCheckoutStore } from '../stores/checkout';
import { useCarritoStore } from '../stores/carrito';
import { crearPedido } from '../services/checkout';

const emit = defineEmits(['back', 'complete']);
const store = useCheckoutStore();
const carrito = useCarritoStore();
const auth = useAuthStore();
const metodoPago = ref(store.metodoPago || 'transferencia');
const error = ref('');

const finalizar = async () => {
  store.metodoPago = metodoPago.value;
  const { save, ...direccion } = store.direccion;
  error.value = '';
  try {
    await crearPedido({
      direccion,
      metodo_envio: store.metodoEnvio?.id,
      metodo_pago: store.metodoPago,
      indicaciones: store.indicaciones,
      save_address: auth.isAuthenticated && save,
    });
    await carrito.cargar();
    emit('complete');
    store.reset();
  } catch (e) {
    error.value = e.response?.data?.detail || 'No se pudo crear el pedido';
  }
};

const subtotal = computed(() => Number(carrito.subtotal));
const envio = computed(() => Number(store.metodoEnvio?.costo ?? 0));
const total = computed(() => subtotal.value + envio.value);
</script>
