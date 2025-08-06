<template>
  <div>
    <h2>Gestión de productos</h2>

    <div>
      <input v-model="filtros.search" placeholder="Buscar..." @input="fetchProductos" />
      <select v-model="filtros.categoria" @change="fetchProductos">
        <option value="">Todas las categorías</option>
        <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
      </select>
      <select v-model="filtros.estado" @change="fetchProductos">
        <option value="">Todos</option>
        <option value="en_existencia">En existencia</option>
        <option value="agotado">Agotado</option>
      </select>
      <select v-model="filtros.marca" @change="fetchProductos">
        <option value="">Todas las marcas</option>
        <option v-for="m in marcas" :key="m.id" :value="m.id">{{ m.nombre }}</option>
      </select>
      <button @click="nuevoProducto">Añadir producto</button>
    </div>

    <table>
      <thead>
        <tr>
          <th>Imagen</th>
          <th>Nombre</th>
          <th>SKU</th>
          <th>Stock</th>
          <th>Precio</th>
          <th>Precio rebajado</th>
          <th>Categorías</th>
          <th>Fecha</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in productos" :key="p.id">
          <td><img v-if="p.miniatura_url" :src="p.miniatura_url" alt="" width="50" /></td>
          <td>
            <span v-if="editingId !== p.id">{{ p.nombre }}</span>
            <input v-else v-model="p.nombre" />
          </td>
          <td>
            <span v-if="editingId !== p.id">{{ p.sku }}</span>
            <input v-else v-model="p.sku" />
          </td>
          <td>
            <span v-if="editingId !== p.id">{{ p.stock }}</span>
            <input v-else type="number" v-model.number="p.stock" />
          </td>
          <td>
            <span v-if="editingId !== p.id">{{ p.precio_normal }}</span>
            <input v-else type="number" step="0.01" v-model.number="p.precio_normal" />
          </td>
          <td>
            <span v-if="editingId !== p.id">{{ p.precio_rebajado }}</span>
            <input v-else type="number" step="0.01" v-model.number="p.precio_rebajado" />
          </td>
          <td>
            <span v-if="editingId !== p.id">{{ categoriasNombres(p.categorias).join(', ') }}</span>
            <select v-else multiple v-model="p.categorias">
              <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
            </select>
          </td>
          <td>{{ new Date(p.fecha_creacion).toLocaleDateString() }}</td>
          <td>
            <div v-if="editingId === p.id">
              <button @click="guardar(p)">Guardar</button>
              <button @click="cancelar(p)">Cancelar</button>
            </div>
            <div v-else>
              <button @click="editar(p)">Edición rápida</button>
              <router-link :to="`/productos/editar/${p.id}`">Editar</router-link>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div>
      <button @click="cambiarPagina(pagination.page - 1)" :disabled="pagination.page === 1">Anterior</button>
      <span>Página {{ pagination.page }} de {{ pagination.totalPages }}</span>
      <button @click="cambiarPagina(pagination.page + 1)" :disabled="pagination.page === pagination.totalPages">Siguiente</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../axios'

defineOptions({ name: 'AdminProductos' })

const router = useRouter()
const route = useRoute()
const productos = ref([])
const categorias = ref([])
const marcas = ref([])
const filtros = reactive({ search: '', categoria: '', estado: '', marca: '' })
const pagination = reactive({ page: 1, totalPages: 1, pageSize: 10 })
const editingId = ref(null)
const cache = ref({})

function categoriasNombres(ids) {
  return ids.map(id => {
    const cat = categorias.value.find(c => c.id === id)
    return cat ? cat.nombre : id
  })
}

async function fetchFiltros() {
  const [catRes, marcaRes] = await Promise.all([
    api.get('categorias/'),
    api.get('marcas/')
  ])
  categorias.value = catRes.data
  marcas.value = marcaRes.data
}

async function fetchProductos() {
  const params = {
    page: pagination.page,
    page_size: pagination.pageSize
  }
  if (filtros.search) params.search = filtros.search
  if (filtros.categoria) params.categoria = filtros.categoria
  if (filtros.estado) params.estado_inventario = filtros.estado
  if (filtros.marca) params.marca = filtros.marca
  const res = await api.get('productos/', { params })
  productos.value = res.data.results
  const total = res.data.count
  pagination.totalPages = Math.ceil(total / pagination.pageSize) || 1
}

function cambiarPagina(page) {
  if (page < 1 || page > pagination.totalPages) return
  pagination.page = page
  fetchProductos()
}

function editar(p) {
  editingId.value = p.id
  cache.value = { ...p }
}

function cancelar(p) {
  Object.assign(p, cache.value)
  editingId.value = null
}

async function guardar(p) {
  const payload = {
    nombre: p.nombre,
    sku: p.sku,
    stock: p.stock,
    precio_normal: p.precio_normal,
    precio_rebajado: p.precio_rebajado,
    categorias: p.categorias
  }
  await api.patch(`productos/${p.id}/`, payload)
  editingId.value = null
  fetchProductos()
}

function nuevoProducto() {
  router.push('/nuevo-producto')
}

onMounted(async () => {
  await fetchFiltros()
  await fetchProductos()
  if (route.query.actualizado) {
    alert('Producto actualizado correctamente')
    router.replace({ query: {} })
  }
})
</script>
