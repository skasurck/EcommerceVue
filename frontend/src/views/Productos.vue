<template>
  <div class="w-full max-w-7xl mx-auto overflow-x-hidden">
    <header class="px-4 pt-4 pb-3 sm:px-6">
      <h1 class="text-2xl font-bold text-center text-gray-800">Productos Disponibles</h1>
    </header>

    <div class="lg:hidden sticky top-0 z-30 w-full max-w-full bg-white/95 backdrop-blur px-4 py-2 border-y border-gray-200 flex items-center gap-2 overflow-x-auto">
      <button
        class="shrink-0 rounded-full border px-3 py-1.5 text-sm font-medium shadow-sm bg-white text-gray-800 hover:border-blue-500 hover:text-blue-700 transition"
        :class="!filtros.categoria ? 'border-blue-500 text-blue-700 bg-blue-50' : ''"
        @click="selectCategoria('')"
      >
        Todas las ofertas
      </button>
      <button
        class="shrink-0 rounded-full border px-3 py-1.5 text-sm font-medium shadow-sm bg-white text-gray-800 hover:border-blue-500 hover:text-blue-700 transition"
        @click="openFilters()"
      >
        {{ categoriaLabel }}
      </button>
      <button
        class="shrink-0 rounded-full border px-3 py-1.5 text-sm font-medium shadow-sm bg-white text-gray-800 hover:border-blue-500 hover:text-blue-700 transition relative"
        @click="openFilters()"
      >
        Filtros
        <span
          v-if="appliedFiltersCount > 0"
          class="absolute -right-2 -top-2 rounded-full bg-amber-500 text-white text-[11px] px-2 py-[1px] font-semibold"
        >
          {{ appliedFiltersCount }}
        </span>
      </button>
    </div>

    <div class="p-4 sm:px-6 lg:grid lg:grid-cols-[16rem_1fr] gap-6 w-full max-w-full">
      <aside class="mb-6 lg:mb-0 hidden lg:block">
        <div class="bg-white border border-gray-200 rounded-lg p-4 space-y-6 shadow-sm">
          <div>
            <h2 class="font-semibold text-gray-800">Departamento</h2>
            <div class="mt-3 space-y-2">
              <label class="flex items-center gap-2 cursor-pointer text-sm text-gray-700">
                <input
                  type="radio"
                  value=""
                  v-model="filtros.categoria"
                  @change="handleFilterChange"
                  class="text-blue-600 focus:ring-blue-500"
                />
                <span>Todo</span>
              </label>

              <CategoryTreeRadio
                :categorias="filteredCategoriasTree"
                v-model:selected-categoria="filtros.categoria"
                v-model:expanded-ids="expandedCategoryIds"
                group-name="categoria-desktop"
                @select="handleFilterChange"
              />
            </div>
          </div>

          <div>
            <h2 class="font-semibold text-gray-800">Marcas</h2>
            <div class="mt-3 space-y-2 text-sm text-gray-700">
              <div
                v-for="marca in visibleMarcas"
                :key="marca.id"
                class="flex items-center gap-2"
              >
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
              v-if="marcas.length > visibleMarcas.length"
              class="mt-2 text-sm text-blue-600 hover:underline"
              @click="showAllMarcas = !showAllMarcas"
            >
              {{ showAllMarcas ? 'Ver menos' : 'Ver más' }}
            </button>
          </div>

          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <h2 class="font-semibold text-gray-800">Promociones</h2>
              <label class="inline-flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  class="text-blue-600 focus:ring-blue-500 rounded"
                  v-model="filtros.promociones"
                  @change="handleFilterChange"
                />
                <span>Solo en oferta</span>
              </label>
            </div>

            <div>
              <h2 class="font-semibold text-gray-800">Precio</h2>
              <div class="mt-3 space-y-3">
                <div class="flex justify-between text-sm text-gray-600 font-semibold">
                  <span>{{ formatCurrency(filtros.precio.min ?? priceRange.min) }}</span>
                  <span>{{ formatCurrency(filtros.precio.max ?? priceRange.max) }}</span>
                </div>
                <div class="p-3 rounded-lg bg-gray-50 border border-gray-200">
                  <PriceSlider
                    v-model:modelValue="priceModel"
                    :min="priceRange.min"
                    :max="priceRange.max"
                    @change="handlePriceChange"
                  />
                </div>
                <div class="grid grid-cols-2 gap-2">
                  <label class="text-xs text-gray-600">
                    Min
                    <input
                      v-model="priceInput.min"
                      type="number"
                      inputmode="numeric"
                      :min="priceRange.min"
                      :max="priceRange.max"
                      class="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      @blur="handlePriceInputCommit"
                      @keydown.enter.prevent="handlePriceInputCommit"
                    />
                  </label>
                  <label class="text-xs text-gray-600">
                    Max
                    <input
                      v-model="priceInput.max"
                      type="number"
                      inputmode="numeric"
                      :min="priceRange.min"
                      :max="priceRange.max"
                      class="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      @blur="handlePriceInputCommit"
                      @keydown.enter.prevent="handlePriceInputCommit"
                    />
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <section>
        <!-- Banner promocional -->
        <component
          v-if="shopBanner"
          :is="shopBanner.enlace ? 'a' : 'div'"
          :href="shopBanner.enlace || undefined"
          class="relative mb-5 block h-44 sm:h-52 w-full rounded-xl overflow-hidden shadow group"
        >
          <img
            :src="shopBanner.imagen_url"
            :alt="shopBanner.titulo || 'Promoción'"
            class="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <!-- gradiente izquierda → derecha -->
          <div class="absolute inset-0 bg-gradient-to-r from-black/70 via-black/30 to-transparent" />
          <div class="relative z-10 h-full flex flex-col justify-center px-6 sm:px-10 max-w-sm">
            <span class="inline-block mb-1 rounded bg-amber-400 px-2 py-0.5 text-[11px] font-bold uppercase tracking-widest text-gray-900">
              Oferta especial
            </span>
            <h2
              class="text-2xl sm:text-3xl font-extrabold leading-tight"
              :style="{ color: /^#[0-9A-Fa-f]{6}$/.test(shopBanner.titulo_color) ? shopBanner.titulo_color : '#ffffff' }"
            >
              {{ shopBanner.titulo || 'Descubre nuestras ofertas' }}
            </h2>
            <p v-if="shopBanner.descripcion" class="mt-1 text-sm text-white/80">
              {{ shopBanner.descripcion }}
            </p>
            <span
              v-if="shopBanner.enlace"
              class="mt-3 inline-block w-fit rounded bg-amber-400 hover:bg-amber-500 px-4 py-1.5 text-sm font-bold text-gray-900 transition-colors"
            >
              Descubrir →
            </span>
          </div>
        </component>

        <div class="mb-4 flex flex-col sm:flex-row gap-2">
          <input
            v-model="filtros.search"
            @input="handleFilterChange"
            placeholder="Buscar..."
            class="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div v-if="loading" class="text-center text-gray-500">Cargando productos...</div>
        <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>
        <div v-else-if="productos.length === 0" class="text-center text-gray-500">No se encontraron productos.</div>

        <div class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
          <ProductCard
            v-for="producto in productos"
            :key="producto.id"
            :producto="producto"
            @add-to-cart="handleAddToCart"
          />
        </div>

        <div v-if="loading && productos.length > 0" class="text-center text-gray-500 py-4">Cargando más productos...</div>
        <div v-if="!loading && pagination.page >= pagination.totalPages" class="text-center text-gray-500 py-4">No hay más productos.</div>
      </section>
    </div>

    <transition name="fade">
      <div
        v-if="showFiltersMobile"
        class="fixed inset-0 z-40 bg-black/40 flex justify-center sm:justify-end items-end overflow-hidden"
        @click.self="closeFilters"
      >
        <div class="h-[80vh] w-[90%] max-w-xl sm:max-w-md bg-white shadow-2xl flex flex-col overflow-hidden rounded-t-2xl sm:rounded-none">
          <div class="flex items-center justify-between border-b px-4 py-3">
            <div>
              <h3 class="text-lg font-semibold text-gray-800">Filtros</h3>
              <p class="text-xs text-gray-500">Ajusta tu búsqueda y vuelve a la lista</p>
            </div>
            <button
              class="p-2 rounded-full border border-gray-300 bg-white hover:bg-gray-100 shadow-sm"
              @click="closeFilters"
              aria-label="Cerrar filtros"
            >
              ✕
            </button>
          </div>

          <div class="flex-1 overflow-y-auto px-4 py-4 space-y-6">
            <div>
              <h2 class="font-semibold text-gray-800">Departamento</h2>
              <div class="mt-3 space-y-2">
                <label class="flex items-center gap-2 cursor-pointer text-sm text-gray-700">
                  <input
                    type="radio"
                    value=""
                    v-model="filtros.categoria"
                    @change="handleFilterChange"
                    class="text-blue-600 focus:ring-blue-500"
                  />
                  <span>Todo</span>
                </label>

                <CategoryTreeRadio
                  :categorias="filteredCategoriasTree"
                  v-model:selected-categoria="filtros.categoria"
                  v-model:expanded-ids="expandedCategoryIds"
                  group-name="categoria-mobile"
                  @select="handleFilterChange"
                />
              </div>
            </div>

            <div>
              <h2 class="font-semibold text-gray-800">Marcas</h2>
              <div class="mt-3 space-y-2 text-sm text-gray-700">
                <div
                  v-for="marca in marcas"
                  :key="marca.id"
                  class="flex items-center gap-2"
                >
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
            </div>

            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <h2 class="font-semibold text-gray-800">Promociones</h2>
                <label class="inline-flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="checkbox"
                    class="text-blue-600 focus:ring-blue-500 rounded"
                    v-model="filtros.promociones"
                    @change="handleFilterChange"
                  />
                  <span>Solo en oferta</span>
                </label>
              </div>

              <div>
                <h2 class="font-semibold text-gray-800 flex items-center justify-between">
                  Precio
                  <span class="text-xs text-gray-500">{{ formatCurrency(filtros.precio.min ?? priceRange.min) }} - {{ formatCurrency(filtros.precio.max ?? priceRange.max) }}</span>
                </h2>
                <div class="mt-3 space-y-3">
                  <div class="p-3 rounded-lg bg-gray-50 border border-gray-200">
                    <PriceSlider
                      v-model:modelValue="priceModel"
                      :min="priceRange.min"
                      :max="priceRange.max"
                      @change="handlePriceChange"
                    />
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <label class="text-xs text-gray-600">
                      Min
                      <input
                        v-model="priceInput.min"
                        type="number"
                        inputmode="numeric"
                        :min="priceRange.min"
                        :max="priceRange.max"
                        class="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        @blur="handlePriceInputCommit"
                        @keydown.enter.prevent="handlePriceInputCommit"
                      />
                    </label>
                    <label class="text-xs text-gray-600">
                      Max
                      <input
                        v-model="priceInput.max"
                        type="number"
                        inputmode="numeric"
                        :min="priceRange.min"
                        :max="priceRange.max"
                        class="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        @blur="handlePriceInputCommit"
                        @keydown.enter.prevent="handlePriceInputCommit"
                      />
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="border-t px-4 py-3 bg-white flex gap-2">
            <button
              class="flex-1 rounded-full border border-gray-300 px-3 py-2 font-semibold text-gray-700 hover:bg-gray-100"
              @click="resetFilters"
            >
              Eliminar filtros
            </button>
            <button
              class="flex-1 rounded-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-semibold px-3 py-2 shadow"
              @click="applyAndClose"
            >
              Mostrar resultados
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import ProductCard from '@/components/ProductCard.vue'
import PriceSlider from '@/components/PriceSlider.vue'
import CategoryTreeRadio from '@/components/CategoryTreeRadio.vue'
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { obtenerProductos, obtenerMarcas, obtenerRangoPrecios, obtenerPromoBanners } from '@/services/api.js'
import api from '@/axios'
import { useCarritoStore } from '@/stores/carrito'
defineOptions({ name: 'ProductosView' })

const cartStore = useCarritoStore()
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
  cartStore.agregar(snapshot)
}

const shopBanner = ref(null)
const productos = ref([])
const categorias = ref([])
const marcas = ref([])
const filtros = reactive({
  search: '',
  categoria: '',
  marcas: [],
  promociones: false,
  precio: { min: null, max: null },
})
const pagination = reactive({ page: 1, totalPages: 1, pageSize: 10 })
const loading = ref(false)
const error = ref(null)
const priceRange = reactive({ min: 0, max: 0 })
const priceInput = reactive({ min: '', max: '' })
const showAllMarcas = ref(false)
const showFiltersMobile = ref(false)
const expandedCategoryIds = ref([])
const unwrapList = (payload) => {
  if (Array.isArray(payload?.results)) return payload.results
  if (Array.isArray(payload)) return payload
  return []
}

const categoriaLabel = computed(() => {
  const found = categorias.value.find((c) => String(c.id) === String(filtros.categoria))
  return found ? found.nombre : 'Categorías'
})

const categoriasTree = computed(() => {
  const nodesById = new Map()
  const roots = []

  categorias.value.forEach((categoria) => {
    nodesById.set(categoria.id, { ...categoria, children: [] })
  })

  nodesById.forEach((node) => {
    if (node.parent && nodesById.has(node.parent)) {
      nodesById.get(node.parent).children.push(node)
      return
    }
    roots.push(node)
  })

  const sortNodes = (nodes) => {
    nodes.sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
    nodes.forEach((child) => sortNodes(child.children))
    return nodes
  }

  return sortNodes(roots)
})

const filteredCategoriasTree = computed(() => {
  const pruneAndCount = (nodes) => {
    return nodes
      .map((node) => {
        const children = pruneAndCount(node.children || [])
        const directCount = Number(node.productos_count ?? 0)
        const safeDirectCount = Number.isFinite(directCount) ? directCount : 0
        const descendantsCount = children.reduce(
          (sum, child) => sum + Number(child.total_productos ?? 0),
          0,
        )
        const totalCount = safeDirectCount + descendantsCount

        if (totalCount <= 0) return null
        return { ...node, children, total_productos: totalCount }
      })
      .filter(Boolean)
  }

  return pruneAndCount(categoriasTree.value)
})

const priceChanged = computed(() => {
  const min = typeof filtros.precio.min === 'number' ? filtros.precio.min : null
  const max = typeof filtros.precio.max === 'number' ? filtros.precio.max : null
  return (min !== null && min !== priceRange.min) || (max !== null && max !== priceRange.max)
})

const appliedFiltersCount = computed(() => {
  let total = 0
  if (filtros.categoria) total += 1
  if (filtros.marcas.length > 0) total += 1
  if (priceChanged.value) total += 1
  if (filtros.search) total += 1
  if (filtros.promociones) total += 1
  return total
})

const priceModel = computed({
  get: () => [filtros.precio.min ?? priceRange.min, filtros.precio.max ?? priceRange.max],
  set: (val = []) => {
    const [min, max] = val
    filtros.precio.min = Number(min)
    filtros.precio.max = Number(max)
  },
})

const syncPriceInputWithFilters = () => {
  priceInput.min = String(filtros.precio.min ?? '')
  priceInput.max = String(filtros.precio.max ?? '')
}

async function fetchCategorias() {
  const res = await api.get('categorias/')
  categorias.value = unwrapList(res.data)
}

async function fetchMarcas() {
  const res = await obtenerMarcas({ page_size: 100, ordering: 'nombre' })
  marcas.value = unwrapList(res.data)
}

async function fetchPriceRange() {
  try {
    const res = await obtenerRangoPrecios()
    const min = Number(res.data?.min_precio) || 0
    const max = Number(res.data?.max_precio) || 0
    priceRange.min = min
    priceRange.max = max
    filtros.precio.min = min
    filtros.precio.max = max
    syncPriceInputWithFilters()
  } catch (err) {
    console.error('Error obteniendo rango de precios:', err)
    priceRange.min = 0
    priceRange.max = 0
    filtros.precio.min = null
    filtros.precio.max = null
    syncPriceInputWithFilters()
  }
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
    if (filtros.marcas.length > 0) params.marca = filtros.marcas.join(',')
    if (typeof filtros.precio.min === 'number') params.precio_min = filtros.precio.min
    if (typeof filtros.precio.max === 'number') params.precio_max = filtros.precio.max
    if (filtros.promociones) params.en_oferta = 'true'

    const res = await obtenerProductos(params)
    let raw = unwrapList(res.data)

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

const handleFilterChange = () => {
  fetchProductos()
}

const normalizePriceRange = (nextMin = filtros.precio.min, nextMax = filtros.precio.max) => {
  let min = Number(nextMin)
  let max = Number(nextMax)

  if (!Number.isFinite(min)) min = priceRange.min
  if (!Number.isFinite(max)) max = priceRange.max

  min = Math.min(Math.max(min, priceRange.min), priceRange.max)
  max = Math.min(Math.max(max, priceRange.min), priceRange.max)

  if (min > max) {
    ;[min, max] = [max, min]
  }

  return { min: Math.round(min), max: Math.round(max) }
}

const applyPriceRange = (nextMin, nextMax) => {
  const { min, max } = normalizePriceRange(nextMin, nextMax)
  filtros.precio.min = min
  filtros.precio.max = max
  syncPriceInputWithFilters()
}

const handlePriceChange = (value) => {
  const [min, max] = value || []
  applyPriceRange(min, max)
  handleFilterChange()
}

const handlePriceInputCommit = () => {
  applyPriceRange(priceInput.min, priceInput.max)
  handleFilterChange()
}

const toggleMarca = (marcaId) => {
  const exists = filtros.marcas.includes(marcaId)
  if (exists) {
    filtros.marcas = filtros.marcas.filter((id) => id !== marcaId)
  } else {
    filtros.marcas = [...filtros.marcas, marcaId]
  }
  handleFilterChange()
}

const selectCategoria = (categoriaId) => {
  filtros.categoria = categoriaId
  handleFilterChange()
}

const currencyFormatter = new Intl.NumberFormat('es-MX', {
  style: 'currency',
  currency: 'MXN',
  maximumFractionDigits: 0,
})

const formatCurrency = (value) => {
  const safeValue = typeof value === 'number' ? value : Number(value) || 0
  return currencyFormatter.format(Math.max(0, safeValue))
}

const visibleMarcas = computed(() => {
  if (showAllMarcas.value) return marcas.value
  return marcas.value.slice(0, 5)
})

const expandCategoryPath = (categoriaId) => {
  if (!categoriaId) return
  const byId = new Map(categorias.value.map((categoria) => [String(categoria.id), categoria]))
  const nextExpanded = new Set(expandedCategoryIds.value.map((id) => String(id)))
  let current = byId.get(String(categoriaId))
  while (current?.parent) {
    nextExpanded.add(String(current.parent))
    current = byId.get(String(current.parent))
  }
  expandedCategoryIds.value = Array.from(nextExpanded)
}

const handleScroll = () => {
  const { scrollTop, scrollHeight, clientHeight } = document.documentElement
  if (scrollTop + clientHeight >= scrollHeight - 5) {
    loadMore()
  }
}

const openFilters = () => {
  showFiltersMobile.value = true
}

const closeFilters = () => {
  showFiltersMobile.value = false
}

const resetFilters = () => {
  filtros.search = ''
  filtros.categoria = ''
  filtros.marcas = []
  filtros.promociones = false
  filtros.precio.min = priceRange.min
  filtros.precio.max = priceRange.max
  syncPriceInputWithFilters()
  handleFilterChange()
}

const applyAndClose = () => {
  handleFilterChange()
  closeFilters()
}

watch(
  () => filtros.categoria,
  (categoriaId) => {
    expandCategoryPath(categoriaId)
  },
)

onMounted(async () => {
  obtenerPromoBanners({ ordering: 'orden' }).then(r => {
    const raw = Array.isArray(r.data?.results) ? r.data.results : Array.isArray(r.data) ? r.data : []
    shopBanner.value = raw.find(b => b.imagen_url) ?? null
  }).catch(() => {})
  await Promise.all([fetchCategorias(), fetchMarcas(), fetchPriceRange()])
  await fetchProductos()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>
