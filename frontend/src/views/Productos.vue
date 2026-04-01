<template>
  <div class="w-full max-w-7xl mx-auto overflow-x-hidden">
    <header class="px-4 pt-4 pb-3 sm:px-6">
      <h1 class="text-2xl font-bold text-center text-gray-800">Productos Disponibles</h1>
    </header>

    <!-- Barra mobile sticky -->
    <div class="lg:hidden sticky top-0 z-30 w-full max-w-full bg-white/95 backdrop-blur px-4 py-2 border-y border-gray-200 flex items-center gap-2 overflow-x-auto">
      <button
        class="shrink-0 rounded-full border px-3 py-1.5 text-sm font-medium shadow-sm bg-white text-gray-800 hover:border-blue-500 hover:text-blue-700 transition"
        :class="!filtros.categoria ? 'border-blue-500 text-blue-700 bg-blue-50' : ''"
        @click="selectCategoria('')"
      >Todas</button>
      <button
        class="shrink-0 rounded-full border px-3 py-1.5 text-sm font-medium shadow-sm bg-white text-gray-800 hover:border-blue-500 hover:text-blue-700 transition"
        @click="openFilters()"
      >{{ categoriaLabel }}</button>
      <button
        class="shrink-0 rounded-full border px-3 py-1.5 text-sm font-medium shadow-sm bg-white text-gray-800 hover:border-blue-500 hover:text-blue-700 transition relative"
        @click="openFilters()"
      >
        Filtros
        <span v-if="appliedFiltersCount > 0" class="absolute -right-2 -top-2 rounded-full bg-amber-500 text-white text-[11px] px-2 py-[1px] font-semibold">
          {{ appliedFiltersCount }}
        </span>
      </button>
    </div>

    <div class="p-4 sm:px-6 lg:grid lg:grid-cols-[16rem_1fr] gap-6 w-full max-w-full">
      <!-- ── Sidebar desktop ──────────────────────────────────────── -->
      <aside class="mb-6 lg:mb-0 hidden lg:block">
        <div class="bg-white border border-gray-200 rounded-lg p-4 space-y-5 shadow-sm">

          <!-- Departamento -->
          <div>
            <h2 class="font-semibold text-gray-800 mb-3">Departamento</h2>
            <div class="space-y-1.5">
              <label class="flex items-center gap-2 cursor-pointer text-sm text-gray-700">
                <input type="radio" value="" v-model="filtros.categoria" @change="handleFilterChange" class="text-blue-600 focus:ring-blue-500" />
                <span>Todo</span>
              </label>
              <CategoryTreeRadio
                :categorias="sidebarCategoriasTree"
                v-model:selected-categoria="filtros.categoria"
                v-model:expanded-ids="expandedCategoryIds"
                group-name="categoria-desktop"
                @select="handleFilterChange"
              />
            </div>
          </div>

          <hr class="border-gray-100" />

          <!-- Disponibilidad -->
          <div>
            <h2 class="font-semibold text-gray-800 mb-3">Disponibilidad</h2>
            <div class="space-y-1.5">
              <label v-for="op in DISPONIBILIDAD_OPTS" :key="op.value" class="flex items-center gap-2 cursor-pointer text-sm text-gray-700">
                <input type="radio" :value="op.value" v-model="filtros.disponibilidad" @change="handleFilterChange" class="text-blue-600 focus:ring-blue-500" />
                <span>{{ op.label }}</span>
              </label>
            </div>
          </div>

          <hr class="border-gray-100" />

          <!-- Ofertas -->
          <div class="flex items-center justify-between">
            <h2 class="font-semibold text-gray-800">Solo en oferta</h2>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="filtros.promociones" @change="handleFilterChange" class="sr-only peer" />
              <div class="w-9 h-5 bg-gray-200 peer-focus:ring-2 peer-focus:ring-blue-400 rounded-full peer peer-checked:bg-blue-600 transition-colors"></div>
              <div class="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform peer-checked:translate-x-4"></div>
            </label>
          </div>

          <hr class="border-gray-100" />

          <!-- Precio -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <h2 class="font-semibold text-gray-800">Precio</h2>
              <button v-if="priceChanged" @click="resetPrecio" class="text-xs text-blue-600 hover:underline">Limpiar</button>
            </div>
            <!-- Rangos rápidos -->
            <div class="flex flex-wrap gap-1.5 mb-3">
              <button
                v-for="rango in RANGOS_PRECIO" :key="rango.label"
                @click="applyRangoPrecio(rango)"
                class="text-xs px-2.5 py-1 rounded-full border transition-colors"
                :class="isRangoActive(rango) ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400 hover:text-blue-600'"
              >{{ rango.label }}</button>
            </div>
            <!-- Slider -->
            <div class="flex justify-between text-xs text-gray-500 mb-2">
              <span>{{ formatCurrency(filtros.precio.min ?? priceRange.min) }}</span>
              <span>{{ formatCurrency(filtros.precio.max ?? priceRange.max) }}</span>
            </div>
            <div class="p-3 rounded-lg bg-gray-50 border border-gray-200">
              <PriceSlider v-model:modelValue="priceModel" :min="priceRange.min" :max="priceRange.max" @change="handlePriceChange" />
            </div>
            <div class="grid grid-cols-2 gap-2 mt-2">
              <label class="text-xs text-gray-600">
                Min
                <input v-model="priceInput.min" type="number" inputmode="numeric" :min="priceRange.min" :max="priceRange.max"
                  class="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @blur="handlePriceInputCommit" @keydown.enter.prevent="handlePriceInputCommit" />
              </label>
              <label class="text-xs text-gray-600">
                Max
                <input v-model="priceInput.max" type="number" inputmode="numeric" :min="priceRange.min" :max="priceRange.max"
                  class="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @blur="handlePriceInputCommit" @keydown.enter.prevent="handlePriceInputCommit" />
              </label>
            </div>
          </div>

          <!-- Marcas -->
          <div v-if="marcas.length">
            <hr class="border-gray-100 mb-4" />
            <h2 class="font-semibold text-gray-800 mb-3">Marcas</h2>
            <div class="space-y-1.5 text-sm text-gray-700">
              <div v-for="marca in visibleMarcas" :key="marca.id" class="flex items-center gap-2">
                <input type="checkbox" class="text-blue-600 focus:ring-blue-500 rounded" :value="marca.id" :checked="filtros.marcas.includes(marca.id)" @change="toggleMarca(marca.id)" />
                <span>{{ marca.nombre }}</span>
              </div>
            </div>
            <button v-if="marcas.length > visibleMarcas.length" class="mt-2 text-xs text-blue-600 hover:underline" @click="showAllMarcas = !showAllMarcas">
              {{ showAllMarcas ? 'Ver menos' : `Ver más (${marcas.length - 5})` }}
            </button>
          </div>

        </div>
      </aside>

      <!-- ── Sección de productos ─────────────────────────────────── -->
      <section>
        <!-- Banner promocional -->
        <component v-if="shopBanner" :is="shopBanner.enlace ? 'a' : 'div'" :href="shopBanner.enlace || undefined"
          class="relative mb-5 block h-44 sm:h-52 w-full rounded-xl overflow-hidden shadow group">
          <img :src="shopBanner.imagen_url" :alt="shopBanner.titulo || 'Promoción'"
            class="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" />
          <div class="absolute inset-0 bg-gradient-to-r from-black/70 via-black/30 to-transparent" />
          <div class="relative z-10 h-full flex flex-col justify-center px-6 sm:px-10 max-w-sm">
            <span class="inline-block mb-1 rounded bg-amber-400 px-2 py-0.5 text-[11px] font-bold uppercase tracking-widest text-gray-900">Oferta especial</span>
            <h2 class="text-2xl sm:text-3xl font-extrabold leading-tight" :style="{ color: /^#[0-9A-Fa-f]{6}$/.test(shopBanner.titulo_color) ? shopBanner.titulo_color : '#ffffff' }">
              {{ shopBanner.titulo || 'Descubre nuestras ofertas' }}
            </h2>
            <p v-if="shopBanner.descripcion" class="mt-1 text-sm text-white/80">{{ shopBanner.descripcion }}</p>
            <span v-if="shopBanner.enlace" class="mt-3 inline-block w-fit rounded bg-amber-400 hover:bg-amber-500 px-4 py-1.5 text-sm font-bold text-gray-900 transition-colors">Descubrir →</span>
          </div>
        </component>

        <!-- Toolbar: buscar + ordenar -->
        <div class="mb-4 flex flex-col sm:flex-row gap-2">
          <input v-model="filtros.search" @input="handleFilterChange" placeholder="Buscar productos..."
            class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <select v-model="filtros.orden" @change="handleFilterChange"
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white">
            <option value="">Más relevantes</option>
            <option value="-fecha_creacion">Más nuevos</option>
            <option value="precio_normal">Menor precio</option>
            <option value="-precio_normal">Mayor precio</option>
          </select>
        </div>

        <!-- Tags de filtros activos -->
        <div v-if="appliedFiltersCount > 0" class="flex flex-wrap gap-2 mb-4">
          <span v-if="filtros.categoria" class="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2.5 py-1">
            {{ categoriaLabel }}
            <button @click="selectCategoria('')" class="ml-0.5 hover:text-blue-900">✕</button>
          </span>
          <span v-if="filtros.disponibilidad" class="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2.5 py-1">
            {{ DISPONIBILIDAD_OPTS.find(o => o.value === filtros.disponibilidad)?.label }}
            <button @click="filtros.disponibilidad = ''; handleFilterChange()" class="ml-0.5 hover:text-blue-900">✕</button>
          </span>
          <span v-if="filtros.promociones" class="inline-flex items-center gap-1 text-xs bg-amber-50 text-amber-700 border border-amber-200 rounded-full px-2.5 py-1">
            Solo oferta
            <button @click="filtros.promociones = false; handleFilterChange()" class="ml-0.5 hover:text-amber-900">✕</button>
          </span>
          <span v-if="priceChanged" class="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2.5 py-1">
            {{ formatCurrency(filtros.precio.min) }} – {{ formatCurrency(filtros.precio.max) }}
            <button @click="resetPrecio" class="ml-0.5 hover:text-blue-900">✕</button>
          </span>
          <button @click="resetFilters" class="text-xs text-gray-500 hover:text-red-600 underline">Limpiar todo</button>
        </div>

        <div v-if="error" class="text-center text-red-500 py-6">{{ error }}</div>

        <!-- Skeleton inicial -->
        <div v-if="loading && productos.length === 0"
             class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
          <div v-for="i in 10" :key="i" class="rounded-xl border border-gray-100 bg-white overflow-hidden animate-pulse shadow-sm">
            <div class="bg-gray-200 aspect-square w-full"></div>
            <div class="p-3 space-y-2">
              <div class="h-4 bg-gray-200 rounded w-1/2"></div>
              <div class="h-3 bg-gray-200 rounded w-full"></div>
              <div class="h-3 bg-gray-200 rounded w-3/4"></div>
              <div class="h-7 bg-gray-100 rounded-full w-full mt-2"></div>
            </div>
          </div>
        </div>

        <div v-else-if="!loading && productos.length === 0 && !error"
             class="flex flex-col items-center justify-center py-20 text-center text-gray-400">
          <svg class="h-12 w-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0H4m8-7v7"/>
          </svg>
          <p class="font-medium">No se encontraron productos</p>
          <p class="text-sm mt-1">Prueba con otros filtros</p>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
          <ProductCard v-for="producto in productos" :key="producto.id" :producto="producto" @add-to-cart="handleAddToCart" />
        </div>

        <div v-if="loading && productos.length > 0" class="flex justify-center py-6">
          <div class="h-7 w-7 rounded-full border-2 border-gray-200 border-t-blue-500 animate-spin"></div>
        </div>
        <div v-if="!loading && pagination.page >= pagination.totalPages && productos.length > 0" class="text-center text-gray-400 text-sm py-4">No hay más productos.</div>
        <div ref="sentinel" class="h-1"></div>
      </section>
    </div>

    <!-- ── Modal filtros mobile ────────────────────────────────────── -->
    <transition name="fade">
      <div v-if="showFiltersMobile" class="fixed inset-0 z-40 bg-black/40 flex justify-center sm:justify-end items-end overflow-hidden" @click.self="closeFilters">
        <div class="h-[88vh] w-full max-w-xl sm:max-w-md bg-white shadow-2xl flex flex-col overflow-hidden rounded-t-2xl sm:rounded-none">
          <div class="flex items-center justify-between border-b px-4 py-3">
            <div>
              <h3 class="text-lg font-semibold text-gray-800">Filtros</h3>
              <p class="text-xs text-gray-500">Ajusta tu búsqueda y vuelve a la lista</p>
            </div>
            <button class="p-2 rounded-full border border-gray-300 bg-white hover:bg-gray-100 shadow-sm" @click="closeFilters" aria-label="Cerrar filtros">✕</button>
          </div>

          <div class="flex-1 overflow-y-auto px-4 py-4 space-y-6">

            <!-- Ordenar (mobile) -->
            <div>
              <h2 class="font-semibold text-gray-800 mb-2">Ordenar por</h2>
              <div class="grid grid-cols-2 gap-2">
                <button v-for="op in ORDEN_OPTS" :key="op.value" @click="filtros.orden = op.value"
                  class="text-sm py-2 px-3 rounded-lg border transition-colors"
                  :class="filtros.orden === op.value ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300'">
                  {{ op.label }}
                </button>
              </div>
            </div>

            <!-- Departamento (mobile) -->
            <div>
              <h2 class="font-semibold text-gray-800 mb-2">Departamento</h2>
              <div class="space-y-1.5">
                <label class="flex items-center gap-2 cursor-pointer text-sm text-gray-700">
                  <input type="radio" value="" v-model="filtros.categoria" @change="handleFilterChange" class="text-blue-600 focus:ring-blue-500" />
                  <span>Todo</span>
                </label>
                <CategoryTreeRadio
                  :categorias="sidebarCategoriasTree"
                  v-model:selected-categoria="filtros.categoria"
                  v-model:expanded-ids="expandedCategoryIds"
                  group-name="categoria-mobile"
                  @select="handleFilterChange"
                />
              </div>
            </div>

            <!-- Disponibilidad (mobile) -->
            <div>
              <h2 class="font-semibold text-gray-800 mb-2">Disponibilidad</h2>
              <div class="grid grid-cols-2 gap-2">
                <label v-for="op in DISPONIBILIDAD_OPTS" :key="op.value"
                  class="flex items-center gap-2 text-sm border rounded-lg px-3 py-2 cursor-pointer transition-colors"
                  :class="filtros.disponibilidad === op.value ? 'bg-blue-50 border-blue-500 text-blue-700' : 'border-gray-200 text-gray-700'">
                  <input type="radio" :value="op.value" v-model="filtros.disponibilidad" class="sr-only" />
                  {{ op.label }}
                </label>
              </div>
            </div>

            <!-- Ofertas (mobile) -->
            <div class="flex items-center justify-between">
              <h2 class="font-semibold text-gray-800">Solo en oferta</h2>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="filtros.promociones" class="sr-only peer" />
                <div class="w-9 h-5 bg-gray-200 peer-focus:ring-2 peer-focus:ring-blue-400 rounded-full peer peer-checked:bg-blue-600 transition-colors"></div>
                <div class="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform peer-checked:translate-x-4"></div>
              </label>
            </div>

            <!-- Precio (mobile) -->
            <div>
              <h2 class="font-semibold text-gray-800 mb-2">Precio</h2>
              <div class="flex flex-wrap gap-1.5 mb-3">
                <button v-for="rango in RANGOS_PRECIO" :key="rango.label" @click="applyRangoPrecio(rango)"
                  class="text-xs px-2.5 py-1 rounded-full border transition-colors"
                  :class="isRangoActive(rango) ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300'">
                  {{ rango.label }}
                </button>
              </div>
              <div class="p-3 rounded-lg bg-gray-50 border border-gray-200">
                <PriceSlider v-model:modelValue="priceModel" :min="priceRange.min" :max="priceRange.max" @change="handlePriceChange" />
              </div>
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>{{ formatCurrency(filtros.precio.min ?? priceRange.min) }}</span>
                <span>{{ formatCurrency(filtros.precio.max ?? priceRange.max) }}</span>
              </div>
              <div class="grid grid-cols-2 gap-2 mt-2">
                <label class="text-xs text-gray-600">
                  Min
                  <input v-model="priceInput.min" type="number" inputmode="numeric" :min="priceRange.min" :max="priceRange.max"
                    class="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    @blur="handlePriceInputCommit" @keydown.enter.prevent="handlePriceInputCommit" />
                </label>
                <label class="text-xs text-gray-600">
                  Max
                  <input v-model="priceInput.max" type="number" inputmode="numeric" :min="priceRange.min" :max="priceRange.max"
                    class="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    @blur="handlePriceInputCommit" @keydown.enter.prevent="handlePriceInputCommit" />
                </label>
              </div>
            </div>

            <!-- Marcas (mobile) -->
            <div v-if="marcas.length">
              <h2 class="font-semibold text-gray-800 mb-2">Marcas</h2>
              <div class="space-y-1.5 text-sm text-gray-700">
                <div v-for="marca in marcas" :key="marca.id" class="flex items-center gap-2">
                  <input type="checkbox" class="text-blue-600 focus:ring-blue-500 rounded" :value="marca.id" :checked="filtros.marcas.includes(marca.id)" @change="toggleMarca(marca.id)" />
                  <span>{{ marca.nombre }}</span>
                </div>
              </div>
            </div>

          </div>

          <div class="border-t px-4 py-3 bg-white flex gap-2">
            <button class="flex-1 rounded-full border border-gray-300 px-3 py-2 font-semibold text-gray-700 hover:bg-gray-100" @click="resetFilters">Limpiar</button>
            <button class="flex-1 rounded-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-semibold px-3 py-2 shadow" @click="applyAndClose">Ver resultados</button>
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
import { ref, reactive, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { obtenerProductos, obtenerMarcas, obtenerRangoPrecios, obtenerPromoBanners } from '@/services/api.js'
import api from '@/axios'
import { useCarritoStore } from '@/stores/carrito'
defineOptions({ name: 'ProductosView' })

const route = useRoute()

// ── Constantes ──────────────────────────────────────────────────────────────
const RANGOS_PRECIO = [
  { label: '< $500',           min: 0,    max: 499  },
  { label: '$500 – $1,500',    min: 500,  max: 1500 },
  { label: '$1,500 – $5,000',  min: 1500, max: 5000 },
  { label: '> $5,000',         min: 5001, max: null  },
]

const DISPONIBILIDAD_OPTS = [
  { value: '',              label: 'Todos'         },
  { value: 'en_existencia', label: 'En existencia' },
  { value: 'agotado',       label: 'Agotado'       },
]

const ORDEN_OPTS = [
  { value: '',               label: 'Más relevantes' },
  { value: '-fecha_creacion', label: 'Más nuevos'    },
  { value: 'precio_normal',  label: 'Menor precio'   },
  { value: '-precio_normal', label: 'Mayor precio'   },
  { value: 'en_oferta',      label: 'Ofertas'        },
]

// ── Estado ───────────────────────────────────────────────────────────────────
const shopBanner      = ref(null)
const productos       = ref([])
const categorias      = ref([])
const marcas          = ref([])
const loading         = ref(false)
const error           = ref(null)
const showAllMarcas   = ref(false)
const showFiltersMobile = ref(false)
const expandedCategoryIds = ref([])
const sentinel        = ref(null)
let observer = null

const filtros = reactive({
  search:        '',
  categoria:     '',
  marcas:        [],
  promociones:   false,
  disponibilidad: '',
  orden:         '',
  precio: { min: null, max: null },
})

const pagination  = reactive({ page: 1, totalPages: 1, pageSize: 10 })
const priceRange  = reactive({ min: 0, max: 0 })
const priceInput  = reactive({ min: '', max: '' })

// ── Helpers ──────────────────────────────────────────────────────────────────
const cartStore = useCarritoStore()

const unwrapList = (payload) => {
  if (Array.isArray(payload?.results)) return payload.results
  if (Array.isArray(payload)) return payload
  return []
}

const currencyFormatter = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 })
const formatCurrency = (v) => currencyFormatter.format(Math.max(0, typeof v === 'number' ? v : Number(v) || 0))

// ── Computeds ────────────────────────────────────────────────────────────────
const categoriaLabel = computed(() => {
  const found = categorias.value.find((c) => String(c.id) === String(filtros.categoria))
  return found ? found.nombre : 'Categorías'
})

const categoriasTree = computed(() => {
  const byId = new Map()
  const roots = []
  categorias.value.forEach((c) => byId.set(c.id, { ...c, children: [] }))
  byId.forEach((node) => {
    if (node.parent && byId.has(node.parent)) { byId.get(node.parent).children.push(node); return }
    roots.push(node)
  })
  const sort = (nodes) => { nodes.sort((a, b) => a.nombre.localeCompare(b.nombre, 'es')); nodes.forEach(n => sort(n.children)); return nodes }
  return sort(roots)
})

const filteredCategoriasTree = computed(() => {
  const prune = (nodes) => nodes.map((node) => {
    const children = prune(node.children || [])
    const direct = Number.isFinite(Number(node.productos_count)) ? Number(node.productos_count) : 0
    const desc   = children.reduce((s, c) => s + Number(c.total_productos ?? 0), 0)
    const total  = direct + desc
    if (total <= 0) return null
    return { ...node, children, total_productos: total }
  }).filter(Boolean)
  return prune(categoriasTree.value)
})

// Árbol inteligente: muestra solo la rama activa al profundizar
const sidebarCategoriasTree = computed(() => {
  const sel = String(filtros.categoria ?? '')
  if (!sel) return filteredCategoriasTree.value.map(r => ({ ...r, children: [] }))

  const containsDesc = (node, id) =>
    (node.children || []).some(c => String(c.id) === id || containsDesc(c, id))

  const pruneNode = (node) => {
    const nid = String(node.id)
    if (nid === sel || containsDesc(node, sel)) {
      return { ...node, children: (node.children || []).map(pruneNode) }
    }
    return { ...node, children: [] }
  }
  return filteredCategoriasTree.value.map(pruneNode)
})

const priceChanged = computed(() => {
  const min = typeof filtros.precio.min === 'number' ? filtros.precio.min : null
  const max = typeof filtros.precio.max === 'number' ? filtros.precio.max : null
  return (min !== null && min !== priceRange.min) || (max !== null && max !== priceRange.max)
})

const isRangoActive = (rango) => {
  if (!priceChanged.value) return false
  const rMax = rango.max === null ? priceRange.max : rango.max
  return filtros.precio.min === rango.min && filtros.precio.max === rMax
}

const appliedFiltersCount = computed(() => {
  let n = 0
  if (filtros.categoria)     n++
  if (filtros.marcas.length) n++
  if (priceChanged.value)    n++
  if (filtros.search)        n++
  if (filtros.promociones)   n++
  if (filtros.disponibilidad) n++
  if (filtros.orden)         n++
  return n
})

const priceModel = computed({
  get: () => [filtros.precio.min ?? priceRange.min, filtros.precio.max ?? priceRange.max],
  set: ([min, max] = []) => { filtros.precio.min = Number(min); filtros.precio.max = Number(max) },
})

const visibleMarcas = computed(() => showAllMarcas.value ? marcas.value : marcas.value.slice(0, 5))

// ── Precio helpers ────────────────────────────────────────────────────────────
const syncPriceInputWithFilters = () => {
  priceInput.min = String(filtros.precio.min ?? '')
  priceInput.max = String(filtros.precio.max ?? '')
}

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
  filtros.precio.min = min
  filtros.precio.max = max
  syncPriceInputWithFilters()
}

const applyRangoPrecio = (rango) => {
  const rMax = rango.max === null ? priceRange.max : rango.max
  applyPriceRange(rango.min, rMax)
  handleFilterChange()
}

const resetPrecio = () => {
  filtros.precio.min = priceRange.min
  filtros.precio.max = priceRange.max
  syncPriceInputWithFilters()
  handleFilterChange()
}

// ── Fetch ─────────────────────────────────────────────────────────────────────
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
    priceRange.min = min; priceRange.max = max
    filtros.precio.min = min; filtros.precio.max = max
    syncPriceInputWithFilters()
  } catch {
    priceRange.min = 0; priceRange.max = 0
    filtros.precio.min = null; filtros.precio.max = null
    syncPriceInputWithFilters()
  }
}

async function fetchProductos(append = false) {
  loading.value = true
  error.value = null
  try {
    if (!append) pagination.page = 1
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (filtros.search)        params.search   = filtros.search
    if (filtros.categoria)     params.categoria = filtros.categoria
    if (filtros.marcas.length) params.marca     = filtros.marcas.join(',')
    if (filtros.disponibilidad) params.estado_inventario = filtros.disponibilidad
    // "en_oferta" en el select actúa como filtro de oferta, no como ordering
    if (filtros.orden === 'en_oferta') {
      params.en_oferta = 'true'
    } else {
      if (filtros.orden)       params.ordering  = filtros.orden
      if (filtros.promociones) params.en_oferta = 'true'
    }
    // Solo enviar precio si difiere del rango completo (evita filtrar con [0,0] del init del slider)
    if (priceChanged.value) {
      if (typeof filtros.precio.min === 'number') params.precio_min = filtros.precio.min
      if (typeof filtros.precio.max === 'number') params.precio_max = filtros.precio.max
    }

    const res = await obtenerProductos(params)
    const raw = unwrapList(res.data)
    if (append) { productos.value.push(...raw) } else { productos.value = raw }
    const total = typeof res.data?.count === 'number' ? res.data.count : raw.length
    pagination.totalPages = Math.max(1, Math.ceil(total / pagination.pageSize))
  } catch (err) {
    console.error('Error cargando productos:', err)
    error.value = 'No se pudieron cargar los productos.'
    if (!append) { productos.value = []; pagination.totalPages = 1 }
  } finally {
    loading.value = false
  }
}

// ── Acciones ──────────────────────────────────────────────────────────────────
const loadMore = () => {
  if (loading.value || pagination.page >= pagination.totalPages) return
  pagination.page++
  fetchProductos(true)
}

const handleFilterChange = () => fetchProductos()

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
  filtros.marcas = filtros.marcas.includes(marcaId)
    ? filtros.marcas.filter(id => id !== marcaId)
    : [...filtros.marcas, marcaId]
  handleFilterChange()
}

const selectCategoria = (id) => {
  filtros.categoria = id
  handleFilterChange()
}

const handleAddToCart = (producto) => {
  const snapshot = { ...producto }
  const idx = productos.value.findIndex(p => p.id === producto.id)
  if (idx !== -1) {
    const newStock = Math.max(0, Number(productos.value[idx].stock) - 1)
    productos.value[idx] = { ...productos.value[idx], stock: newStock, estado_inventario: newStock === 0 ? 'agotado' : productos.value[idx].estado_inventario }
  }
  cartStore.agregar(snapshot)
}

const expandCategoryPath = (categoriaId) => {
  if (!categoriaId) { expandedCategoryIds.value = []; return }
  const byId = new Map(categorias.value.map(c => [String(c.id), c]))
  const next = new Set()
  // Expande la categoría seleccionada si tiene hijos
  if (categorias.value.some(c => String(c.parent) === String(categoriaId))) {
    next.add(String(categoriaId))
  }
  // Expande todos los ancestros
  let cur = byId.get(String(categoriaId))
  while (cur?.parent) { next.add(String(cur.parent)); cur = byId.get(String(cur.parent)) }
  expandedCategoryIds.value = Array.from(next)
}

const setupObserver = () => {
  if (observer) observer.disconnect()
  observer = new IntersectionObserver(
    (entries) => { if (entries[0].isIntersecting) loadMore() },
    { rootMargin: '300px' }
  )
  if (sentinel.value) observer.observe(sentinel.value)
}

const openFilters  = () => { showFiltersMobile.value = true }
const closeFilters = () => { showFiltersMobile.value = false }

const resetFilters = () => {
  filtros.search = ''
  filtros.categoria = ''
  filtros.marcas = []
  filtros.promociones = false
  filtros.disponibilidad = ''
  filtros.orden = ''
  filtros.precio.min = priceRange.min
  filtros.precio.max = priceRange.max
  syncPriceInputWithFilters()
  handleFilterChange()
}

const applyAndClose = () => { handleFilterChange(); closeFilters() }

// ── Watchers ──────────────────────────────────────────────────────────────────
watch(() => filtros.categoria, (id) => expandCategoryPath(id))

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  if (route.query.categoria)    filtros.categoria     = String(route.query.categoria)
  if (route.query.search)       filtros.search        = String(route.query.search)
  if (route.query.en_oferta)    filtros.promociones   = true
  if (route.query.orden)        filtros.orden         = String(route.query.orden)
  if (route.query.disponibilidad) filtros.disponibilidad = String(route.query.disponibilidad)

  obtenerPromoBanners({ ordering: 'orden' }).then(r => {
    const raw = Array.isArray(r.data?.results) ? r.data.results : Array.isArray(r.data) ? r.data : []
    shopBanner.value = raw.find(b => b.imagen_url) ?? null
  }).catch(() => {})

  // Precio primero para que el slider no contamine fetchProductos con [0,0]
  await fetchPriceRange()

  await Promise.all([fetchProductos(), fetchCategorias(), fetchMarcas()])
  await nextTick()
  setupObserver()
})

onUnmounted(() => { if (observer) observer.disconnect() })
</script>
