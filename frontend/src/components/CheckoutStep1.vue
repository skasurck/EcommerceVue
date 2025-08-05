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
      <input v-model="nombre" placeholder="Nombre" />
      <span class="error">{{ errors.nombre }}</span>
      <input v-model="apellidos" placeholder="Apellidos" />
      <span class="error">{{ errors.apellidos }}</span>
      <input v-model="email" placeholder="Email" />
      <span class="error">{{ errors.email }}</span>
      <input v-model="nombre_empresa" placeholder="Nombre empresa" />
      <input v-model="calle" placeholder="Calle" />
      <span class="error">{{ errors.calle }}</span>
      <input v-model="numero_exterior" placeholder="Número exterior" />
      <span class="error">{{ errors.numero_exterior }}</span>
      <input v-model="numero_interior" placeholder="Número interior" />
      <input v-model="colonia" placeholder="Colonia" />
      <span class="error">{{ errors.colonia }}</span>
      <input v-model="ciudad" placeholder="Ciudad o alcaldía" />
      <span class="error">{{ errors.ciudad }}</span>
      <input v-model="pais" placeholder="País" />
      <span class="error">{{ errors.pais }}</span>
      <input v-model="estado" placeholder="Estado" />
      <span class="error">{{ errors.estado }}</span>
      <input v-model="codigo_postal" placeholder="Código postal" />
      <span class="error">{{ errors.codigo_postal }}</span>
      <input v-model="telefono" placeholder="Teléfono" />
      <span class="error">{{ errors.telefono }}</span>
      <textarea v-model="referencias" placeholder="Referencias"></textarea>
      <label v-if="!tieneDireccion"><input type="checkbox" v-model="save" /> Guardar dirección</label>
      <button type="submit">Continuar</button>
    </form>
    <div class="mt-4 p-4 border rounded">
      <div class="flex justify-between">
        <span>Subtotal</span>
        <span>${{ (subtotal ?? 0).toFixed(2) }}</span>
      </div>
      <div class="flex justify-between">
        <span>Envío</span>
        <span>${{ (envio ?? 0).toFixed(2) }}</span>
      </div>
      <div class="flex justify-between font-bold">
        <span>Total</span>
        <span>${{ (total ?? 0).toFixed(2) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useForm } from 'vee-validate';
import * as yup from 'yup';
import { useCheckoutStore } from '../stores/checkout';
import { useCarritoStore } from '../stores/carrito';
import { obtenerDirecciones } from '../services/checkout';

const emit = defineEmits(['next']);
const store = useCheckoutStore();
const carrito = useCarritoStore();

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

const { errors, handleSubmit, setValues, defineField } = useForm({
  validationSchema: schema,
  initialValues: { ...store.direccion },
});

const [nombre] = defineField('nombre');
const [apellidos] = defineField('apellidos');
const [email] = defineField('email');
const [nombre_empresa] = defineField('nombre_empresa');
const [calle] = defineField('calle');
const [numero_exterior] = defineField('numero_exterior');
const [numero_interior] = defineField('numero_interior');
const [colonia] = defineField('colonia');
const [ciudad] = defineField('ciudad');
const [pais] = defineField('pais');
const [estado] = defineField('estado');
const [codigo_postal] = defineField('codigo_postal');
const [telefono] = defineField('telefono');
const [referencias] = defineField('referencias');
const [save] = defineField('save');

const direcciones = ref([]);
const seleccionada = ref(null);
const tieneDireccion = ref(false);

onMounted(async () => {
  try {
    const { data } = await obtenerDirecciones();
    direcciones.value = data.direcciones;
    tieneDireccion.value = data.tiene_direccion;
    if (direcciones.value.length === 1) {
      seleccionada.value = direcciones.value[0];
      seleccionarDireccion();
    } else {
      const def = direcciones.value.find(d => d.predeterminada);
      if (def) {
        seleccionada.value = def;
        seleccionarDireccion();
      }
    }
  } catch {
    direcciones.value = [];
    tieneDireccion.value = false;
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
  store.step = 2;
  emit('next');
});

const subtotal = computed(() => carrito.subtotal);
const envio = computed(() => store.metodoEnvio?.costo || 0);
const total = computed(() => subtotal.value + envio.value);
</script>

<style scoped>
.error {
  color: red;
  font-size: 0.8em;
}
</style>
