<template>
  <div class="p-4 max-w-7xl mx-auto">
    <h1 class="text-2xl font-bold mb-6 text-center text-gray-800">🛍️ Productos Disponibles</h1>

    <div class="mb-4 flex gap-2">
      <input v-model="filtros.search" @input="fetchProductos" placeholder="Buscar..." />
      <select v-model="filtros.categoria" @change="fetchProductos">
        <option value="">Todas</option>
        <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
      </select>
    </div>

    <div v-if="productos.length === 0" class="text-center text-gray-500">Cargando productos...</div>

    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <ProductCard
        v-for="producto in productos"
        :key="producto.id"
        :producto="producto"
      />
    </div>

    <div class="mt-4 flex justify-center items-center gap-2">
      <button @click="cambiarPagina(pagination.page - 1)" :disabled="pagination.page === 1">Anterior</button>
      <span>Página {{ pagination.page }} de {{ pagination.totalPages }}</span>
      <button @click="cambiarPagina(pagination.page + 1)" :disabled="pagination.page === pagination.totalPages">Siguiente</button>
    </div>
  </div>
</template>

<script setup>
import ProductCard from '@/components/ProductCard.vue'
import { ref, reactive, onMounted } from 'vue'
import { obtenerProductos } from '../services/api.js'
import api from '../axios'
import { RouterLink } from 'vue-router'
import { useCarritoStore } from '../stores/carrito'
defineOptions({ name: 'ProductosView' })

const productos = ref([])
const categorias = ref([])
const filtros = reactive({ search: '', categoria: '' })
const pagination = reactive({ page: 1, totalPages: 1, pageSize: 10 })
const carrito = useCarritoStore()

const agregar = async (producto) => {
  await carrito.agregar(producto)
  producto.stock = Math.max(producto.stock - 1, 0)
}

async function fetchCategorias() {
  const res = await api.get('categorias/')
  categorias.value = res.data
}

async function fetchProductos() {
  const params = { page: pagination.page, page_size: pagination.pageSize }
  if (filtros.search) params.search = filtros.search
  if (filtros.categoria) params.categoria = filtros.categoria
  const res = await obtenerProductos(params)
  productos.value = res.data.results
  const total = res.data.count
  pagination.totalPages = Math.ceil(total / pagination.pageSize) || 1
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

<style scoped>
h1 {
  color: #333;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  padding: 8px;
  border-bottom: 1px solid #ccc;
}
li:last-child {
  border-bottom: none;
}
.ImagenProducto {
  width: 250px;
  height: auto;
  object-fit: cover;
}
</style>
