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
      <ImageUpload label="Imagen principal" @cambio="e => producto.imagen_principal = e" />

      <!-- Galería -->
      <ImageUpload label="Galería de imágenes" :multiple="true" @cambio="e => producto.galeria = e" />

      <!-- Stock -->
      <InputNumber v-model="producto.stock" label="Stock" />

      <!-- Estado inventario -->
      <SelectInput v-model="producto.estado_inventario" label="Estado de inventario" :options="['en_existencia', 'agotado']" />

      <!-- Disponible -->
      <SwitchInput v-model="producto.disponible" label="Disponible" />

      <!-- Visibilidad -->
      <SwitchInput v-model="producto.visibilidad" label="Visible al público" />

      <!-- Estado publicación -->
      <SelectInput v-model="producto.estado" label="Estado" :options="['borrador', 'publicado']" />

      <!-- Categoría -->
      <div class="flex items-center gap-2">
        <SelectInput
          v-model="producto.categoria"
          label="Categoría"
          :options="categorias"
          option-label="nombre"
          option-value="id"
        />
        <button type="button" @click="abrirModalCategoria = true" class="text-blue-600 underline">+ Nueva</button>
      </div>

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
import SelectInput from '../inputs/SelectInput.vue'
import SwitchInput from '../inputs/SwitchInput.vue'
import ImageUpload from '../inputs/ImageUpload.vue'
import MultiCheckbox from '../inputs/MultiCheckbox.vue'
import EscalonadoInput from '../inputs/EscalonadoInput.vue'
import ModalInput from '../inputs/ModalInput.vue'
import ModalAtributo from '../inputs/ModalAtributo.vue'

const router = useRouter()
const producto = reactive({
  nombre: '', descripcion_corta: '', descripcion_larga: '',
  precio_normal: 0, precio_rebajado: null, sku: '', imagen_principal: null,
  galeria: [], stock: 0, estado_inventario: 'agotado', disponible: true,
  visibilidad: true, estado: 'borrador', categoria: null, marca: null,
  atributos: [], precios_escalonados: []
})

watch(
  () => producto.stock,
  (nuevoStock) => {
    producto.estado_inventario = nuevoStock > 0 ? 'en_existencia' : 'agotado'
  }
)

watch(
  () => producto.precio_normal,
  (nuevo) => {
    if (producto.precio_rebajado !== null && producto.precio_rebajado > nuevo) {
      producto.precio_rebajado = nuevo
    }
  }
)

watch(
  () => producto.precio_rebajado,
  (nuevo) => {
    if (nuevo !== null && nuevo > producto.precio_normal) {
      producto.precio_rebajado = producto.precio_normal
    }
  }
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
  atributos.value.map(a => ({ ...a, label: `${a.atributo.nombre}: ${a.valor}` }))
)

const crearCategoria = async (nombre) => {
  try {
    const res = await api.post('categorias/', { nombre: nombre }) // <-- así debe ir
    categorias.value.push(res.data)
  } catch (e) {
    console.error('Error creando categoría', e)
    console.log('Detalles del error:', e.response?.data) // Esto te muestra el error que lanza el serializer
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
    let atributo = atributosBase.value.find(
      a => a.nombre.toLowerCase() === nombre.toLowerCase()
    )
    if (!atributo) {
      const { data } = await api.post('atributos-base/', { nombre })
      atributo = data
      atributosBase.value.push(data)
    }
    const res = await api.post('atributos/', { atributo_id: atributo.id, valor })
    atributos.value.push(res.data)
    producto.atributos.push(res.data.id)
  } catch (e) {
    console.error('Error creando atributo', e)
  }
}

onMounted(async () => {
  const [catRes, marcaRes, attrRes, baseRes] = await Promise.all([
    api.get('categorias/'),
    api.get('marcas/'),
    api.get('atributos/'),
    api.get('atributos-base/')
  ])
  categorias.value = catRes.data
  marcas.value = marcaRes.data
  atributos.value = attrRes.data
  atributosBase.value = baseRes.data
})

const crearProducto = async () => {
  const cantidades = producto.precios_escalonados.map(t => t.cantidad_minima)
  if (new Set(cantidades).size !== cantidades.length) {
    alert('Cantidades mínimas duplicadas')
    return
  }

  const formData = new FormData()
  Object.entries(producto).forEach(([k, v]) => {
    if (k === 'atributos') v.forEach(id => formData.append('atributos', id))
    else if (k === 'precios_escalonados') {
      formData.append('precios_escalonados', JSON.stringify(v))
    }
    else if (k === 'galeria') v.forEach(f => formData.append('galeria', f))
    else if (v !== null) formData.append(k, v)
  })
  try {
    await api.post('productos/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    mensaje.value = 'Producto guardado correctamente'
    router.push('/productos')
  } catch (err) {
    console.error(err)
    mensaje.value = 'Error al guardar producto'
  }
}
</script>

<style scoped>
h2 {
  color: #333;
}
input, textarea {
  transition: border-color 0.2s;
}
input:focus, textarea:focus {
  border-color: #3b82f6; /* Azul claro */
  outline: none;
}
.border-red-500 {
  border-color: #f87171; /* Rojo claro */
}
.border {
  border: 1px solid #e5e7eb; /* Gris claro */
}
.imagePrevi {
  max-width: 290px;
  height: auto;
}
</style>
<!-- This is a simple form to create a new product. It uses Vue's reactivity system to bind the form inputs to a `producto` object. When the form is submitted, it sends a POST request to the API to create the product. If successful, it displays a success message and resets the form. If there's an error, it logs the error and displays an error message. The form includes fields for name, description, price, and availability. -->