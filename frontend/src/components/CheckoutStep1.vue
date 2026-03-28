<template>
  <div class="space-y-5">

    <!-- Dirección guardada -->
    <div v-if="auth.isAuthenticated && direcciones.length" class="space-y-1">
      <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Dirección guardada</label>
      <select
        v-model="seleccionada"
        @change="seleccionarDireccion"
        class="w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400"
      >
        <option :value="null">— Nueva dirección —</option>
        <option v-for="d in direcciones" :key="d.id" :value="d">
          {{ d.calle }} {{ d.numero_exterior }}, {{ d.colonia }}, {{ d.ciudad }}
        </option>
      </select>
    </div>

    <form @submit.prevent="onSubmit" class="space-y-4">

      <!-- Nombre y apellidos -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Nombre <span class="text-rose-500">*</span></label>
          <input v-model="nombre" placeholder="Nombre" :class="inputClass(errors.nombre)" />
          <p v-if="errors.nombre" class="text-xs text-rose-500">{{ errors.nombre }}</p>
        </div>
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Apellidos <span class="text-rose-500">*</span></label>
          <input v-model="apellidos" placeholder="Apellidos" :class="inputClass(errors.apellidos)" />
          <p v-if="errors.apellidos" class="text-xs text-rose-500">{{ errors.apellidos }}</p>
        </div>
      </div>

      <!-- Email y teléfono -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Correo electrónico <span class="text-rose-500">*</span></label>
          <input v-model="email" type="email" placeholder="correo@ejemplo.com" :class="inputClass(errors.email)" />
          <p v-if="errors.email" class="text-xs text-rose-500">{{ errors.email }}</p>
        </div>
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Teléfono <span class="text-rose-500">*</span></label>
          <input v-model="telefono" type="tel" placeholder="10 dígitos" :class="inputClass(errors.telefono)" />
          <p v-if="errors.telefono" class="text-xs text-rose-500">{{ errors.telefono }}</p>
        </div>
      </div>

      <!-- Empresa (opcional) -->
      <div class="space-y-1">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Empresa <span class="text-xs text-slate-400">(opcional)</span></label>
        <input v-model="nombre_empresa" placeholder="Nombre de empresa" :class="inputClass()" />
      </div>

      <!-- Calle y números -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="col-span-2 space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Calle <span class="text-rose-500">*</span></label>
          <input v-model="calle" placeholder="Nombre de la calle" :class="inputClass(errors.calle)" />
          <p v-if="errors.calle" class="text-xs text-rose-500">{{ errors.calle }}</p>
        </div>
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Núm. ext. <span class="text-rose-500">*</span></label>
          <input v-model="numero_exterior" placeholder="Ej. 72" :class="inputClass(errors.numero_exterior)" />
          <p v-if="errors.numero_exterior" class="text-xs text-rose-500">{{ errors.numero_exterior }}</p>
        </div>
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Núm. int. <span class="text-xs text-slate-400">(opc.)</span></label>
          <input v-model="numero_interior" placeholder="Depto, piso…" :class="inputClass()" />
        </div>
      </div>

      <!-- Código postal con detección automática -->
      <div class="space-y-1">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Código postal <span class="text-rose-500">*</span>
        </label>
        <div class="relative">
          <input
            v-model="codigo_postal"
            placeholder="5 dígitos"
            maxlength="5"
            inputmode="numeric"
            :class="inputClass(errors.codigo_postal)"
            @input="onCPInput"
          />
          <div v-if="cpCargando" class="absolute right-3 top-1/2 -translate-y-1/2">
            <svg class="w-4 h-4 animate-spin text-cyan-500" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
          </div>
          <div v-else-if="cpOk" class="absolute right-3 top-1/2 -translate-y-1/2">
            <svg class="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
        </div>
        <p v-if="errors.codigo_postal" class="text-xs text-rose-500">{{ errors.codigo_postal }}</p>
        <p v-if="cpError" class="text-xs text-rose-500">{{ cpError }}</p>
      </div>

      <!-- Colonia -->
      <div class="space-y-1">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Colonia <span class="text-rose-500">*</span></label>
        <!-- Dropdown cuando el CP encontró colonias -->
        <select
          v-if="colonias.length"
          v-model="colonia"
          :class="inputClass(errors.colonia)"
        >
          <option value="">— Selecciona colonia —</option>
          <option v-for="c in colonias" :key="c" :value="c">{{ c }}</option>
        </select>
        <!-- Input libre cuando no hay datos del CP -->
        <input
          v-else
          v-model="colonia"
          placeholder="Colonia o fraccionamiento"
          :class="inputClass(errors.colonia)"
        />
        <p v-if="errors.colonia" class="text-xs text-rose-500">{{ errors.colonia }}</p>
      </div>

      <!-- Ciudad/Municipio y Estado (auto-llenados) -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Ciudad / Municipio <span class="text-rose-500">*</span></label>
          <input v-model="ciudad" placeholder="Ciudad o alcaldía" :class="inputClass(errors.ciudad)" />
          <p v-if="errors.ciudad" class="text-xs text-rose-500">{{ errors.ciudad }}</p>
        </div>
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Estado <span class="text-rose-500">*</span></label>
          <input v-model="estado" placeholder="Estado" :class="inputClass(errors.estado)" />
          <p v-if="errors.estado" class="text-xs text-rose-500">{{ errors.estado }}</p>
        </div>
      </div>

      <!-- País (oculto, siempre México) -->
      <input v-model="pais" type="hidden" />

      <!-- Referencias -->
      <div class="space-y-1">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Referencias <span class="text-xs text-slate-400">(opcional)</span></label>
        <textarea
          v-model="referencias"
          placeholder="Entre calles, color de fachada, puntos de referencia…"
          rows="2"
          class="w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 resize-none"
        />
      </div>

      <!-- Guardar dirección -->
      <label v-if="auth.isAuthenticated && !tieneDireccion" class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 cursor-pointer">
        <input type="checkbox" v-model="save" class="rounded border-slate-300 text-cyan-500 focus:ring-cyan-400" />
        Guardar esta dirección para futuras compras
      </label>

      <!-- Botón -->
      <button
        type="submit"
        class="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-white font-semibold text-sm shadow-sm transition-colors"
      >
        Continuar →
      </button>

    </form>

    <!-- Resumen de totales -->
    <div class="rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-4 text-sm space-y-1.5">
      <div class="flex justify-between text-slate-600 dark:text-slate-400">
        <span>Subtotal</span>
        <span>{{ fmt(subtotal) }}</span>
      </div>
      <div class="flex justify-between text-slate-600 dark:text-slate-400">
        <span>Envío</span>
        <span>{{ envio > 0 ? fmt(envio) : 'Se calcula en el siguiente paso' }}</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useForm } from 'vee-validate';
import * as yup from 'yup';
import { useAuthStore } from '@/stores/auth';
import { useCheckoutStore } from '@/stores/checkout';
import { useCarritoStore } from '@/stores/carrito';
import { obtenerDirecciones } from '@/services/checkout';

const emit = defineEmits(['next']);
const store = useCheckoutStore();
const carrito = useCarritoStore();
const auth = useAuthStore();

const schema = yup.object({
  nombre: yup.string().required('Requerido'),
  apellidos: yup.string().required('Requerido'),
  email: yup.string().email('Email inválido').required('Requerido'),
  calle: yup.string().required('Requerido'),
  numero_exterior: yup.string().required('Requerido'),
  colonia: yup.string().required('Requerido'),
  ciudad: yup.string().required('Requerido'),
  pais: yup.string().required(),
  estado: yup.string().required('Requerido'),
  codigo_postal: yup.string().matches(/^\d{5}$/, 'Debe ser de 5 dígitos').required('Requerido'),
  telefono: yup.string().required('Requerido'),
});

const { errors, handleSubmit, setValues, defineField } = useForm({
  validationSchema: schema,
  initialValues: { pais: 'México', ...store.direccion },
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

// ── Código postal ──────────────────────────────────────────────────────────
const colonias = ref([]);
const cpCargando = ref(false);
const cpError = ref('');
const cpOk = ref(false);

const buscarCP = async (cp) => {
  if (!/^\d{5}$/.test(cp)) {
    colonias.value = [];
    cpOk.value = false;
    return;
  }
  cpCargando.value = true;
  cpError.value = '';
  cpOk.value = false;
  try {
    const res = await fetch(
      `https://sepomex.icalialabs.com/api/v1/zip_codes?zip_code=${cp}&per_page=100`,
    );
    const data = await res.json();
    const zips = data?.zip_codes ?? [];
    if (!zips.length) {
      cpError.value = 'Código postal no encontrado en México';
      colonias.value = [];
      return;
    }
    // Colonias únicas ordenadas
    colonias.value = [...new Set(zips.map(z => z.d_asenta))].sort();

    const primero = zips[0];
    // Auto-llenar campos —  el usuario puede corregirlos si quiere
    estado.value = primero.d_estado ?? estado.value;
    ciudad.value = primero.D_mnpio || primero.d_ciudad || ciudad.value;
    pais.value = 'México';
    // Si solo hay una colonia, auto-seleccionarla
    if (colonias.value.length === 1) colonia.value = colonias.value[0];
    cpOk.value = true;
  } catch {
    cpError.value = 'No se pudo consultar el código postal, llena los campos manualmente';
    colonias.value = [];
  } finally {
    cpCargando.value = false;
  }
};

const onCPInput = (e) => {
  const val = e.target.value.replace(/\D/g, '').slice(0, 5);
  codigo_postal.value = val;
  if (val.length === 5) buscarCP(val);
  else { colonias.value = []; cpOk.value = false; cpError.value = ''; }
};

// Re-buscar si se carga una dirección guardada con CP ya definido
watch(codigo_postal, (val) => {
  if (val?.length === 5 && !colonias.value.length && !cpCargando.value) buscarCP(val);
});

// ── Direcciones guardadas ──────────────────────────────────────────────────
const direcciones = ref([]);
const seleccionada = ref(null);
const tieneDireccion = ref(false);

onMounted(async () => {
  if (!auth.isAuthenticated) {
    setValues({ pais: 'México', ...store.direccion, save: false });
    return;
  }
  try {
    const { data } = await obtenerDirecciones();
    direcciones.value = data.direcciones;
    tieneDireccion.value = data.tiene_direccion;
    const def = direcciones.value.length === 1
      ? direcciones.value[0]
      : direcciones.value.find(d => d.predeterminada);
    if (def) { seleccionada.value = def; seleccionarDireccion(); }
  } catch {
    direcciones.value = [];
    tieneDireccion.value = false;
  }
});

const seleccionarDireccion = () => {
  const vals = seleccionada.value ? seleccionada.value : { ...store.direccion, pais: 'México' };
  setValues(vals);
  colonias.value = [];
  cpOk.value = false;
  if (vals.codigo_postal?.length === 5) buscarCP(vals.codigo_postal);
};

// ── Submit ─────────────────────────────────────────────────────────────────
const onSubmit = handleSubmit((vals) => {
  store.direccion = { ...vals };
  store.step = 2;
  emit('next');
});

// ── Helpers ────────────────────────────────────────────────────────────────
const fmt = (n) => Number(n).toLocaleString('es-MX', { style: 'currency', currency: 'MXN' });
const subtotal = computed(() => carrito.subtotal);
const envio = computed(() => store.metodoEnvio?.costo || 0);

const inputClass = (err) =>
  `w-full rounded-xl border px-3 py-2.5 text-sm bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-400 transition-colors ${
    err
      ? 'border-rose-400 dark:border-rose-500'
      : 'border-slate-300 dark:border-slate-600'
  }`;
</script>
