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
    <div class="flex gap-2 mt-4">
      <button type="button" @click="emit('back')">Atrás</button>
      <button type="button" @click="finalizar">Finalizar</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useCheckoutStore } from '../stores/checkout';
import { crearPedido } from '../services/checkout';

const emit = defineEmits(['back', 'complete']);
const store = useCheckoutStore();
const metodoPago = ref(store.metodoPago || 'transferencia');

const finalizar = async () => {
  store.metodoPago = metodoPago.value;
  try {
    await crearPedido({
      direccion: store.direccion,
      metodo_envio: store.metodoEnvio?.id,
      metodo_pago: store.metodoPago,
      indicaciones: store.indicaciones,
      save_address: store.direccion.save,
    });
    emit('complete');
    store.reset();
  } catch (e) {
    console.error(e);
  }
};
</script>
