<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#060c18]">

    <!-- ─── HERO HEADER ────────────────────────────────────────────── -->
    <div class="relative overflow-hidden bg-gradient-to-br from-slate-900 via-slate-900 to-[#060c18] pb-0 pt-10">
      <!-- grid decoration -->
      <div class="pointer-events-none absolute inset-0 opacity-[0.035]"
           style="background-image:linear-gradient(rgba(255,255,255,0.6) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.6) 1px,transparent 1px);background-size:50px 50px"></div>
      <!-- radial glow -->
      <div class="pointer-events-none absolute inset-0"
           :style="currentCategory ? `background: radial-gradient(ellipse 60% 60% at 20% 50%, ${getConfig(currentCategory.nombre).color}18, transparent)` : ''"></div>

      <div class="relative mx-auto max-w-7xl px-4">
        <!-- Breadcrumb -->
        <nav class="mb-4 flex items-center gap-2 text-xs text-slate-500">
          <RouterLink to="/" class="hover:text-slate-300 transition-colors">Inicio</RouterLink>
          <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
          <RouterLink to="/categorias" class="hover:text-slate-300 transition-colors">Categorías</RouterLink>
          <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
          <span class="text-slate-300 font-medium truncate max-w-[180px]">{{ currentCategory?.nombre ?? '...' }}</span>
        </nav>

        <!-- Title row -->
        <div class="flex items-center gap-4 pb-8">
          <!-- Icon -->
          <div v-if="currentCategory"
               class="hidden sm:flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl"
               :style="{ background: `linear-gradient(135deg, ${getConfig(currentCategory.nombre).color}30, ${getConfig(currentCategory.nombre).color}0a)`,
                         border: `1px solid ${getConfig(currentCategory.nombre).color}40` }">
            <svg class="h-8 w-8" :style="{ color: getConfig(currentCategory.nombre).color }"
                 v-html="getConfig(currentCategory.nombre).iconPath"
                 fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true"></svg>
          </div>
          <div>
            <h1 class="text-2xl font-bold text-white sm:text-3xl">
              {{ currentCategory?.nombre ?? 'Cargando…' }}
            </h1>
            <p class="mt-1 text-sm text-slate-400">
              <template v-if="totalProductos !== null">
                {{ totalProductos }} producto{{ totalProductos !== 1 ? 's' : '' }}
              </template>
              <template v-else>Explorando…</template>
            </p>
          </div>
        </div>
      </div>

      <!-- ─── SUBCATEGORY PILLS NAV ──────────────────────────────── -->
      <div v-if="subcategorias.length" class="relative border-t border-slate-800">
        <!-- Fade edges -->
        <div class="pointer-events-none absolute left-0 top-0 bottom-0 z-10 w-8 bg-gradient-to-r from-slate-900 to-transparent"></div>
        <div class="pointer-events-none absolute right-0 top-0 bottom-0 z-10 w-8 bg-gradient-to-l from-slate-900 to-transparent"></div>

        <div class="scrollbar-hide flex gap-2 overflow-x-auto px-4 py-3 mx-auto max-w-7xl" style="-webkit-overflow-scrolling:touch">
          <!-- "Todos" pill -->
          <button
            @click="selectSub(null)"
            class="shrink-0 rounded-full border px-4 py-1.5 text-sm font-medium whitespace-nowrap transition-all duration-200"
            :class="selectedSubId === null
              ? 'border-cyan-500 bg-cyan-500/15 text-cyan-300'
              : 'border-slate-700 bg-slate-800/60 text-slate-400 hover:border-slate-500 hover:text-slate-200'"
          >
            Todos
          </button>
          <button
            v-for="sub in subcategorias"
            :key="sub.id"
            @click="selectSub(sub.id)"
            class="shrink-0 rounded-full border px-4 py-1.5 text-sm font-medium whitespace-nowrap transition-all duration-200"
            :class="selectedSubId === sub.id
              ? 'border-cyan-500 bg-cyan-500/15 text-cyan-300'
              : 'border-slate-700 bg-slate-800/60 text-slate-400 hover:border-slate-500 hover:text-slate-200'"
          >
            {{ sub.nombre }}
          </button>
        </div>
      </div>
    </div>

    <!-- ─── PRODUCT GRID ───────────────────────────────────────────── -->
    <div class="mx-auto max-w-7xl px-4 py-8">

      <!-- Loading skeleton initial -->
      <div v-if="loadingInitial" class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        <div v-for="i in 10" :key="i" class="aspect-[3/4] animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800"></div>
      </div>

      <!-- Empty state -->
      <div v-else-if="!loadingInitial && productos.length === 0" class="py-24 text-center">
        <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
          <svg class="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.182 16.318A4.486 4.486 0 0012.016 15a4.486 4.486 0 00-3.198 1.318M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75zm-.375 0h.008v.015h-.008V9.75zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75zm-.375 0h.008v.015h-.008V9.75z"/>
          </svg>
        </div>
        <p class="text-slate-500 dark:text-slate-400">No hay productos en esta categoría.</p>
        <button @click="selectSub(null)" v-if="selectedSubId" class="mt-4 text-sm text-cyan-600 hover:underline">
          Ver todos los productos
        </button>
      </div>

      <!-- Products -->
      <div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        <ProductCard
          v-for="producto in productos"
          :key="producto.id"
          :producto="producto"
        />
      </div>

      <!-- Load more sentinel -->
      <div ref="sentinel" class="h-4 mt-4"></div>

      <!-- Loading more spinner -->
      <div v-if="loadingMore" class="flex justify-center py-8">
        <div class="h-8 w-8 rounded-full border-2 border-slate-300 border-t-cyan-500 animate-spin"></div>
      </div>

      <!-- End of results -->
      <p v-if="!hasMore && productos.length > 0 && !loadingInitial" class="mt-8 text-center text-sm text-slate-400 dark:text-slate-600">
        Has visto todos los productos · {{ productos.length }} en total
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHead } from '@vueuse/head'
import { getCategoriasTree, getProductos } from '@/api/productos'
import ProductCard from '@/components/ProductCard.vue'

const route = useRoute()
const router = useRouter()

// ─── State ─────────────────────────────────────────────────────────────────
const categoriaId   = computed(() => Number(route.params.categoriaId))
const allCategories = ref([])
const productos     = ref([])
const totalProductos = ref(null)
const selectedSubId = ref(null)
const loadingInitial = ref(true)
const loadingMore    = ref(false)
const hasMore        = ref(true)
const page           = ref(1)
const PAGE_SIZE      = 20

const sentinel = ref(null)
let observer = null

// ─── Derived ────────────────────────────────────────────────────────────────
const currentCategory = computed(() =>
  allCategories.value.find((c) => c.id === categoriaId.value) ?? null
)
const subcategorias = computed(() => currentCategory.value?.subcategorias ?? [])

useHead(computed(() => ({
  title: currentCategory.value ? `${currentCategory.value.nombre} — Productos` : 'Categoría',
})))

// ─── Fetch categories tree ───────────────────────────────────────────────────
const fetchCategories = async () => {
  try {
    const { data } = await getCategoriasTree()
    allCategories.value = data
  } catch (e) {
    console.error('Error cargando categorías', e)
  }
}

// ─── Fetch products ──────────────────────────────────────────────────────────
const fetchProducts = async ({ reset = false } = {}) => {
  if (reset) {
    page.value = 1
    hasMore.value = true
    productos.value = []
    totalProductos.value = null
    loadingInitial.value = true
  } else {
    loadingMore.value = true
  }

  try {
    const params = {
      categoria: selectedSubId.value ?? categoriaId.value,
      page: page.value,
      page_size: PAGE_SIZE,
    }
    const { data } = await getProductos(params)
    const results = data.results ?? data
    totalProductos.value = data.count ?? results.length

    if (reset) {
      productos.value = results
    } else {
      productos.value.push(...results)
    }

    hasMore.value = !!data.next
  } catch (e) {
    console.error('Error cargando productos', e)
    hasMore.value = false
  } finally {
    loadingInitial.value = false
    loadingMore.value = false
  }
}

// ─── Subcategory selection ───────────────────────────────────────────────────
const selectSub = (id) => {
  selectedSubId.value = id
}

// ─── Infinite scroll ─────────────────────────────────────────────────────────
const setupObserver = () => {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && hasMore.value && !loadingMore.value && !loadingInitial.value) {
        page.value++
        fetchProducts()
      }
    },
    { rootMargin: '400px' }
  )
  if (sentinel.value) observer.observe(sentinel.value)
}

// ─── Watchers ────────────────────────────────────────────────────────────────
watch(categoriaId, () => {
  selectedSubId.value = null
  fetchProducts({ reset: true })
})

watch(selectedSubId, () => {
  fetchProducts({ reset: true })
})

// ─── Lifecycle ───────────────────────────────────────────────────────────────
onMounted(async () => {
  await fetchCategories()
  await fetchProducts({ reset: true })
  setupObserver()
})

onUnmounted(() => {
  observer?.disconnect()
})

// ─── Category icon/color config ──────────────────────────────────────────────
const CONFIGS = [
  {
    keys: ['audio', 'video', 'sonido', 'multimedia'],
    color: '#a855f7',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 11-.99-3.467l2.31-.66a2.25 2.25 0 001.632-2.163zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 01-.99-3.467l2.31-.66A2.25 2.25 0 009 15.553z"/>',
  },
  {
    keys: ['computadora', 'laptop', 'notebook'],
    color: '#3b82f6',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25A2.25 2.25 0 015.25 3h13.5A2.25 2.25 0 0121 5.25z"/>',
  },
  {
    keys: ['cómputo', 'computo', 'hardware', 'componente'],
    color: '#06b6d4',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25zm.75-12h9v9h-9v-9z"/>',
  },
  {
    keys: ['energía', 'energia', 'fuente', 'ups', 'batería', 'bateria', 'electr'],
    color: '#f59e0b',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>',
  },
  {
    keys: ['impresión', 'impresion', 'copiado', 'toner', 'tinta', 'escaner'],
    color: '#10b981',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M6.72 13.829c-.24.03-.48.062-.72.096m.72-.096a42.415 42.415 0 0110.56 0m-10.56 0L6.34 18m10.94-4.171c.24.03.48.062.72.096m-.72-.096L17.66 18m0 0l.229 2.523a1.125 1.125 0 01-1.12 1.227H7.231c-.662 0-1.18-.568-1.12-1.227L6.34 18m11.318 0h1.091A2.25 2.25 0 0021 15.75V9.456c0-1.081-.768-2.015-1.837-2.175a48.055 48.055 0 00-1.913-.247M6.34 18H5.25A2.25 2.25 0 013 15.75V9.456c0-1.081.768-2.015 1.837-2.175a48.056 48.056 0 011.913-.247m10.5 0a48.536 48.536 0 00-10.5 0m10.5 0V3.375c0-.621-.504-1.125-1.125-1.125h-8.25c-.621 0-1.125.504-1.125 1.125v3.659M18 10.5h.008v.008H18V10.5zm-3 0h.008v.008H15V10.5z"/>',
  },
  {
    keys: ['punto de venta', 'pos', 'caja', 'cobro'],
    color: '#f97316',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 013.75 9.375v-4.5zM3.75 14.625c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5a1.125 1.125 0 01-1.125-1.125v-4.5zM13.5 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0113.5 9.375v-4.5z"/>',
  },
  {
    keys: ['seguridad', 'vigilancia', 'camara', 'cámara', 'cctv'],
    color: '#ef4444',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m0-10.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.75c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.57-.598-3.75h-.152c-3.196 0-6.1-1.249-8.25-3.286zm0 13.036h.008v.008H12v-.008z"/>',
  },
  {
    keys: ['software', 'servicio', 'licencia'],
    color: '#8b5cf6',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M6.75 7.5l3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0021 18V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v12a2.25 2.25 0 002.25 2.25z"/>',
  },
]
const DEFAULT_CONFIG = {
  color: '#64748b',
  iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"/>',
}
const getConfig = (nombre) => {
  const lower = nombre.toLowerCase()
  for (const cfg of CONFIGS) {
    if (cfg.keys.some((k) => lower.includes(k))) return cfg
  }
  return DEFAULT_CONFIG
}
</script>

<style scoped>
.scrollbar-hide {
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
