<template>
  <div class="max-w-2xl mx-auto p-6 bg-white rounded shadow">
    <h2 class="text-2xl font-bold mb-6">Crear producto completo</h2>

    <form @submit.prevent="crearProducto" class="space-y-4">
      <!-- Nombre -->
      <InputText v-model="producto.nombre" label="Nombre *" required />

      <!-- Descripciones -->
      <InputTextarea v-model="producto.descripcion_corta" label="Descripción corta" />
      <InputTextarea v-model="producto.descripcion_larga" label="Descripción larga (HTML permitido)" />

      <!-- Precios -->
      <InputNumber v-model="producto.precio_normal" label="Precio normal (MXN) *" prop="precio_normal" />
      <InputNumber v-model="producto.precio_rebajado" label="Precio rebajado (MXN)" />

      <!-- SKU -->
      <InputText v-model="producto.sku" label="SKU" />

      <!-- Imagen principal -->
      <ImageUpload
        label="Imagen principal"
        @cambio="onImagenPrincipal"
      />

      <!-- Galería -->
      <ImageUpload
        label="Galería de imágenes"
        :multiple="true"
        @cambio="onGaleria"
      />

      <!-- Stock -->
      <InputNumber v-model="producto.stock" label="Stock" />

      <!-- Estado inventario -->
      <div>
  <InputLabel label="Estado de inventario" />
  <div class="px-3 py-2 rounded bg-gray-100 inline-block">
    {{ estadoInventario }}
  </div>
</div>

      <!-- Disponible -->
      <SwitchInput v-model="producto.disponible" label="Disponible" />

      <!-- Visibilidad -->
      <SwitchInput v-model="producto.visibilidad" label="Visible al público" />

      <!-- Estado publicación -->
      <SelectInput v-model="producto.estado" label="Estado" :options="['borrador', 'publicado']" />

      <!-- Categoría principal (FK) -->
      <SelectInput
        v-model="producto.categoria"
        label="Categoría (principal)"
        :options="categorias"
        option-label="nombre"
        option-value="id"
      />

      <!-- Subcategorías / categorías extra (M2M) -->
      <MultiCheckbox
        v-model="producto.categorias"         
        label="Subcategorías / categorías extra"
        :options="categorias"                 
        option-label="nombre"
        option-value="id"
      />

      <!-- Marca -->
      <div class="flex items-center gap-2">
        <SelectInput
          v-model="producto.marca"
          label="Marca"
          :options="marcas"
          option-label="nombre"
          option-value="id"
        />
        <button type="button" @click="abrirModalMarca = true" class="text-blue-600 underline">+ Nueva</button>
      </div>

      <!-- Atributos -->
      <div class="flex items-center gap-2">
        <MultiCheckbox
          v-model="producto.atributos"
          label="Atributos"
          :options="opcionesAtributos"
          option-label="label"
          option-value="id"
        />
        <button type="button" @click="abrirModalAtributo = true" class="text-blue-600 underline">+ Nuevo</button>
      </div>

      <!-- Precios escalonados -->
      <EscalonadoInput v-model="producto.precios_escalonados" />

      <button class="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded">
        Guardar producto
      </button>
    </form>

    <p v-if="mensaje" class="mt-4 text-green-600">{{ mensaje }}</p>
  </div>
  <ModalInput v-model:visible="abrirModalCategoria" label="Nueva categoría" @save="crearCategoria" />
  <ModalInput v-model:visible="abrirModalMarca" label="Nueva marca" @save="crearMarca" />
  <ModalAtributo v-model:visible="abrirModalAtributo" label="Nuevo atributo" @save="crearAtributo" />

</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import api from '../axios'
import { useRouter } from 'vue-router'
import InputText from '../inputs/InputText.vue'
import InputTextarea from '../inputs/InputTextarea.vue'
import InputNumber from '../inputs/InputNumber.vue'
import InputLabel from '../inputs/InputLabel.vue'
import SelectInput from '../inputs/SelectInput.vue'
import SwitchInput from '../inputs/SwitchInput.vue'
import ImageUpload from '../inputs/ImageUpload.vue'
import MultiCheckbox from '../inputs/MultiCheckbox.vue'
//import MultiSelect from '../inputs/MultiSelect.vue'
import EscalonadoInput from '../inputs/EscalonadoInput.vue'
import ModalInput from '../inputs/ModalInput.vue'
import ModalAtributo from '../inputs/ModalAtributo.vue'
import { postMultipart } from '../api/api-multipart'



// Devuelve un File o null desde distintos formatos comunes de uploaders
const toFile = (x) => {
  if (!x) return null
  const FileCtor = (typeof window !== 'undefined' && window.File) ? window.File : null
  if (FileCtor && x instanceof FileCtor) return x
  if (FileCtor && x?.file instanceof FileCtor) return x.file   // muchos componentes emiten { file }
  if (FileCtor && x?.raw  instanceof FileCtor) return x.raw    // otros emiten { raw }
  return null
}

const onImagenPrincipal = (e) => {
  // algunos uploaders envían un objeto, otros un array
  const first = Array.isArray(e) ? e[0] : e
  producto.imagen_principal = toFile(first)
}

const onGaleria = (e) => {
  const list = Array.isArray(e) ? e : [e]
  producto.galeria = list.map(toFile).filter(Boolean)
}


const router = useRouter()
const producto = reactive({
  nombre: '', descripcion_corta: '', descripcion_larga: '',
  precio_normal: 0, precio_rebajado: null, sku: '', imagen_principal: null,
  galeria: [], stock: 0, estado_inventario: 'agotado', disponible: true,
  visibilidad: true, estado: 'borrador', categoria: null, marca: null,
  atributos: [], precios_escalonados: [],categorias: [],
})

const estadoInventario = computed(() =>
  (producto.stock > 0 ? 'en_existencia' : 'agotado')
)


const categorias = ref([])
const marcas = ref([])
const atributos = ref([])
const atributosBase = ref([])
const mensaje = ref('')
const abrirModalCategoria = ref(false)
const abrirModalMarca = ref(false)
const abrirModalAtributo = ref(false)

const opcionesAtributos = computed(() =>
  (Array.isArray(atributos.value) ? atributos.value : [])
    .filter(Boolean)
    .map(a => ({ ...a, label: `${a?.atributo?.nombre ?? 'Atributo'}: ${a?.valor ?? ''}` }))
)


const crearCategoria = async ({ nombre, parentId = null }) => {
  try {
    const payload = parentId ? { nombre, parent: parentId } : { nombre }
    const res = await api.post('categorias/', payload)
    categorias.value.push(res.data)
  } catch (e) {
    console.error('Error creando categoría', e)
    console.log('Detalles del error:', e.response?.data)
  }
}

const crearMarca = async (nombre) => {
  try {
    const res = await api.post('marcas/', { nombre })
    marcas.value.push(res.data)
  } catch (e) {
    console.error('Error creando marca', e)
  }
}

const crearAtributo = async ({ nombre, valor }) => {
  try {
    let base = atributosBase.value.find(a => a.nombre.toLowerCase() === nombre.toLowerCase())
    if (!base) {
      const { data } = await api.post('atributos-base/', { nombre })  // ← ruta correcta
      base = data
      atributosBase.value.push(base)
    }
    const res = await api.post('atributos/', { atributo_id: base.id, valor }) // ← ruta correcta
    atributos.value.push(res.data)
    producto.atributos.push(res.data.id)  // ← agrega ID numérico del ValorAtributo
  } catch (e) {
    console.error('Error creando atributo', e)
  }
}

onMounted(async () => {
  const [catRes, marcaRes, valoresRes, basesRes] = await Promise.all([
    api.get('categorias/'),
    api.get('marcas/'),
    api.get('atributos/'),       // ← ValorAtributo (NO valores-atributo)
    api.get('atributos-base/'),  // ← Atributo base
  ])
  // helper para paginación DRF
  const unpage = (d) => Array.isArray(d) ? d : (d && Array.isArray(d.results) ? d.results : [])

  categorias.value = unpage(catRes.data)   // si no está paginada, igual funciona
  marcas.value     = unpage(marcaRes.data)
  atributos.value  = unpage(valoresRes.data)
  atributosBase.value = unpage(basesRes.data)
})

const crearProducto = async () => {
  // Reglas previas
  const cantidades = (producto.precios_escalonados || []).map(t => t.cantidad_minima)
  if (new Set(cantidades).size !== cantidades.length) {
    alert('Cantidades mínimas duplicadas')
    return
  }

  // Normalización
  if (producto.categoria != null) producto.categoria = Number(producto.categoria) || null
  if (producto.marca != null)     producto.marca     = Number(producto.marca) || null

  producto.atributos  = (producto.atributos  || []).map(x => Number(x)).filter(Boolean)
  producto.categorias = (producto.categorias || []).map(x => Number(x)).filter(Boolean)

  producto.precio_normal   = producto.precio_normal   === '' ? null : Number(producto.precio_normal)
  producto.precio_rebajado = producto.precio_rebajado === '' ? null : Number(producto.precio_rebajado)
  producto.stock           = Number(producto.stock || 0)

  // Corrige rebajado sin watchers
  if (producto.precio_rebajado != null && producto.precio_normal != null) {
    if (producto.precio_rebajado > producto.precio_normal) {
      producto.precio_rebajado = producto.precio_normal
    }
  }

  producto.precios_escalonados = (producto.precios_escalonados || []).map(t => ({
    cantidad_minima: Number(t.cantidad_minima),
    precio_unitario: Number(t.precio_unitario),
  }))

  // FormData
  const formData = new FormData()

  // Campos simples
  formData.append('nombre', producto.nombre ?? '')
  if (producto.descripcion_corta != null) formData.append('descripcion_corta', producto.descripcion_corta)
  if (producto.descripcion_larga != null) formData.append('descripcion_larga', producto.descripcion_larga)
  if (producto.precio_normal != null)     formData.append('precio_normal', String(producto.precio_normal))
  if (producto.precio_rebajado != null)   formData.append('precio_rebajado', String(producto.precio_rebajado))
  if (producto.sku != null)               formData.append('sku', producto.sku)
  if (producto.imagen_principal)          formData.append('imagen_principal', producto.imagen_principal)
  formData.append('disponible', String(!!producto.disponible))
  formData.append('visibilidad', String(!!producto.visibilidad))
  formData.append('estado', producto.estado || 'borrador')
  if (producto.categoria != null)         formData.append('categoria', String(producto.categoria))
  if (producto.marca != null)             formData.append('marca', String(producto.marca))
  formData.append('stock', String(producto.stock))

  // Derivado (calculado al momento para evitar bucles recursivos)
  formData.append('estado_inventario', producto.stock > 0 ? 'en_existencia' : 'agotado')

  // M2M
  for (const id of producto.categorias) formData.append('categorias', String(id))
  for (const id of producto.atributos)  formData.append('atributos',  String(id))

  // Galería
  for (const f of (producto.galeria || [])) formData.append('galeria', f)

  // Escalonados
  formData.append('precios_escalonados', JSON.stringify(producto.precios_escalonados || []))

  try {
    const { data } = await postMultipart('productos/', formData) // sin forzar Content-Type
    mensaje.value = 'Producto guardado correctamente'
    router.push('/productos')
  } catch (err) {
    console.error('❌ POST /productos error:', err?.response?.data || err)
    mensaje.value = 'Error al guardar producto'
  }
}

</script>
