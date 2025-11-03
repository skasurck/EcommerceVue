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

    <div v-if="loading && productos.length > 0" class="text-center text-gray-500 py-4">Cargando más productos...</div>
    <div v-if="!loading && pagination.page >= pagination.totalPages" class="text-center text-gray-500 py-4">No hay más productos.</div>
  </div>
</template>

<script setup>
import ProductCard from '@/components/ProductCard.vue'
import { ref, reactive, onMounted, onUnmounted } from 'vue'
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

async function fetchProductos(append = false) {
  loading.value = true
  error.value = null
  try {
    if (!append) {
      pagination.page = 1
    }
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (filtros.search) params.search = filtros.search
    if (filtros.categoria) params.categoria = filtros.categoria

    const res = await obtenerProductos(params)
    const raw = unwrapList(res.data)

    if (append) {
      productos.value.push(...raw)
    } else {
      productos.value = raw
    }

    const total = typeof res.data?.count === 'number' ? res.data.count : raw.length
    pagination.totalPages = Math.max(1, Math.ceil(total / pagination.pageSize))
  } catch (err) {
    console.error('Error cargando productos:', err)
    error.value = 'No se pudieron cargar los productos. Intenta nuevamente más tarde.'
    if (!append) {
      productos.value = []
      pagination.totalPages = 1
    }
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  if (loading.value || pagination.page >= pagination.totalPages) return
  pagination.page++
  fetchProductos(true)
}

const handleScroll = () => {
  const { scrollTop, scrollHeight, clientHeight } = document.documentElement
  if (scrollTop + clientHeight >= scrollHeight - 5) { // 5px buffer
    loadMore()
  }
}

onMounted(async () => {
  await fetchCategorias()
  await fetchProductos()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

