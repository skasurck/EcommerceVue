<template>
  <div class="w-full max-w-7xl mx-auto overflow-x-hidden">

    <!-- Header -->
    <header class="px-4 pt-6 pb-3 sm:px-6">
      <p class="text-sm text-slate-500 mb-1">Resultados de búsqueda</p>
      <div class="flex flex-wrap items-end gap-3">
        <h1 class="text-2xl font-bold text-slate-800">
          <span v-if="query">"{{ query }}"</span>
          <span v-else>Todos los productos</span>
        </h1>
        <span v-if="!loading && total !== null" class="text-sm text-slate-500 mb-0.5">
          {{ total }} {{ total === 1 ? 'resultado' : 'resultados' }}
        </span>
      </div>
    </header>

    <!-- Barra móvil -->
    <div class="lg:hidden sticky top-0 z-30 w-full bg-white/95 backdrop-blur px-4 py-2 border-y border-gray-200 flex items-center gap-2 overflow-x-auto">
      <button
        class="shrink-0 rounded-full border px-3 py-1.5 text-sm font-medium bg-white text-gray-800 hover:border-blue-500 hover:text-blue-700 transition"
        @click="openFilters"
      >
        Filtros
        <span
          v-if="appliedFiltersCount > 0"
          class="ml-1 rounded-full bg-amber-500 text-white text-[11px] px-1.5 py-px font-semibold"
        >{{ appliedFiltersCount }}</span>
      </button>
      <button
        v-if="appliedFiltersCount > 0"
        class="shrink-0 rounded-full border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 transition"
        @click="resetFilters"
      >
        Limpiar
      </button>
    </div>

    <div class="p-4 sm:px-6 lg:grid lg:grid-cols-[16rem_1fr] gap-6">

      <!-- Sidebar desktop -->
      <aside class="hidden lg:block">
        <div class="bg-white border border-gray-200 rounded-lg p-4 space-y-6 shadow-sm sticky top-4">

          <!-- Búsqueda refinada -->
          <form @submit.prevent="submitSearch" class="flex gap-1.5">
            <input
              v-model="inputQ"
              type="search"
              placeholder="Refinar búsqueda…"
              class="flex-1 border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
            <button type="submit" class="px-3 py-1.5 bg-cyan-500 hover:bg-cyan-600 text-white rounded text-sm transition">
              ›
            </button>
          </form>

          <!-- Categoría -->
          <div>
            <h2 class="font-semibold text-gray-800">Departamento</h2>
            <div class="mt-3 space-y-2">
              <label class="flex items-center gap-2 cursor-pointer text-sm text-gray-700">
                <input type="radio" value="" v-model="filtros.categoria" @change="handleFilterChange" class="text-blue-600 focus:ring-blue-500" />
                <span>Todo</span>
              </label>
              <CategoryTreeRadio
                :categorias="filteredCategoriasTree"
                v-model:selected-categoria="filtros.categoria"
                v-model:expanded-ids="expandedCategoryIds"
                group-name="cat-busqueda-desktop"
                @select="handleFilterChange"
              />
            </div>
          </div>

          <!-- Marcas -->
          <div>
            <h2 class="font-semibold text-gray-800">Marcas</h2>
            <div class="mt-3 space-y-2 text-sm text-gray-700">
              <div v-for="marca in visibleMarcas" :key="marca.id" class="flex items-center gap-2">
                <input
                  type="checkbox"
                  class="text-blue-600 focus:ring-blue-500 rounded"
                  :value="marca.id"
                  :checked="filtros.marcas.includes(marca.id)"
                  @change="toggleMarca(marca.id)"
                />
                <span>{{ marca.nombre }}</span>
              </div>
            </div>
            <button
              v-if="marcas.length > 5"
              class="mt-2 text-sm text-blue-600 hover:underline"
              @click="showAllMarcas = !showAllMarcas"
            >
              {{ showAllMarcas ? 'Ver menos' : 'Ver más' }}
            </button>
          </div>

          <!-- Precio + Promociones -->
          <div class="space-y-4">
            <label class="inline-flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input type="checkbox" class="text-blue-600 focus:ring-blue-500 rounded" v-model="filtros.promociones" @change="handleFilterChange" />
              <span>Solo en oferta</span>
            </label>

            <div>
              <div class="flex items-center justify-between mb-2">
                <h2 class="font-semibold text-gray-800">Precio</h2>
                <span class="text-xs text-gray-500">
                  {{ formatCurrency(filtros.precio.min ?? priceRange.min) }} – {{ formatCurrency(filtros.precio.max ?? priceRange.max) }}
                </span>
              </div>
              <div class="p-3 rounded-lg bg-gray-50 border border-gray-200">
                <PriceSlider v-model:modelValue="priceModel" :min="priceRange.min" :max="priceRange.max" @change="handlePriceChange" />
              </div>
              <div class="grid grid-cols-2 gap-2 mt-2">
                <label class="text-xs text-gray-600">
                  Min
                  <input v-model="priceInput.min" type="number" :min="priceRange.min" :max="priceRange.max"
                    class="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    @blur="handlePriceInputCommit" @keydown.enter.prevent="handlePriceInputCommit" />
                </label>
                <label class="text-xs text-gray-600">
                  Max
                  <input v-model="priceInput.max" type="number" :min="priceRange.min" :max="priceRange.max"
                    class="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    @blur="handlePriceInputCommit" @keydown.enter.prevent="handlePriceInputCommit" />
                </label>
              </div>
            </div>
          </div>

          <button class="w-full rounded-full border border-gray-300 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 transition" @click="resetFilters">
            Eliminar filtros
          </button>
        </div>
      </aside>

      <!-- Resultados -->
      <section>
        <!-- Skeleton -->
        <div v-if="loading && !productos.length" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          <div v-for="n in 12" :key="n" class="bg-white rounded-lg border border-gray-200 overflow-hidden animate-pulse">
            <div class="bg-gray-200 aspect-square w-full" />
            <div class="p-3 space-y-2">
              <div class="h-3 bg-gray-200 rounded w-3/4" />
              <div class="h-3 bg-gray-200 rounded w-1/2" />
              <div class="h-4 bg-gray-200 rounded w-1/3 mt-2" />
            </div>
          </div>
        </div>

        <!-- Sin resultados -->
        <div v-else-if="!loading && !productos.length" class="py-16 text-center">
          <div class="text-6xl mb-4">🔍</div>
          <h2 class="text-xl font-semibold text-gray-700 mb-2">Sin resultados para "{{ query }}"</h2>
          <p class="text-gray-500 mb-6">Intenta con otra búsqueda o ajusta los filtros.</p>
          <button class="px-5 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-md font-medium transition" @click="resetFilters">
            Limpiar filtros
          </button>
        </div>

        <!-- Grid -->
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <ProductCard
            v-for="producto in productos"
            :key="producto.id"
            :producto="producto"
            @add-to-cart="handleAddToCart"
          />
        </div>

        <div v-if="!loading && pagination.page >= pagination.totalPages && productos.length" class="text-center text-gray-400 text-sm py-6">
          Fin de los resultados
        </div>
      </section>
    </div>

    <!-- Panel móvil de filtros -->
    <transition name="fade">
      <div
        v-if="showFiltersMobile"
        class="fixed inset-0 z-40 bg-black/40 flex justify-center sm:justify-end items-end"
        @click.self="closeFilters"
      >
        <div class="h-[80vh] w-[90%] max-w-xl sm:max-w-md bg-white shadow-2xl flex flex-col overflow-hidden rounded-t-2xl sm:rounded-none">
          <div class="flex items-center justify-between border-b px-4 py-3">
            <h3 class="text-lg font-semibold text-gray-800">Filtros</h3>
            <button class="p-2 rounded-full border hover:bg-gray-100" @click="closeFilters">✕</button>
          </div>

          <div class="flex-1 overflow-y-auto px-4 py-4 space-y-6">
            <!-- Categoría -->
            <div>
              <h2 class="font-semibold text-gray-800">Departamento</h2>
              <div class="mt-3 space-y-2">
                <label class="flex items-center gap-2 cursor-pointer text-sm text-gray-700">
                  <input type="radio" value="" v-model="filtros.categoria" @change="handleFilterChange" class="text-blue-600" />
                  <span>Todo</span>
                </label>
                <CategoryTreeRadio
                  :categorias="filteredCategoriasTree"
                  v-model:selected-categoria="filtros.categoria"
                  v-model:expanded-ids="expandedCategoryIds"
                  group-name="cat-busqueda-mobile"
                  @select="handleFilterChange"
                />
              </div>
            </div>

            <!-- Marcas -->
            <div>
              <h2 class="font-semibold text-gray-800">Marcas</h2>
              <div class="mt-3 space-y-2 text-sm text-gray-700">
                <div v-for="marca in marcas" :key="marca.id" class="flex items-center gap-2">
                  <input type="checkbox" class="text-blue-600 rounded" :value="marca.id" :checked="filtros.marcas.includes(marca.id)" @change="toggleMarca(marca.id)" />
                  <span>{{ marca.nombre }}</span>
                </div>
              </div>
            </div>

            <!-- Precio + Promociones -->
            <div class="space-y-4">
              <label class="inline-flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input type="checkbox" class="text-blue-600 rounded" v-model="filtros.promociones" @change="handleFilterChange" />
                <span>Solo en oferta</span>
              </label>
              <div>
                <div class="flex items-center justify-between mb-2">
                  <h2 class="font-semibold text-gray-800">Precio</h2>
                  <span class="text-xs text-gray-500">{{ formatCurrency(filtros.precio.min ?? priceRange.min) }} – {{ formatCurrency(filtros.precio.max ?? priceRange.max) }}</span>
                </div>
                <div class="p-3 rounded-lg bg-gray-50 border border-gray-200">
                  <PriceSlider v-model:modelValue="priceModel" :min="priceRange.min" :max="priceRange.max" @change="handlePriceChange" />
                </div>
                <div class="grid grid-cols-2 gap-2 mt-2">
                  <label class="text-xs text-gray-600">Min
                    <input v-model="priceInput.min" type="number" class="mt-1 w-full border rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      @blur="handlePriceInputCommit" @keydown.enter.prevent="handlePriceInputCommit" />
                  </label>
                  <label class="text-xs text-gray-600">Max
                    <input v-model="priceInput.max" type="number" class="mt-1 w-full border rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      @blur="handlePriceInputCommit" @keydown.enter.prevent="handlePriceInputCommit" />
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div class="border-t px-4 py-3 bg-white flex gap-2">
            <button class="flex-1 rounded-full border border-gray-300 py-2 font-semibold text-gray-700 hover:bg-gray-100" @click="resetFilters">Eliminar filtros</button>
            <button class="flex-1 rounded-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-semibold py-2" @click="applyAndClose">Mostrar resultados</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHead } from '@vueuse/head'
import { obtenerProductos, obtenerMarcas, obtenerRangoPrecios } from '@/services/api.js'
import { useCarritoStore } from '@/stores/carrito'
import api from '@/axios'
import ProductCard from '@/components/ProductCard.vue'
import PriceSlider from '@/components/PriceSlider.vue'
import CategoryTreeRadio from '@/components/CategoryTreeRadio.vue'

const route  = useRoute()
const router = useRouter()
const carrito = useCarritoStore()

// ── Estado ────────────────────────────────────────────────
const productos  = ref([])
const categorias = ref([])
const marcas     = ref([])
const loading    = ref(false)
const total      = ref(null)
const inputQ     = ref(route.query.q ?? '')
const showAllMarcas      = ref(false)
const showFiltersMobile  = ref(false)
const expandedCategoryIds = ref([])

const query = computed(() => route.query.q ?? '')

// ── SEO dinámico según término buscado ────────────────────
useHead(computed(() => {
  const q = query.value
  const title = q
    ? `Resultados para "${q}" — Mktska Digital`
    : 'Búsqueda de productos — Mktska Digital'
  const desc = q
    ? `Encuentra ${q} en Mktska Digital. Tecnología y cómputo al mejor precio. Envíos a todo México.`
    : 'Busca tecnología, computadoras, componentes y más en Mktska Digital.'
  const origin = typeof window !== 'undefined' ? window.location.origin : 'https://mktska.net'
  const url = typeof window !== 'undefined' ? window.location.href : ''
  return {
    title,
    meta: [
      { name: 'description', content: desc },
      { name: 'robots', content: 'noindex, follow' }, // resultados de búsqueda no se indexan
      { property: 'og:type', content: 'website' },
      { property: 'og:url', content: url },
      { property: 'og:title', content: title },
      { property: 'og:description', content: desc },
      { property: 'og:image', content: `${origin}/logo-mktska.png` },
    ],
  }
}))

const filtros = reactive({
  categoria:   '',
  marcas:      [],
  promociones: false,
  precio:      { min: null, max: null },
})
const pagination = reactive({ page: 1, totalPages: 1, pageSize: 40 })
const priceRange = reactive({ min: 0, max: 0 })
const priceInput = reactive({ min: '', max: '' })

// ── Helpers ───────────────────────────────────────────────
const unwrapList = (d) => Array.isArray(d?.results) ? d.results : Array.isArray(d) ? d : []

const currencyFormatter = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 })
const formatCurrency = (v) => currencyFormatter.format(Math.max(0, Number(v) || 0))

const syncPriceInputWithFilters = () => {
  priceInput.min = String(filtros.precio.min ?? '')
  priceInput.max = String(filtros.precio.max ?? '')
}

// ── Computados ────────────────────────────────────────────
const visibleMarcas = computed(() => showAllMarcas.value ? marcas.value : marcas.value.slice(0, 5))

const categoriasTree = computed(() => {
  const byId = new Map()
  categorias.value.forEach(c => byId.set(c.id, { ...c, children: [] }))
  const roots = []
  byId.forEach(node => {
    if (node.parent && byId.has(node.parent)) byId.get(node.parent).children.push(node)
    else roots.push(node)
  })
  const sort = (nodes) => { nodes.sort((a, b) => a.nombre.localeCompare(b.nombre, 'es')); nodes.forEach(n => sort(n.children)); return nodes }
  return sort(roots)
})

const filteredCategoriasTree = computed(() => {
  const prune = (nodes) => nodes.map(node => {
    const children = prune(node.children || [])
    const total = (Number(node.productos_count) || 0) + children.reduce((s, c) => s + (c.total_productos ?? 0), 0)
    return total > 0 ? { ...node, children, total_productos: total } : null
  }).filter(Boolean)
  return prune(categoriasTree.value)
})

const priceChanged = computed(() => {
  const { min, max } = filtros.precio
  return (min !== null && min !== priceRange.min) || (max !== null && max !== priceRange.max)
})

const appliedFiltersCount = computed(() => {
  let n = 0
  if (filtros.categoria) n++
  if (filtros.marcas.length) n++
  if (priceChanged.value) n++
  if (filtros.promociones) n++
  return n
})

const priceModel = computed({
  get: () => [filtros.precio.min ?? priceRange.min, filtros.precio.max ?? priceRange.max],
  set: ([min, max]) => { filtros.precio.min = Number(min); filtros.precio.max = Number(max) },
})

// ── Fetch ─────────────────────────────────────────────────
async function fetchCategorias() {
  const r = await api.get('categorias/')
  categorias.value = unwrapList(r.data)
}

async function fetchMarcas() {
  const r = await obtenerMarcas({ page_size: 100, ordering: 'nombre' })
  marcas.value = unwrapList(r.data)
}

async function fetchPriceRange() {
  try {
    const r = await obtenerRangoPrecios()
    const min = Number(r.data?.min_precio) || 0
    const max = Number(r.data?.max_precio) || 0
    Object.assign(priceRange, { min, max })
    filtros.precio.min = min
    filtros.precio.max = max
    syncPriceInputWithFilters()
  } catch { /* silent */ }
}

async function fetchResultados() {
  if (!query.value?.trim()) { productos.value = []; total.value = 0; return }
  loading.value = true
  try {
    const params = { search: query.value, page: pagination.page, page_size: pagination.pageSize }
    if (filtros.categoria) params.categoria = filtros.categoria
    if (filtros.marcas.length) params.marca = filtros.marcas.join(',')
    if (typeof filtros.precio.min === 'number') params.precio_min = filtros.precio.min
    if (typeof filtros.precio.max === 'number') params.precio_max = filtros.precio.max
    if (filtros.promociones) params.en_oferta = 'true'

    const res = await obtenerProductos(params)
    const list = unwrapList(res.data).filter(p => p?.id != null)
    if (pagination.page === 1) {
      productos.value = list
    } else {
      productos.value = [...productos.value, ...list]
    }
    total.value = res.data?.count ?? list.length
    pagination.totalPages = Math.max(1, Math.ceil(total.value / pagination.pageSize))
  } catch {
    productos.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// ── Handlers ──────────────────────────────────────────────
const handleFilterChange = () => { pagination.page = 1; fetchResultados() }

const normalizePriceRange = (nextMin, nextMax) => {
  let min = Number(nextMin), max = Number(nextMax)
  if (!Number.isFinite(min)) min = priceRange.min
  if (!Number.isFinite(max)) max = priceRange.max
  min = Math.min(Math.max(min, priceRange.min), priceRange.max)
  max = Math.min(Math.max(max, priceRange.min), priceRange.max)
  if (min > max) [min, max] = [max, min]
  return { min: Math.round(min), max: Math.round(max) }
}

const applyPriceRange = (nextMin, nextMax) => {
  const { min, max } = normalizePriceRange(nextMin, nextMax)
  filtros.precio.min = min; filtros.precio.max = max
  syncPriceInputWithFilters()
}

const handlePriceChange  = ([min, max]) => { applyPriceRange(min, max); handleFilterChange() }
const handlePriceInputCommit = () => { applyPriceRange(priceInput.min, priceInput.max); handleFilterChange() }
const toggleMarca = (id) => {
  filtros.marcas = filtros.marcas.includes(id) ? filtros.marcas.filter(x => x !== id) : [...filtros.marcas, id]
  handleFilterChange()
}

const resetFilters = () => {
  filtros.categoria = ''; filtros.marcas = []; filtros.promociones = false
  filtros.precio.min = priceRange.min; filtros.precio.max = priceRange.max
  syncPriceInputWithFilters(); handleFilterChange()
}

const submitSearch = () => {
  const term = inputQ.value.trim()
  if (term) router.push({ name: 'busqueda', query: { q: term } })
}

const openFilters  = () => { showFiltersMobile.value = true }
const closeFilters = () => { showFiltersMobile.value = false }
const applyAndClose = () => { handleFilterChange(); closeFilters() }

const handleAddToCart = (producto) => {
  const idx = productos.value.findIndex(p => p.id === producto.id)
  if (idx !== -1) {
    const newStock = Math.max(0, Number(productos.value[idx].stock) - 1)
    productos.value[idx] = { ...productos.value[idx], stock: newStock, estado_inventario: newStock === 0 ? 'agotado' : productos.value[idx].estado_inventario }
  }
  carrito.agregar({ ...producto })
}

// ── Watchers ──────────────────────────────────────────────
watch(query, (val) => { inputQ.value = val; pagination.page = 1; fetchResultados() })

watch(() => filtros.categoria, (id) => {
  if (!id) return
  const byId = new Map(categorias.value.map(c => [String(c.id), c]))
  const expanded = new Set(expandedCategoryIds.value.map(String))
  let cur = byId.get(String(id))
  while (cur?.parent) { expanded.add(String(cur.parent)); cur = byId.get(String(cur.parent)) }
  expandedCategoryIds.value = [...expanded]
})

const handleScroll = () => {
  const { scrollTop, scrollHeight, clientHeight } = document.documentElement
  if (scrollTop + clientHeight >= scrollHeight - 5 && !loading.value && pagination.page < pagination.totalPages) {
    pagination.page++
    fetchResultados()
  }
}

onMounted(async () => {
  await Promise.all([fetchCategorias(), fetchMarcas(), fetchPriceRange()])
  fetchResultados()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => window.removeEventListener('scroll', handleScroll))
</script>
