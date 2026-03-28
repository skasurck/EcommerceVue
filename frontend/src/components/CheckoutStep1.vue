<template>
  <div class="space-y-5">

    <!-- ── Tarjetas de direcciones guardadas ── -->
    <div v-if="auth.isAuthenticated && direcciones.length">
      <p class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">Selecciona una dirección de entrega</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">

        <button
          v-for="d in direcciones"
          :key="d.id"
          type="button"
          @click="elegirDireccion(d)"
          :class="tarjetaClass(seleccionada?.id === d.id)"
        >
          <div class="flex items-start gap-3">
            <div :class="radioClass(seleccionada?.id === d.id)">
              <div v-if="seleccionada?.id === d.id" class="w-1.5 h-1.5 rounded-full bg-white"></div>
            </div>
            <div class="text-left min-w-0">
              <p class="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">
                {{ d.calle }} {{ d.numero_exterior }}<span v-if="d.numero_interior"> Int. {{ d.numero_interior }}</span>
              </p>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{{ d.colonia }}, {{ d.ciudad }}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400">{{ d.estado }}, CP {{ d.codigo_postal }}</p>
              <span
                v-if="d.predeterminada"
                class="inline-block mt-1.5 text-[11px] font-medium text-cyan-600 dark:text-cyan-400 bg-cyan-50 dark:bg-cyan-900/30 border border-cyan-200 dark:border-cyan-800 rounded-full px-2 py-0.5"
              >Predeterminada</span>
            </div>
          </div>
        </button>

        <!-- Nueva dirección -->
        <button
          type="button"
          @click="elegirNueva()"
          :class="tarjetaClass(seleccionada === null)"
        >
          <div class="flex items-start gap-3">
            <div :class="radioClass(seleccionada === null)">
              <div v-if="seleccionada === null" class="w-1.5 h-1.5 rounded-full bg-white"></div>
            </div>
            <div class="text-left">
              <p class="font-semibold text-sm text-slate-800 dark:text-slate-100">+ Nueva dirección</p>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Agregar una dirección diferente</p>
            </div>
          </div>
        </button>

      </div>
    </div>

    <!-- ── Formulario ── -->
    <form v-if="mostrarFormulario" @submit.prevent="onSubmit" class="space-y-4">

      <!-- Nombre y apellidos -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Nombre <span class="text-rose-500">*</span></label>
          <input v-model="nombre" autocomplete="given-name" placeholder="Nombre" :class="inputClass(errors.nombre)" />
          <p v-if="errors.nombre" class="text-xs text-rose-500">{{ errors.nombre }}</p>
        </div>
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Apellidos <span class="text-rose-500">*</span></label>
          <input v-model="apellidos" autocomplete="family-name" placeholder="Apellidos" :class="inputClass(errors.apellidos)" />
          <p v-if="errors.apellidos" class="text-xs text-rose-500">{{ errors.apellidos }}</p>
        </div>
      </div>

      <!-- Email y teléfono -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Correo electrónico <span class="text-rose-500">*</span></label>
          <input v-model="email" type="email" autocomplete="email" placeholder="correo@ejemplo.com" :class="inputClass(errors.email)" />
          <p v-if="errors.email" class="text-xs text-rose-500">{{ errors.email }}</p>
        </div>
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Teléfono <span class="text-rose-500">*</span></label>
          <input v-model="telefono" type="tel" autocomplete="tel" placeholder="10 dígitos" :class="inputClass(errors.telefono)" />
          <p v-if="errors.telefono" class="text-xs text-rose-500">{{ errors.telefono }}</p>
        </div>
      </div>

      <!-- Empresa (opcional) -->
      <div class="space-y-1">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Empresa <span class="text-xs text-slate-400">(opcional)</span></label>
        <input v-model="nombre_empresa" autocomplete="organization" placeholder="Nombre de empresa" :class="inputClass()" />
      </div>

      <!-- Calle y números -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="col-span-2 space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Calle <span class="text-rose-500">*</span></label>
          <input v-model="calle" autocomplete="address-line1" placeholder="Nombre de la calle" :class="inputClass(errors.calle)" />
          <p v-if="errors.calle" class="text-xs text-rose-500">{{ errors.calle }}</p>
        </div>
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Núm. ext. <span class="text-rose-500">*</span></label>
          <input v-model="numero_exterior" autocomplete="address-line2" placeholder="Ej. 72" :class="inputClass(errors.numero_exterior)" />
          <p v-if="errors.numero_exterior" class="text-xs text-rose-500">{{ errors.numero_exterior }}</p>
        </div>
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Núm. int. <span class="text-xs text-slate-400">(opc.)</span></label>
          <input v-model="numero_interior" autocomplete="address-line3" placeholder="Depto, piso…" :class="inputClass()" />
        </div>
      </div>

      <!-- Código postal -->
      <div class="space-y-1">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Código postal <span class="text-rose-500">*</span>
        </label>
        <div class="relative">
          <input
            v-model="codigo_postal"
            autocomplete="postal-code"
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
        <select v-if="colonias.length" v-model="colonia" :class="inputClass(errors.colonia)">
          <option value="">— Selecciona colonia —</option>
          <option v-for="c in colonias" :key="c" :value="c">{{ c }}</option>
        </select>
        <input v-else v-model="colonia" autocomplete="address-level3" placeholder="Colonia o fraccionamiento" :class="inputClass(errors.colonia)" />
        <p v-if="errors.colonia" class="text-xs text-rose-500">{{ errors.colonia }}</p>
      </div>

      <!-- Ciudad y Estado -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Ciudad / Municipio <span class="text-rose-500">*</span></label>
          <input v-model="ciudad" autocomplete="address-level2" placeholder="Ciudad o alcaldía" :class="inputClass(errors.ciudad)" />
          <p v-if="errors.ciudad" class="text-xs text-rose-500">{{ errors.ciudad }}</p>
        </div>
        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Estado <span class="text-rose-500">*</span></label>
          <input v-model="estado" autocomplete="address-level1" placeholder="Estado" :class="inputClass(errors.estado)" />
          <p v-if="errors.estado" class="text-xs text-rose-500">{{ errors.estado }}</p>
        </div>
      </div>

      <!-- País oculto -->
      <input v-model="pais" type="hidden" autocomplete="country-name" />

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

      <button type="submit" class="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-white font-semibold text-sm shadow-sm transition-colors">
        Continuar →
      </button>

    </form>

    <!-- Botón cuando hay dirección guardada seleccionada -->
    <button
      v-else-if="seleccionada"
      type="button"
      @click="confirmarSeleccionada"
      class="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-white font-semibold text-sm shadow-sm transition-colors"
    >
      Continuar con esta dirección →
    </button>

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
  nombre:          yup.string().required('Requerido'),
  apellidos:       yup.string().required('Requerido'),
  email:           yup.string().email('Email inválido').required('Requerido'),
  calle:           yup.string().required('Requerido'),
  numero_exterior: yup.string().required('Requerido'),
  colonia:         yup.string().required('Requerido'),
  ciudad:          yup.string().required('Requerido'),
  pais:            yup.string().required(),
  estado:          yup.string().required('Requerido'),
  codigo_postal:   yup.string().matches(/^\d{5}$/, 'Debe ser de 5 dígitos').required('Requerido'),
  telefono:        yup.string().required('Requerido'),
});

const { errors, handleSubmit, setValues, defineField } = useForm({
  validationSchema: schema,
  initialValues: { pais: 'México', ...store.direccion },
});

const [nombre]          = defineField('nombre');
const [apellidos]       = defineField('apellidos');
const [email]           = defineField('email');
const [nombre_empresa]  = defineField('nombre_empresa');
const [calle]           = defineField('calle');
const [numero_exterior] = defineField('numero_exterior');
const [numero_interior] = defineField('numero_interior');
const [colonia]         = defineField('colonia');
const [ciudad]          = defineField('ciudad');
const [pais]            = defineField('pais');
const [estado]          = defineField('estado');
const [codigo_postal]   = defineField('codigo_postal');
const [telefono]        = defineField('telefono');
const [referencias]     = defineField('referencias');
const [save]            = defineField('save');

// ── Código postal (SEPOMEX) ────────────────────────────────────────────────
const colonias   = ref([]);
const cpCargando = ref(false);
const cpError    = ref('');
const cpOk       = ref(false);

const buscarCP = async (cp) => {
  if (!/^\d{5}$/.test(cp)) { colonias.value = []; cpOk.value = false; return; }
  cpCargando.value = true;
  cpError.value = '';
  cpOk.value = false;
  try {
    const res  = await fetch(`https://sepomex.icalialabs.com/api/v1/zip_codes?zip_code=${cp}&per_page=100`);
    const data = await res.json();
    const zips = data?.zip_codes ?? [];
    if (!zips.length) { cpError.value = 'Código postal no encontrado en México'; colonias.value = []; return; }
    colonias.value = [...new Set(zips.map(z => z.d_asenta))].sort();
    const primero = zips[0];
    estado.value  = primero.d_estado ?? estado.value;
    ciudad.value  = primero.D_mnpio || primero.d_ciudad || ciudad.value;
    pais.value    = 'México';
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

watch(codigo_postal, (val) => {
  if (val?.length === 5 && !colonias.value.length && !cpCargando.value) buscarCP(val);
});

// ── Direcciones guardadas ──────────────────────────────────────────────────
const direcciones   = ref([]);
const seleccionada  = ref(null);
const tieneDireccion = ref(false);

const mostrarFormulario = computed(() =>
  !auth.isAuthenticated || !direcciones.value.length || seleccionada.value === null
);

onMounted(async () => {
  if (!auth.isAuthenticated) {
    setValues({ pais: 'México', ...store.direccion, save: false });
    return;
  }
  try {
    const { data } = await obtenerDirecciones();
    direcciones.value   = data.direcciones;
    tieneDireccion.value = data.tiene_direccion;
    const def = direcciones.value.length === 1
      ? direcciones.value[0]
      : direcciones.value.find(d => d.predeterminada);
    if (def) elegirDireccion(def);
  } catch {
    direcciones.value   = [];
    tieneDireccion.value = false;
  }
});

const elegirDireccion = (d) => {
  seleccionada.value = d;
  setValues({ ...d, pais: 'México' });
  colonias.value = [];
  cpOk.value = false;
  if (d.codigo_postal?.length === 5) buscarCP(d.codigo_postal);
};

const elegirNueva = () => {
  seleccionada.value = null;
  setValues({ pais: 'México', nombre: '', apellidos: '', email: '', telefono: '',
    calle: '', numero_exterior: '', numero_interior: '', colonia: '',
    ciudad: '', estado: '', codigo_postal: '', referencias: '' });
  colonias.value = [];
  cpOk.value = false;
  cpError.value = '';
};

const confirmarSeleccionada = () => {
  store.direccion = { ...seleccionada.value };
  store.step = 2;
  emit('next');
};

// ── Submit ─────────────────────────────────────────────────────────────────
const onSubmit = handleSubmit((vals) => {
  store.direccion = { ...vals };
  store.step = 2;
  emit('next');
});

// ── Helpers ────────────────────────────────────────────────────────────────
const fmt      = (n) => Number(n).toLocaleString('es-MX', { style: 'currency', currency: 'MXN' });
const subtotal = computed(() => carrito.subtotal);
const envio    = computed(() => store.metodoEnvio?.costo || 0);

const inputClass = (err) =>
  `w-full rounded-xl border px-3 py-2.5 text-sm bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-400 transition-colors ${
    err ? 'border-rose-400 dark:border-rose-500' : 'border-slate-300 dark:border-slate-600'
  }`;

const tarjetaClass = (activa) =>
  `w-full rounded-xl border-2 p-4 text-left transition-all cursor-pointer ${
    activa
      ? 'border-cyan-400 bg-cyan-50 dark:bg-cyan-900/20 dark:border-cyan-500'
      : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-600'
  }`;

const radioClass = (activo) =>
  `mt-0.5 shrink-0 w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors ${
    activo ? 'border-cyan-500 bg-cyan-500' : 'border-slate-300 dark:border-slate-600'
  }`;
</script>
