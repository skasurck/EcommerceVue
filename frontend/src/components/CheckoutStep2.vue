<template>
  <div>
    <div v-for="m in metodos" :key="m.id">
      <label>
        <input type="radio" v-model="metodo" :value="m" />
        {{ m.nombre }} - ${{ m.costo }} MXN
      </label>
    </div>
    <textarea v-model="indicaciones" placeholder="Indicaciones del pedido"></textarea>
    <div class="flex gap-2 mt-2">
      <button type="button" @click="emit('back')">Atrás</button>
      <button type="button" @click="onSubmit">Continuar</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { obtenerMetodosEnvio } from '../services/checkout';
import { useCheckoutStore } from '../stores/checkout';

const emit = defineEmits(['next', 'back']);
const store = useCheckoutStore();

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
  emit('next');
};
</script>
