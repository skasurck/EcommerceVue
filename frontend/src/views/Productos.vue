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
      <div
        v-for="producto in productos"
        :key="producto.id"
        class="relative bg-white border border-gray-200 rounded-lg shadow hover:shadow-xl transition duration-200 overflow-hidden"
      >
        <div v-if="producto.stock <= 0" class="absolute top-0 left-0 bg-red-600 text-white text-xs px-2 py-1">
          Agotado
        </div>
        <RouterLink :to="`/producto/${producto.id}`">
          <img
            :src="producto.miniatura_url || producto.imagen_principal || 'https://via.placeholder.com/150'"
            alt="Imagen del producto"
            class="ImagenProducto w-full h-48 object-cover hover:brightness-90 transition"
          />
        </RouterLink>
        <div class="p-4">
          <h2 class="text-lg font-bold">
            <RouterLink :to="`/producto/${producto.id}`" class="text-blue-700 hover:underline">
              {{ producto.nombre }}
            </RouterLink>
          </h2>
          <p class="text-blue-600 font-semibold">        
           <span v-if="producto.precio_rebajado">
              <span class="line-through mr-1 text-gray-500">
                ${{ Number(producto.precio_normal).toFixed(2) }}
              </span>
              ${{ Number(producto.precio_rebajado).toFixed(2) }}
            </span>
            <span v-else>
              ${{ Number(producto.precio_normal).toFixed(2) }}
            </span>
          </p>
          <p class="text-sm text-gray-500">{{ producto.descripcion_corta }}</p>
          <button
            v-if="producto.stock > 0"
            @click="agregar(producto)"
            class="mt-2 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded"
          >
            Agregar al carrito
          </button>
          <button
            v-else
            disabled
            class="mt-2 bg-gray-400 text-white px-3 py-1 rounded cursor-not-allowed"
          >
            Agotado
          </button>
        </div>
      </div>
    </div>

    <div class="mt-4 flex justify-center items-center gap-2">
      <button @click="cambiarPagina(pagination.page - 1)" :disabled="pagination.page === 1">Anterior</button>
      <span>Página {{ pagination.page }} de {{ pagination.totalPages }}</span>
      <button @click="cambiarPagina(pagination.page + 1)" :disabled="pagination.page === pagination.totalPages">Siguiente</button>
    </div>
  </div>
</template>

<script setup>
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
