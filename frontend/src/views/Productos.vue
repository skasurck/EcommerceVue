<template>
  <div class="p-4 max-w-7xl mx-auto">
    <h1 class="text-2xl font-bold mb-6 text-center text-gray-800">🛍️ Productos Disponibles</h1>

    <div class="mb-4 flex gap-2">
      <input
        v-model="filtros.search"
        @input="fetchProductos"
        placeholder="Buscar..."
        class="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <select
        v-model="filtros.categoria"
        @change="fetchProductos"
        class="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">Todas</option>
        <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
      </select>
    </div>

    <div v-if="loading" class="text-center text-gray-500">Cargando productos...</div>
    <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>
    <div v-else-if="productos.length === 0" class="text-center text-gray-500">No se encontraron productos.</div>

    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <ProductCard
        v-for="producto in productos"
        :key="producto.id"
        :producto="producto"
      />
    </div>

    <div class="mt-4 flex justify-center items-center gap-2">
      <button
        @click="cambiarPagina(pagination.page - 1)"
        :disabled="pagination.page === 1"
        class="px-3 py-1.5 rounded bg-blue-600 text-white disabled:opacity-50"
      >Anterior</button>
      <span>Página {{ pagination.page }} de {{ pagination.totalPages }}</span>
      <button
        @click="cambiarPagina(pagination.page + 1)"
        :disabled="pagination.page === pagination.totalPages"
        class="px-3 py-1.5 rounded bg-blue-600 text-white disabled:opacity-50"
      >Siguiente</button>
    </div>
  </div>
</template>

<script setup>
import ProductCard from '@/components/ProductCard.vue'
import { ref, reactive, onMounted } from 'vue'
import { obtenerProductos } from '../services/api.js'
import api from '../axios'
defineOptions({ name: 'ProductosView' })

const productos = ref([])
const categorias = ref([])
const filtros = reactive({ search: '', categoria: '' })
const pagination = reactive({ page: 1, totalPages: 1, pageSize: 10 })
const loading = ref(false)
const error = ref(null)
const unwrapList = (payload) => {
  if (Array.isArray(payload?.results)) return payload.results
  if (Array.isArray(payload)) return payload
  return []
}


async function fetchCategorias() {
  const res = await api.get('categorias/')
  categorias.value = unwrapList(res.data)
}

async function fetchProductos() {
  loading.value = true
  error.value = null
  try {
    const currentPage = pagination.page
    const params = { page: currentPage, page_size: pagination.pageSize }
    if (filtros.search) params.search = filtros.search
    if (filtros.categoria) params.categoria = filtros.categoria

    const res = await obtenerProductos(params)
    const raw = unwrapList(res.data)
    productos.value = raw

    const total = typeof res.data?.count === 'number' ? res.data.count : raw.length
    const totalPages = Math.max(1, Math.ceil(total / pagination.pageSize))
    if (currentPage > totalPages && total > 0) {
      pagination.page = totalPages
      await fetchProductos()
      return
    }
    pagination.totalPages = totalPages
  } catch (err) {
    console.error('Error cargando productos:', err)
    error.value = 'No se pudieron cargar los productos. Intenta nuevamente más tarde.'
    productos.value = []
    pagination.totalPages = 1
  } finally {
    loading.value = false
  }
}

function cambiarPagina(p) {
  if (p < 1 || p > pagination.totalPages) return
  pagination.page = p
  fetchProductos()
}

onMounted(async () => {
  await fetchCategorias()
  await fetchProductos()
})
</script>

