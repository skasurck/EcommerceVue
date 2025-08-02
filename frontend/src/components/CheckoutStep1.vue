<template>
  <div>
    <div v-if="direcciones.length">
      <label>Direcciones guardadas</label>
      <select v-model="seleccionada" @change="seleccionarDireccion">
        <option :value="null">Nueva dirección</option>
        <option v-for="d in direcciones" :key="d.id" :value="d">{{ d.calle }} {{ d.numero_exterior }}</option>
      </select>
    </div>
    <form @submit.prevent="onSubmit" class="flex flex-col gap-2">
      <input v-model="values.nombre" placeholder="Nombre" />
      <span class="error">{{ errors.nombre }}</span>
      <input v-model="values.apellidos" placeholder="Apellidos" />
      <span class="error">{{ errors.apellidos }}</span>
      <input v-model="values.email" placeholder="Email" />
      <span class="error">{{ errors.email }}</span>
      <input v-model="values.nombre_empresa" placeholder="Nombre empresa" />
      <input v-model="values.calle" placeholder="Calle" />
      <span class="error">{{ errors.calle }}</span>
      <input v-model="values.numero_exterior" placeholder="Número exterior" />
      <span class="error">{{ errors.numero_exterior }}</span>
      <input v-model="values.numero_interior" placeholder="Número interior" />
      <input v-model="values.colonia" placeholder="Colonia" />
      <span class="error">{{ errors.colonia }}</span>
      <input v-model="values.ciudad" placeholder="Ciudad o alcaldía" />
      <span class="error">{{ errors.ciudad }}</span>
      <input v-model="values.pais" placeholder="País" />
      <span class="error">{{ errors.pais }}</span>
      <input v-model="values.estado" placeholder="Estado" />
      <span class="error">{{ errors.estado }}</span>
      <input v-model="values.codigo_postal" placeholder="Código postal" />
      <span class="error">{{ errors.codigo_postal }}</span>
      <input v-model="values.telefono" placeholder="Teléfono" />
      <span class="error">{{ errors.telefono }}</span>
      <textarea v-model="values.referencias" placeholder="Referencias"></textarea>
      <label><input type="checkbox" v-model="values.save" /> Guardar dirección</label>
      <button type="submit">Continuar</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useForm } from 'vee-validate';
import * as yup from 'yup';
import { useCheckoutStore } from '../stores/checkout';
import { obtenerDirecciones } from '../services/checkout';

const emit = defineEmits(['next']);
const store = useCheckoutStore();

const schema = yup.object({
  nombre: yup.string().required(),
  apellidos: yup.string().required(),
  email: yup.string().email().required(),
  calle: yup.string().required(),
  numero_exterior: yup.string().required(),
  colonia: yup.string().required(),
  ciudad: yup.string().required(),
  pais: yup.string().required(),
  estado: yup.string().required(),
  codigo_postal: yup.string().required(),
  telefono: yup.string().required(),
});

const { values, errors, handleSubmit, setValues } = useForm({
  validationSchema: schema,
  initialValues: store.direccion,
});

const direcciones = ref([]);
const seleccionada = ref(null);

onMounted(async () => {
  try {
    const { data } = await obtenerDirecciones();
    direcciones.value = data;
  } catch {
    direcciones.value = [];
  }
});

const seleccionarDireccion = () => {
  if (seleccionada.value) {
    setValues(seleccionada.value);
  } else {
    setValues(store.direccion);
  }
};

const onSubmit = handleSubmit((vals) => {
  store.direccion = { ...vals };
  emit('next');
});
</script>

<style scoped>
.error {
  color: red;
  font-size: 0.8em;
}
</style>
