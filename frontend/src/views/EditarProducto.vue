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
        <button type="button" @click="showCatModal = true">Gestionar</button>
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
        <button type="button" @click="showMarcaModal = true">Gestionar</button>
      </div>
      <div>
        <label>Atributos</label>
        <select v-model="form.atributos" multiple>
          <option v-for="a in atributos" :key="a.id" :value="a.id">{{ nombreAtributo(a) }} - {{ a.valor }}</option>
        </select>
        <button type="button" @click="showAttrModal = true">Gestionar</button>
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
      <button type="submit" :disabled="loading">Guardar</button>
      <span v-if="loading">Guardando...</span>
    </form>

    <!-- Modal Categorías -->
    <div v-if="showCatModal" class="modal">
      <div class="modal-content">
        <h3>Categorías</h3>
        <div v-for="c in categorias" :key="c.id">
          <input v-model="c.nombre" />
          <button type="button" @click="guardarCategoria(c)">Guardar</button>
          <button type="button" @click="eliminarCategoria(c.id)">Eliminar</button>
        </div>
        <input v-model="nuevaCategoria" placeholder="Nueva categoría" />
        <button type="button" @click="agregarCategoria">Agregar</button>
        <button type="button" @click="showCatModal = false">Cerrar</button>
      </div>
    </div>

    <!-- Modal Marcas -->
    <div v-if="showMarcaModal" class="modal">
      <div class="modal-content">
        <h3>Marcas</h3>
        <div v-for="m in marcas" :key="m.id">
          <input v-model="m.nombre" />
          <button type="button" @click="guardarMarca(m)">Guardar</button>
          <button type="button" @click="eliminarMarca(m.id)">Eliminar</button>
        </div>
        <input v-model="nuevaMarca" placeholder="Nueva marca" />
        <button type="button" @click="agregarMarca">Agregar</button>
        <button type="button" @click="showMarcaModal = false">Cerrar</button>
      </div>
    </div>

    <!-- Modal Atributos -->
    <div v-if="showAttrModal" class="modal">
      <div class="modal-content">
        <h3>Atributos</h3>
        <div v-for="a in atributos" :key="a.id">
          <select v-model="a.atributo_id">
            <option v-for="b in atributosBase" :key="b.id" :value="b.id">{{ b.nombre }}</option>
          </select>
          <input v-model="a.valor" />
          <button type="button" @click="guardarValor(a)">Guardar</button>
          <button type="button" @click="eliminarValor(a.id)">Eliminar</button>
        </div>
        <div>
          <select v-model="nuevoValor.atributo_id">
            <option v-for="b in atributosBase" :key="b.id" :value="b.id">{{ b.nombre }}</option>
          </select>
          <input v-model="nuevoValor.valor" placeholder="Valor" />
          <button type="button" @click="agregarValor">Agregar valor</button>
        </div>
        <div>
          <input v-model="nuevoAtributo" placeholder="Nuevo atributo" />
          <button type="button" @click="agregarAtributo">Agregar atributo</button>
        </div>
        <button type="button" @click="showAttrModal = false">Cerrar</button>
      </div>
    </div>
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
const atributosBase = ref([])
const preciosEscalonados = ref([])
const showCatModal = ref(false)
const showMarcaModal = ref(false)
const showAttrModal = ref(false)
const nuevaCategoria = ref('')
const nuevaMarca = ref('')
const nuevoValor = reactive({ atributo_id: null, valor: '' })
const nuevoAtributo = ref('')
const loading = ref(false)

onMounted(async () => {
  await fetchOpciones()
  await fetchProducto()
})

async function fetchOpciones() {
  const [catRes, marcaRes, attrRes, baseRes] = await Promise.all([
    api.get('categorias/'),
    api.get('marcas/'),
    api.get('atributos/'),
    api.get('atributos-base/')
  ])
  categorias.value = catRes.data
  marcas.value = marcaRes.data
  atributos.value = attrRes.data.map(v => ({ ...v, atributo_id: v.atributo.id }))
  atributosBase.value = baseRes.data
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
  preciosEscalonados.value.push({ cantidad_minima: 0, precio_unitario: 0 })
}

function removeTier(index) {
  preciosEscalonados.value.splice(index, 1)
}

async function guardar() {
  const cantidades = preciosEscalonados.value.map(t => t.cantidad_minima)
  if (new Set(cantidades).size !== cantidades.length) {
    alert('Cantidades mínimas duplicadas')
    return
  }

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

  loading.value = true
  try {
    await api.put(`productos/${id}/`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    alert('Producto actualizado')
    router.push('/admin/productos')
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

async function agregarCategoria() {
  if (!nuevaCategoria.value) return
  const slug = slugify(nuevaCategoria.value)
  const { data } = await api.post('categorias/', { nombre: nuevaCategoria.value, slug })
  categorias.value.push(data)
  nuevaCategoria.value = ''
}

async function guardarCategoria(cat) {
  const slug = slugify(cat.nombre)
  await api.put(`categorias/${cat.id}/`, { nombre: cat.nombre, slug })
}

async function eliminarCategoria(id) {
  await api.delete(`categorias/${id}/`)
  categorias.value = categorias.value.filter(c => c.id !== id)
  if (form.categoria === id) form.categoria = null
  form.categorias = form.categorias.filter(c => c !== id)
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

