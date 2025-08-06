<template>
  <div>
    <h2>Editar producto</h2>
    <form @submit.prevent="guardar">
      <div>
        <label>Nombre</label>
        <input v-model="form.nombre" />
      </div>
      <div>
        <label>Descripción corta</label>
        <textarea v-model="form.descripcion_corta"></textarea>
      </div>
      <div>
        <label>Descripción larga</label>
        <textarea v-model="form.descripcion_larga"></textarea>
      </div>
      <div>
        <label>Precio normal</label>
        <input type="number" step="0.01" v-model.number="form.precio_normal" />
      </div>
      <div>
        <label>Precio rebajado</label>
        <input type="number" step="0.01" v-model.number="form.precio_rebajado" />
      </div>
      <div>
        <label>SKU</label>
        <input v-model="form.sku" />
      </div>
      <div>
        <label>Stock</label>
        <input type="number" v-model.number="form.stock" />
      </div>
      <div>
        <label>Estado inventario</label>
        <select v-model="form.estado_inventario">
          <option value="en_existencia">En existencia</option>
          <option value="agotado">Agotado</option>
        </select>
      </div>
      <div>
        <label>Estado</label>
        <select v-model="form.estado">
          <option value="borrador">Borrador</option>
          <option value="publicado">Publicado</option>
        </select>
      </div>
      <div>
        <label>Categoria principal</label>
        <select v-model="form.categoria">
          <option :value="null">Sin categoría</option>
          <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
        </select>
      </div>
      <div>
        <label>Categorías</label>
        <select v-model="form.categorias" multiple>
          <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
        </select>
      </div>
      <div>
        <label>Marca</label>
        <select v-model="form.marca">
          <option :value="null">Sin marca</option>
          <option v-for="m in marcas" :key="m.id" :value="m.id">{{ m.nombre }}</option>
        </select>
      </div>
      <div>
        <label>Atributos</label>
        <select v-model="form.atributos" multiple>
          <option v-for="a in atributos" :key="a.id" :value="a.id">{{ a.atributo }} - {{ a.valor }}</option>
        </select>
      </div>
      <div>
        <label>
          <input type="checkbox" v-model="form.disponible" /> Disponible
        </label>
      </div>
      <div>
        <label>
          <input type="checkbox" v-model="form.visibilidad" /> Visible
        </label>
      </div>
      <div>
        <label>Imagen principal</label>
        <input type="file" @change="onImagenChange" />
        <div v-if="form.imagen_principal_url">
          <img :src="form.imagen_principal_url" width="100" />
        </div>
      </div>
      <div>
        <h3>Galería</h3>
        <div v-for="img in galeria" :key="img.id">
          <img :src="img.imagen" width="80" />
          <button type="button" @click="eliminarImagen(img.id)">Eliminar</button>
        </div>
        <input type="file" multiple @change="subirGaleria" />
      </div>
      <div>
        <h3>Precios escalonados</h3>
        <table>
          <tr v-for="(tier, index) in preciosEscalonados" :key="index">
            <td><input type="number" v-model.number="tier.cantidad_minima" /></td>
            <td><input type="number" step="0.01" v-model.number="tier.precio_unitario" /></td>
            <td><button type="button" @click="removeTier(index)">X</button></td>
          </tr>
        </table>
        <button type="button" @click="addTier">Añadir precio</button>
      </div>
      <button type="submit">Guardar</button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../axios'

defineOptions({ name: 'EditarProducto' })

const route = useRoute()
const router = useRouter()
const id = route.params.id

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
  categoria: null,
  categorias: [],
  marca: null,
  atributos: [],
  stock: 0,
  imagen_principal_url: null
})

const imagenPrincipal = ref(null)
const galeria = ref([])
const categorias = ref([])
const marcas = ref([])
const atributos = ref([])
const preciosEscalonados = ref([])

onMounted(async () => {
  await fetchOpciones()
  await fetchProducto()
})

async function fetchOpciones() {
  const [catRes, marcaRes, attrRes] = await Promise.all([
    api.get('categorias/'),
    api.get('marcas/'),
    api.get('atributos/')
  ])
  categorias.value = catRes.data
  marcas.value = marcaRes.data
  atributos.value = attrRes.data
}

async function fetchProducto() {
  const { data } = await api.get(`productos/${id}/`)
  Object.assign(form, data)
  form.imagen_principal_url = data.imagen_principal
  form.categorias = data.categorias || []
  form.atributos = data.atributos || []
  galeria.value = data.galeria || []
  preciosEscalonados.value = data.precios_escalonados || []
}

function onImagenChange(e) {
  imagenPrincipal.value = e.target.files[0]
}

async function subirGaleria(e) {
  const files = e.target.files
  for (const file of files) {
    const fd = new FormData()
    fd.append('imagen', file)
    await api.post(`productos/${id}/galeria/`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
  await fetchProducto()
}

async function eliminarImagen(imgId) {
  await api.delete(`galeria/${imgId}/`)
  await fetchProducto()
}

function addTier() {
  preciosEscalonados.value.push({ cantidad_minima: 0, precio_unitario: 0 })
}

function removeTier(index) {
  preciosEscalonados.value.splice(index, 1)
}

async function guardar() {
  const fd = new FormData()
  fd.append('nombre', form.nombre)
  fd.append('descripcion_corta', form.descripcion_corta || '')
  fd.append('descripcion_larga', form.descripcion_larga || '')
  fd.append('precio_normal', form.precio_normal)
  if (form.precio_rebajado !== null) {
    fd.append('precio_rebajado', form.precio_rebajado)
  }
  fd.append('sku', form.sku || '')
  fd.append('disponible', form.disponible)
  fd.append('estado_inventario', form.estado_inventario)
  fd.append('visibilidad', form.visibilidad)
  fd.append('estado', form.estado)
  if (form.categoria) fd.append('categoria', form.categoria)
  form.categorias.forEach(c => fd.append('categorias', c))
  if (form.marca) fd.append('marca', form.marca)
  form.atributos.forEach(a => fd.append('atributos', a))
  fd.append('stock', form.stock)
  preciosEscalonados.value.forEach(t =>
    fd.append('precios_escalonados', JSON.stringify(t))
  )
  if (imagenPrincipal.value) {
    fd.append('imagen_principal', imagenPrincipal.value)
  }

  await api.put(`productos/${id}/`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  alert('Producto actualizado')
  router.push('/admin/productos')
}
</script>

