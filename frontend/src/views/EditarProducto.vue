<template>
  <div class="space-y-6">
    <!-- TOASTS -->
    <div class="fixed top-4 right-4 z-[60] space-y-2">
      <div v-for="t in toasts" :key="t.id"
           :class="['rounded-lg px-4 py-3 shadow text-sm text-white',
                    t.type==='success' ? 'bg-emerald-600' :
                    t.type==='error' ? 'bg-rose-600' : 'bg-slate-800']">
        {{ t.msg }}
      </div>
    </div>

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <div class="text-sm text-slate-500">Productos / <span class="text-slate-700">Editar</span></div>
        <h1 class="text-2xl font-bold text-slate-800">Editar producto</h1>
      </div>
      <RouterLink to="/admin/productos" class="text-sm text-blue-700 hover:underline">← Volver al listado</RouterLink>
    </div>

    <!-- Básicos -->
    <section class="bg-white border rounded-xl p-5 shadow-sm">
      <h2 class="text-lg font-semibold text-slate-800 mb-3">Información básica</h2>
      <div class="grid sm:grid-cols-2 gap-4">
        <div class="sm:col-span-2">
          <label class="block text-xs font-medium text-slate-600 mb-1">Nombre</label>
          <input v-model="form.nombre" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Ej. Audífonos inalámbricos XYZ" />
          <p v-if="errs.nombre" class="mt-1 text-xs text-rose-600">{{ errs.nombre }}</p>
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-600 mb-1">Precio normal</label>
          <input type="number" step="0.01" v-model.number="form.precio_normal" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 text-right" />
          <p v-if="errs.precio_normal" class="mt-1 text-xs text-rose-600">{{ errs.precio_normal }}</p>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-600 mb-1">Precio rebajado</label>
          <input type="number" step="0.01" v-model.number="form.precio_rebajado" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 text-right" />
          <p v-if="errs.precio_rebajado" class="mt-1 text-xs text-rose-600">{{ errs.precio_rebajado }}</p>
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-600 mb-1">SKU</label>
          <input v-model="form.sku" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <p v-if="errs.sku" class="mt-1 text-xs text-rose-600">{{ errs.sku }}</p>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-600 mb-1">Stock</label>
          <input type="number" v-model.number="form.stock" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 text-right" />
          <p v-if="errs.stock" class="mt-1 text-xs text-rose-600">{{ errs.stock }}</p>
        </div>

        <div class="sm:col-span-2">
          <label class="block text-xs font-medium text-slate-600 mb-1">Descripción corta</label>
          <textarea v-model="form.descripcion_corta" rows="2" class="w-full rounded-md border border-slate-300 px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Resumen breve que aparece en listados"></textarea>
          <p v-if="errs.descripcion_corta" class="mt-1 text-xs text-rose-600">{{ errs.descripcion_corta }}</p>
        </div>

        <div class="sm:col-span-2">
          <label class="block text-xs font-medium text-slate-600 mb-1">Descripción larga</label>
          <textarea v-model="form.descripcion_larga" rows="6" class="w-full rounded-md border border-slate-300 px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Detalles, especificaciones, cuidados, etc."></textarea>
          <p v-if="errs.descripcion_larga" class="mt-1 text-xs text-rose-600">{{ errs.descripcion_larga }}</p>
        </div>
      </div>
    </section>

    <!-- Estado / Inventario -->
    <section class="bg-white border rounded-xl p-5 shadow-sm">
      <h2 class="text-lg font-semibold text-slate-800 mb-3">Estado e inventario</h2>
      <div class="grid sm:grid-cols-3 gap-4">
        <div>
          <label class="block text-xs font-medium text-slate-600 mb-1">Estado inventario</label>
          <select v-model="form.estado_inventario" class="h-10 w-full rounded-md border border-slate-300 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="en_existencia">En existencia</option>
            <option value="agotado">Agotado</option>
          </select>
          <p v-if="errs.estado_inventario" class="mt-1 text-xs text-rose-600">{{ errs.estado_inventario }}</p>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-600 mb-1">Estado</label>
          <select v-model="form.estado" class="h-10 w-full rounded-md border border-slate-300 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="borrador">Borrador</option>
            <option value="publicado">Publicado</option>
          </select>
          <p v-if="errs.estado" class="mt-1 text-xs text-rose-600">{{ errs.estado }}</p>
        </div>
        <div class="flex items-end gap-4">
          <label class="inline-flex items-center gap-2">
            <input type="checkbox" v-model="form.disponible" class="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
            <span>Disponible</span>
          </label>
          <label class="inline-flex items-center gap-2">
            <input type="checkbox" v-model="form.visibilidad" class="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
            <span>Visible</span>
          </label>
        </div>
      </div>
    </section>

    <!-- Categorías / Marca -->
    <section class="bg-white border rounded-xl p-5 shadow-sm">
      <h2 class="text-lg font-semibold text-slate-800 mb-3">Taxonomías</h2>
      <div class="grid sm:grid-cols-2 gap-x-4 gap-y-2">
        <div class="sm:col-span-2">
          <CategorySelector v-model="form.categorias" label="Categorías" />
        </div>
        
        <div>
          <label class="block text-xs font-medium text-slate-600 mb-1">Marca</label>
          <div class="flex gap-2">
            <select v-model="form.marca" class="h-10 w-full rounded-md border border-slate-300 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 flex-1">
              <option :value="null">Sin marca</option>
              <option v-for="m in marcas" :key="m.id" :value="m.id">{{ m.nombre }}</option>
            </select>
            <button type="button" @click="showMarcaModal = true" class="inline-flex items-center gap-2 border border-slate-300 hover:bg-slate-50 text-slate-800 px-3 py-2 rounded-md text-sm">Gestionar</button>
          </div>
          <p v-if="errs.marca" class="mt-1 text-xs text-rose-600">{{ errs.marca }}</p>
        </div>
      </div>
    </section>

    <!-- Atributos -->
    <section class="bg-white border rounded-xl p-5 shadow-sm">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-slate-800 mb-3">Atributos</h2>
        <button type="button" @click="showAttrModal = true" class="inline-flex items-center gap-2 border border-slate-300 hover:bg-slate-50 text-slate-800 px-3 py-2 rounded-md text-sm">Gestionar</button>
      </div>
      <select v-model="form.atributos" multiple class="h-10 w-full rounded-md border border-slate-300 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 h-32">
        <option v-for="a in atributos" :key="a.id" :value="a.id">
          {{ nombreAtributo(a) }} — {{ a.valor }}
        </option>
      </select>
    </section>

    <!-- Imágenes -->
    <section class="bg-white border rounded-xl p-5 shadow-sm">
      <h2 class="text-lg font-semibold text-slate-800 mb-3">Imágenes</h2>

      <div class="grid lg:grid-cols-3 gap-6">
        <!-- Principal -->
        <div class="lg:col-span-1">
          <label class="block text-xs font-medium text-slate-600 mb-1">Imagen principal</label>
          <div class="flex items-start gap-4">
            <label class="inline-flex items-center px-3 py-2 rounded border border-slate-300 hover:bg-slate-50 cursor-pointer">
              <input type="file" class="hidden" @change="onImagenChange" />
              Subir archivo
            </label>
            <div v-if="form.imagen_principal_url" class="border rounded-lg overflow-hidden w-32 h-32 bg-white">
              <img :src="form.imagen_principal_url" class="object-cover w-full h-full" />
            </div>
          </div>
        </div>

        <!-- Galería -->
        <div class="lg:col-span-2">
          <div class="flex items-center justify-between">
            <label class="block text-xs font-medium text-slate-600 mb-1">Galería</label>
            <label class="inline-flex items-center px-3 py-2 rounded border border-slate-300 hover:bg-slate-50 cursor-pointer">
              <input type="file" class="hidden" multiple @change="subirGaleria" />
              Añadir a galería
            </label>
          </div>

          <div class="mt-3 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            <div v-for="img in galeria" :key="img.id" class="group relative border rounded-lg overflow-hidden bg-white">
              <img :src="img.imagen" class="object-cover w-full h-28" />
              <button
                type="button"
                class="absolute top-2 right-2 px-2 py-1 text-xs rounded bg-rose-600 text-white opacity-90 hover:opacity-100"
                @click="eliminarImagen(img.id)"
              >
                Eliminar
              </button>
            </div>
            <div v-if="!galeria.length" class="text-sm text-slate-500 col-span-full">
              Aún no hay imágenes en la galería.
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Precios escalonados -->
    <section class="bg-white border rounded-xl p-5 shadow-sm">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-slate-800 mb-3">Precios escalonados</h2>
        <button type="button" @click="addTier" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm">Añadir precio</button>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-slate-50 border-b">
            <tr>
              <th class="text-left font-semibold px-3 py-2">Cantidad mínima</th>
              <th class="text-left font-semibold px-3 py-2">Precio unitario</th>
              <th class="text-right font-semibold px-3 py-2 w-20"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(tier, index) in preciosEscalonados" :key="tier.id || index" class="border-b last:border-0">
              <td class="px-3 py-2">
                <input type="number" v-model.number="tier.cantidad_minima" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 w-40 text-right" />
              </td>
              <td class="px-3 py-2">
                <input type="number" step="0.01" v-model.number="tier.precio_unitario" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 w-48 text-right" />
              </td>
              <td class="px-3 py-2 text-right">
                <button type="button" @click="removeTier(index)" class="inline-flex items-center gap-2 bg-rose-600 hover:bg-rose-700 text-white px-3 py-2 rounded-md text-sm">Quitar</button>
              </td>
            </tr>
            <tr v-if="!preciosEscalonados.length">
              <td colspan="3" class="px-3 py-4 text-center text-slate-500">Sin reglas de precio aún.</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="errs.precios_escalonados" class="mt-1 text-xs text-rose-600 mt-2">{{ errs.precios_escalonados }}</p>
    </section>

    <!-- Barra de acciones -->
    <div class="sticky bottom-0 bg-white/95 backdrop-blur border-t p-3">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="text-sm text-slate-600">
          <span class="mr-3">Precio: <span class="font-medium text-slate-800">${{ Number(form.precio_normal||0).toFixed(2) }}</span></span>
          <span class="mr-3">Stock: <span class="font-medium text-slate-800">{{ form.stock }}</span></span>
          <span>Estado: <span class="font-medium capitalize text-slate-800">{{ form.estado }}</span></span>
        </div>
        <div class="flex items-center gap-2">
          <RouterLink to="/admin/productos" class="inline-flex items-center gap-2 border border-slate-300 hover:bg-slate-50 text-slate-800 px-3 py-2 rounded-md text-sm">Cancelar</RouterLink>
          <button type="button" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm" :disabled="loading" @click="guardar">
            <span v-if="!loading">Guardar cambios</span>
            <span v-else>Guardando…</span>
          </button>
        </div>
      </div>
    </div>

    <!-- MODALES -->
    <div v-if="showMarcaModal" class="fixed inset-0 bg-black/40 z-50 grid place-items-center p-4" @click.self="showMarcaModal=false">
      <div class="w-full max-w-3xl bg-white rounded-xl shadow-xl p-5">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-semibold text-slate-800">Marcas</h3>
          <button class="text-slate-500 hover:text-slate-700" @click="showMarcaModal=false">✕</button>
        </div>
        <div class="space-y-2">
          <div v-for="m in marcas" :key="m.id" class="flex items-center gap-2">
            <input v-model="m.nombre" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 flex-1" />
            <button type="button" @click="guardarMarca(m)" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm">Guardar</button>
            <button type="button" @click="eliminarMarca(m.id)" class="inline-flex items-center gap-2 bg-rose-600 hover:bg-rose-700 text-white px-3 py-2 rounded-md text-sm">Eliminar</button>
          </div>
          <div class="flex items-center gap-2 pt-2 border-t">
            <input v-model="nuevaMarca" placeholder="Nueva marca" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 flex-1" />
            <button type="button" @click="agregarMarca" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm">Agregar</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAttrModal" class="fixed inset-0 bg-black/40 z-50 grid place-items-center p-4" @click.self="showAttrModal=false">
      <div class="w-full max-w-3xl bg-white rounded-xl shadow-xl p-5">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-semibold text-slate-800">Atributos</h3>
          <button class="text-slate-500 hover:text-slate-700" @click="showAttrModal=false">✕</button>
        </div>

        <div class="space-y-3">
          <div v-for="a in atributos" :key="a.id" class="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <select v-model="a.atributo_id" class="h-10 w-full rounded-md border border-slate-300 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option v-for="b in atributosBase" :key="b.id" :value="b.id">{{ b.nombre }}</option>
            </select>
            <input v-model="a.valor" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Valor" />
            <div class="flex gap-2">
              <button type="button" @click="guardarValor(a)" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm flex-1">Guardar</button>
              <button type="button" @click="eliminarValor(a.id)" class="inline-flex items-center gap-2 bg-rose-600 hover:bg-rose-700 text-white px-3 py-2 rounded-md text-sm flex-1">Eliminar</button>
            </div>
          </div>

          <div class="pt-3 border-t space-y-3">
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <select v-model="nuevoValor.atributo_id" class="h-10 w-full rounded-md border border-slate-300 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option v-for="b in atributosBase" :key="b.id" :value="b.id">{{ b.nombre }}</option>
              </select>
              <input v-model="nuevoValor.valor" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Valor" />
              <button type="button" @click="agregarValor" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm">Agregar valor</button>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <input v-model="nuevoAtributo" class="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:col-span-2" placeholder="Nuevo atributo (nombre)" />
              <button type="button" @click="agregarAtributo" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm">Agregar atributo</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import api from '@/axios'
import { useProductoStore } from '@/stores/productos'
import * as yup from 'yup'
import CategorySelector from '@/components/CategorySelector.vue'

defineOptions({ name: 'EditarProducto' })

const route = useRoute()
const router = useRouter()
const id = route.params.id

const toasts = ref([])
const toast = (type, msg, timeout = 2500) => {
  const id = Date.now() + Math.random()
  toasts.value.push({ id, type, msg })
  setTimeout(() => { toasts.value = toasts.value.filter(t => t.id !== id) }, timeout)
}

const form = reactive({
  nombre: '',
  descripcion_corta: '',
  descripcion_larga: '',
  precio_normal: 0,
  precio_rebajado: null,
  sku: '',
  disponible: false,
  estado_inventario: 'en_existencia',
  visibilidad: true,
  estado: 'borrador',
  categorias: [],
  marca: null,
  atributos: [],
  stock: 0,
  imagen_principal_url: null
})
const errs = reactive({})

const imagenPrincipal = ref(null)
const galeria = ref([])
const marcas = ref([])
const atributos = ref([])
const atributosBase = ref([])
const preciosEscalonados = ref([])

const showMarcaModal = ref(false)
const showAttrModal = ref(false)
const nuevaMarca = ref('')
const nuevoValor = reactive({ atributo_id: null, valor: '' })
const nuevoAtributo = ref('')
const loading = ref(false)
const isInitializing = ref(true)
const productoStore = useProductoStore()

const schema = yup.object({
  nombre: yup.string().trim().required('El nombre es obligatorio').max(160, 'Máx 160 caracteres'),
  descripcion_corta: yup.string().trim().max(300, 'Máx 300 caracteres').nullable(),
  descripcion_larga: yup.string().trim().nullable(),
  precio_normal: yup.number().typeError('Precio normal inválido').required('Precio normal es obligatorio').moreThan(0, 'Debe ser > 0'),
  precio_rebajado: yup.number().nullable().transform(v => (v === '' || isNaN(v) ? null : v))
    .min(0, 'No puede ser negativo')
    .test('lte-normal', 'El rebajado no puede exceder el precio normal',
      function (val) { if (val == null) return true; return val <= this.parent.precio_normal }),
  sku: yup.string().trim().max(60, 'Máx 60 caracteres').nullable(),
  stock: yup.number().typeError('Stock inválido').min(0, 'No puede ser negativo').integer('Debe ser entero').required('Stock es obligatorio'),
  estado_inventario: yup.mixed().oneOf(['en_existencia', 'agotado'], 'Valor inválido').required(),
  estado: yup.mixed().oneOf(['borrador', 'publicado'], 'Valor inválido').required(),
  categorias: yup.array(yup.number()).optional(),
  marca: yup.number().nullable().optional(),
  atributos: yup.array(yup.number()).optional(),
})

onMounted(async () => {
  await fetchOpciones()
  await fetchProducto()
  isInitializing.value = false
})

watch(preciosEscalonados, val => {
  if (productoStore.cache[id]) {
    productoStore.cache[id].precios_escalonados = val
  }
}, { deep: true })


const unwrap = (payload) => {
  if (Array.isArray(payload?.results)) return payload.results
  if (Array.isArray(payload)) return payload
  return []
}

async function fetchOpciones() {
  const [marcaRes, attrRes, baseRes] = await Promise.all([
    api.get('marcas/'),
    api.get('atributos/'),
    api.get('atributos-base/')
  ])
  marcas.value = unwrap(marcaRes.data)
  const unwrappedAttr = unwrap(attrRes.data)
  atributos.value = unwrappedAttr.map(v => ({ ...v, atributo_id: v.atributo.id }))
  atributosBase.value = unwrap(baseRes.data)
}

async function fetchProducto() {
  try {
    const data = await productoStore.get(id)
    if (data) {
      Object.assign(form, data)
      form.imagen_principal_url = data.imagen_principal
      form.categorias = data.categorias || []
      form.atributos = data.atributos || []
      galeria.value = data.galeria || []
      preciosEscalonados.value = data.precios_escalonados || []
    } else {
      console.error('Product not found')
    }
  } catch (error) {
    console.error('Error in fetchProducto:', error)
  }
}

function onImagenChange(e) {
  imagenPrincipal.value = e.target.files[0]
}

async function subirGaleria(e) {
  const files = e.target.files
  for (const file of files) {
    const fd = new FormData()
    fd.append('imagen', file)
    const { data } = await api.post(`productos/${id}/galeria/`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    galeria.value.push(data)
  }
  e.target.value = ''
}

async function eliminarImagen(imgId) {
  await api.delete(`galeria/${imgId}/`)
  galeria.value = galeria.value.filter(i => i.id !== imgId)
}

function addTier() {
  preciosEscalonados.value.push({ id: null, cantidad_minima: 0, precio_unitario: 0 })
}
function removeTier(index) {
  preciosEscalonados.value.splice(index, 1)
}

async function guardar() {
  Object.keys(errs).forEach(k => delete errs[k])

  if (preciosEscalonados.value.length) {
    const cantidades = preciosEscalonados.value.map(t => Number(t.cantidad_minima))
    const precios = preciosEscalonados.value.map(t => Number(t.precio_unitario))
    const hayDuplicados = new Set(cantidades).size !== cantidades.length
    const invalidos = cantidades.some(c => isNaN(c) || c <= 0) || precios.some(p => isNaN(p) || p <= 0)
    if (hayDuplicados) errs.precios_escalonados = 'Cantidades mínimas duplicadas.'
    if (invalidos) errs.precios_escalonados = (errs.precios_escalonados ? errs.precios_escalonados + ' ' : '') + 'Usa valores > 0.'
    if (errs.precios_escalonados) {
      toast('error', 'Corrige los precios escalonados.')
      return
    }
  }

  try {
    await schema.validate(form, { abortEarly: false })
  } catch (e) {
    if (e.inner?.length) {
      e.inner.forEach(err => { if (!errs[err.path]) errs[err.path] = err.message })
    } else if (e.message && e.path) {
      errs[e.path] = e.message
    }
    toast('error', 'Revisa los campos marcados.')
    return
  }

  const fd = new FormData()
  fd.append('nombre', form.nombre)
  fd.append('descripcion_corta', form.descripcion_corta || '')
  fd.append('descripcion_larga', form.descripcion_larga || '')
  fd.append('precio_normal', form.precio_normal)
  if (form.precio_rebajado !== null && form.precio_rebajado !== '') {
    fd.append('precio_rebajado', form.precio_rebajado)
  }
  fd.append('sku', form.sku || '')
  fd.append('disponible', form.disponible)
  fd.append('estado_inventario', form.estado_inventario)
  fd.append('visibilidad', form.visibilidad)
  fd.append('estado', form.estado)
  form.categorias.forEach(c => fd.append('categorias', c))
  if (form.marca) fd.append('marca', form.marca)
  form.atributos.forEach(a => fd.append('atributos', a))
  fd.append('stock', form.stock)
  fd.append('precios_escalonados', JSON.stringify(preciosEscalonados.value))
  if (imagenPrincipal.value) {
    fd.append('imagen_principal', imagenPrincipal.value)
  }

  loading.value = true
  try {
    const { data } = await api.put(`productos/${id}/`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    productoStore.cache[id] = data
    toast('success', 'Producto actualizado correctamente.')
    setTimeout(() => router.push('/admin/productos'), 600)
  } catch (err) {
    console.error(err)
    toast('error', 'Error al guardar. Intenta de nuevo.')
  } finally {
    loading.value = false
  }
}

function slugify(str) {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
}
function nombreAtributo(a) {
  const base = atributosBase.value.find(b => b.id === a.atributo_id || b.id === a.atributo?.id)
  return base ? base.nombre : ''
}

async function agregarMarca() {
  if (!nuevaMarca.value) return
  const { data } = await api.post('marcas/', { nombre: nuevaMarca.value })
  marcas.value.push(data)
  nuevaMarca.value = ''
}
async function guardarMarca(m) {
  await api.put(`marcas/${m.id}/`, { nombre: m.nombre })
}
async function eliminarMarca(id) {
  await api.delete(`marcas/${id}/`)
  marcas.value = marcas.value.filter(m => m.id !== id)
  if (form.marca === id) form.marca = null
}

async function agregarAtributo() {
  if (!nuevoAtributo.value) return
  const { data } = await api.post('atributos-base/', { nombre: nuevoAtributo.value })
  atributosBase.value.push(data)
  nuevoAtributo.value = ''
}
async function agregarValor() {
  if (!nuevoValor.atributo_id || !nuevoValor.valor) return
  const { data } = await api.post('atributos/', {
    atributo_id: nuevoValor.atributo_id,
    valor: nuevoValor.valor
  })
  data.atributo_id = data.atributo.id
  atributos.value.push(data)
  nuevoValor.atributo_id = null
  nuevoValor.valor = ''
}
async function guardarValor(v) {
  await api.put(`atributos/${v.id}/`, {
    atributo_id: v.atributo_id,
    valor: v.valor
  })
}
async function eliminarValor(id) {
  await api.delete(`atributos/${id}/`)
  atributos.value = atributos.value.filter(a => a.id !== id)
  form.atributos = form.atributos.filter(a => a !== id)
}
</script>