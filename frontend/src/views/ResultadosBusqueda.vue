<template>
  <div class="w-full max-w-7xl mx-auto px-4 sm:px-6 py-6">
    <!-- Header -->
    <div class="mb-6">
      <p class="text-sm text-gray-500 mb-1">Resultados de búsqueda</p>
      <div class="flex items-end gap-3 flex-wrap">
        <h1 class="text-2xl font-bold text-gray-800">
          <span v-if="query">"{{ query }}"</span>
          <span v-else>Todos los productos</span>
        </h1>
        <span v-if="!loading && total !== null" class="text-sm text-gray-500 mb-0.5">
          {{ total }} {{ total === 1 ? 'resultado' : 'resultados' }}
        </span>
      </div>
    </div>

    <!-- Search bar -->
    <form @submit.prevent="submitSearch" class="mb-6 flex gap-2 max-w-xl">
      <input
        v-model="inputQ"
        type="search"
        placeholder="Buscar productos…"
        class="flex-1 border border-gray-300 rounded-l-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
      />
      <button
        type="submit"
        class="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-r-md transition flex items-center gap-1.5 font-medium"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-4.35-4.35m0 0A7.5 7.5 0 1 0 6.15 6.15a7.5 7.5 0 0 0 10.5 10.5Z"/>
        </svg>
        Buscar
      </button>
    </form>

    <!-- Loading skeleton -->
    <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      <div v-for="n in 10" :key="n" class="bg-white rounded-lg border border-gray-200 overflow-hidden animate-pulse">
        <div class="bg-gray-200 aspect-square w-full"></div>
        <div class="p-3 space-y-2">
          <div class="h-3 bg-gray-200 rounded w-3/4"></div>
          <div class="h-3 bg-gray-200 rounded w-1/2"></div>
          <div class="h-4 bg-gray-200 rounded w-1/3 mt-2"></div>
        </div>
      </div>
    </div>

    <!-- Sin resultados -->
    <div v-else-if="!productos.length" class="py-16 text-center">
      <div class="text-6xl mb-4">🔍</div>
      <h2 class="text-xl font-semibold text-gray-700 mb-2">Sin resultados para "{{ query }}"</h2>
      <p class="text-gray-500 mb-6">Intenta con otra búsqueda o revisa los productos disponibles.</p>
      <RouterLink
        to="/productos"
        class="inline-block px-6 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-md transition font-medium"
      >
        Ver todos los productos
      </RouterLink>
    </div>

    <!-- Resultados -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      <ProductCard
        v-for="producto in productos"
        :key="producto.id"
        :producto="producto"
        @add-to-cart="handleAddToCart"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { obtenerProductos } from '@/services/api.js'
import ProductCard from '@/components/ProductCard.vue'
import { useCarritoStore } from '@/stores/carrito'

const route = useRoute()
const router = useRouter()
const carrito = useCarritoStore()

const productos = ref([])
const loading = ref(false)
const total = ref(null)
const inputQ = ref(route.query.q ?? '')

const query = computed(() => route.query.q ?? '')

const fetchResultados = async (q) => {
  if (!q?.trim()) {
    productos.value = []
    total.value = 0
    return
  }
  loading.value = true
  try {
    const res = await obtenerProductos({ search: q, page_size: 40 })
    const data = res.data
    const list = Array.isArray(data) ? data : (data?.results ?? [])
    productos.value = list.filter(p => p && p.id != null)
    total.value = data?.count ?? list.length
  } catch {
    productos.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

watch(query, (val) => {
  inputQ.value = val
  fetchResultados(val)
}, { immediate: true })

const submitSearch = () => {
  const term = inputQ.value.trim()
  if (!term) return
  router.push({ name: 'busqueda', query: { q: term } })
}

const handleAddToCart = (producto) => {
  const snapshot = { ...producto }
  const idx = productos.value.findIndex(p => p.id === producto.id)
  if (idx !== -1) {
    const newStock = Math.max(0, Number(productos.value[idx].stock) - 1)
    productos.value[idx] = {
      ...productos.value[idx],
      stock: newStock,
      estado_inventario: newStock === 0 ? 'agotado' : productos.value[idx].estado_inventario,
    }
  }
  carrito.agregar(snapshot)
}
</script>
