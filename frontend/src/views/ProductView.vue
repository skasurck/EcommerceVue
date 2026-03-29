<template>
  <div>
    <div v-if="loading" class="animate-pulse mx-auto max-w-7xl px-4 py-6 space-y-4">
      <div class="h-8 bg-gray-300 rounded w-2/3"></div>
      <div class="h-96 bg-gray-300 rounded"></div>
      <div class="h-6 bg-gray-300 rounded w-1/3"></div>
      <div class="h-24 bg-gray-300 rounded"></div>
    </div>

    <div v-else-if="errorMsg" class="mx-auto max-w-3xl px-4 py-10">
      <div class="rounded-md border border-rose-200 bg-rose-50 p-4 text-rose-700">{{ errorMsg }}</div>
    </div>

    <div v-else-if="p" class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">

      <!-- ── Panel de administrador ── -->
      <div v-if="auth.hasAnyRole(['admin', 'super_admin'])" class="mb-5 rounded-lg border border-amber-300 bg-amber-50 p-4">
        <div class="flex items-center justify-between gap-2 cursor-pointer select-none" @click="adminPanelOpen = !adminPanelOpen">
          <div class="flex items-center gap-2">
            <span class="text-base">⚙️</span>
            <span class="font-semibold text-amber-800 text-sm">Panel de administrador</span>
            <span v-if="p.categorias_detalle?.length" class="text-xs text-amber-700">
              — {{ p.categorias_detalle.map(c => c.nombre).join(', ') }}
            </span>
          </div>
          <span class="text-amber-600 text-sm">{{ adminPanelOpen ? '▲ Cerrar' : '▼ Editar categoría' }}</span>
        </div>

        <div v-if="adminPanelOpen" class="mt-4 space-y-4">
          <!-- Categorías actuales -->
          <div v-if="p.categorias_detalle?.length" class="text-sm text-amber-700">
            <span class="font-medium">Categorías actuales:</span>
            <span v-for="(cat, i) in p.categorias_detalle" :key="cat.id" class="ml-1">
              {{ cat.nombre }}<span v-if="i < p.categorias_detalle.length - 1">,</span>
            </span>
          </div>
          <div v-else class="text-sm text-amber-700 italic">Sin categoría asignada</div>

          <!-- Selectores de nivel -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label class="block text-xs font-medium text-amber-800 mb-1">Categoría nivel 1</label>
              <select v-model="adminLevel1" @change="onAdminLevel1Change"
                class="w-full rounded border border-amber-300 bg-white px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400">
                <option value="">— Selecciona —</option>
                <option v-for="cat in adminCategories" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-amber-800 mb-1">Categoría nivel 2</label>
              <select v-model="adminLevel2" @change="onAdminLevel2Change" :disabled="!adminLevel2Options.length"
                class="w-full rounded border border-amber-300 bg-white px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 disabled:bg-amber-100 disabled:text-amber-400">
                <option value="">— Selecciona —</option>
                <option v-for="cat in adminLevel2Options" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-amber-800 mb-1">Categoría nivel 3</label>
              <select v-model="adminLevel3" :disabled="!adminLevel3Options.length"
                class="w-full rounded border border-amber-300 bg-white px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 disabled:bg-amber-100 disabled:text-amber-400">
                <option value="">— Selecciona —</option>
                <option v-for="cat in adminLevel3Options" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <button
              @click="saveAdminCategory"
              :disabled="!adminFinalCategoryId || adminSaving"
              class="rounded bg-amber-500 hover:bg-amber-600 disabled:opacity-50 px-4 py-2 text-sm font-semibold text-white transition">
              {{ adminSaving ? 'Guardando…' : 'Guardar categoría' }}
            </button>
            <RouterLink :to="`/admin/productos/editar/${p.id}`"
              class="rounded border border-amber-400 px-4 py-2 text-sm font-medium text-amber-800 hover:bg-amber-100 transition">
              Editar producto completo →
            </RouterLink>
            <span v-if="adminSaveMsg" class="text-sm" :class="adminSaveError ? 'text-red-600' : 'text-green-700'">{{ adminSaveMsg }}</span>
          </div>
        </div>
      </div>

        <!-- Main layout -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <!-- Left: gallery -->
          <div class="lg:col-span-6">
            <div class="flex gap-3">
              <!-- Thumbs -->
              <div class="hidden sm:flex flex-col gap-2 w-16 overflow-auto max-h-[420px] pr-1">
                <button
                  v-for="(t, i) in thumbs"
                  :key="i"
                  type="button"
                  class="relative rounded-md border overflow-hidden hover:ring-2 hover:ring-sky-500 focus:outline-none"
                  :class="selectedIndex === i ? 'ring-2 ring-sky-500 border-sky-500' : 'border-gray-300'"
                  @click="selectedIndex = i"
                >
                  <img :src="t" alt="miniatura" class="h-14 w-14 object-cover rounded" />
                </button>
              </div>
              <!-- Main image -->
              <div class="flex-1">
                <img :src="selectedImage || placeholder" :alt="p.nombre" class="w-full aspect-square object-contain bg-white rounded-lg border cursor-zoom-in" @click="openLightbox" />
                <button type="button" class="mt-2 block mx-auto text-center text-xs text-sky-700 hover:underline" @click="openLightbox">Haz clic para una vista completa</button>
              </div>
            </div>
          </div>

          <!-- Middle: info -->
          <div class="lg:col-span-4">
             <!-- Title -->
            <h1 class="text-2xl font-semibold text-gray-900 mb-3 leading-snug break-words">
              {{ p.nombre }}
              <span v-if="agotado" class="inline-block align-middle bg-red-600 text-white text-xs px-2 py-1 rounded ml-1">Agotado</span>
            </h1>

            <div
              v-if="categoryBreadcrumb.length > 0"
              class="mb-3 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs sm:text-sm text-gray-700"
            >
              <span class="font-semibold text-gray-800">Categorías:</span>
              <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
                <template v-for="(cat, idx) in categoryBreadcrumb" :key="idx">
                  <span
                    :class="[
                      'inline-flex items-center rounded-full px-2 py-1',
                      idx === categoryBreadcrumb.length - 1
                        ? 'bg-blue-50 border border-blue-200 text-blue-800'
                        : 'bg-gray-100'
                    ]"
                  >{{ cat }}</span>
                  <span v-if="idx < categoryBreadcrumb.length - 1" class="text-gray-400">&gt;</span>
                </template>
              </div>
            </div>
            <div v-else class="mb-3 text-xs sm:text-sm text-gray-600">Categoría: Sin categoría</div>

             <div class="space-y-2">
                <div v-if="hasDiscount" class="inline-flex items-center rounded-md bg-rose-600 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
                  Promoción
                </div>
                <div class="flex items-baseline gap-2">
                  <span v-if="hasDiscount" class="text-2xl font-semibold text-rose-600">-{{ discountPct }}%</span>
                  <div class="flex items-baseline gap-1 text-gray-900 font-semibold">
                    <span class="text-3xl leading-none">{{ priceMajor }}</span>
                    <span class="relative -top-1 text-lg">{{ priceSeparator }}{{ priceMinor }}</span>
                  </div>
                </div>
                <div v-if="hasDiscount && listPriceFormatted" class="flex items-center gap-2 text-sm text-gray-500">
                  <span>Precio de lista:</span>
                  <span class="line-through">{{ listPriceFormatted }}</span>
                  <span class="inline-flex h-4 w-4 items-center justify-center rounded-full border border-gray-400 text-[10px]">i</span>
                </div>
                <p v-if="hasDiscount" class="text-xs font-medium text-emerald-700">Ahorros: {{ savingsFormatted }}</p>
              </div>
            <!-- Attributes quick picks -->
            <div v-if="colors.length" class="mt-3">
              <div class="text-sm text-gray-700 mb-1">Color</div>
              <div class="flex gap-2">
                <span v-for="(c,i) in colors" :key="i" class="h-7 w-7 rounded-full border" :style="{ backgroundColor: c }"></span>
              </div>
            </div>
            <div v-if="tamanos.length" class="mt-3">
              <div class="text-sm text-gray-700 mb-1">Tamaño</div>
              <div class="flex flex-wrap gap-2">
                <span v-for="(t,i) in tamanos" :key="i" class="px-2 py-1 rounded border text-sm">{{ t }}</span>
              </div>
            </div>
            <!-- Tier pricing -->
            <div v-if="tienePreciosEscalonados" class="mt-4">
              <h3 class="text-sm font-medium text-gray-900 mb-2">Precios por volumen</h3>
              <table class="w-full border text-sm">
                <thead class="bg-gray-50 text-gray-700">
                  <tr>
                    <th class="border p-2 text-left">Desde</th>
                    <th class="border p-2 text-left">Precio unitario</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(tier,idx) in p.precios_escalonados" :key="idx">
                    <td class="border p-2">{{ tier.cantidad_minima }}</td>
                    <td class="border p-2">{{ fmt(tier.precio_unitario) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>

          <!-- Right: buy box -->
          <aside class="lg:col-span-2">
            <div class="sticky top-4 rounded-lg border p-4 shadow-sm space-y-5">
              
              <div class="text-gray-900 font-semibold">
                <span class="text-xl">{{ priceMajor }}</span><span class="align-top text-[11px]">{{ priceMinor }}</span>
              </div>

              <div class=" text-sm text-gray-700">
                <p class="text-xs font-semibold uppercase tracking-wide text-sky-700">Entrega aproximada</p>
                <p class="text-xs font-semibold text-gray-900">{{ entregaAproxTexto }}</p>
                <!-- <p class="text-xs text-gray-600">Envío estándar estimado en {{ SHIPPING_ESTIMATE_DAYS }} días.</p>-->
              </div>

              <div
                v-if="showShipToBlock"
                class="flex border border bg-white/70 p-3 text-sm text-gray-700"
              >
                <svg
                  aria-hidden="true"
                  class="h-5 w-5 text-gray-500 mt-0.5 flex-shrink-0"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 11a3 3 0 100-6 3 3 0 000 6z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 21c-4.5-5-6-7.5-6-10.5a6 6 0 1112 0c0 3-1.5 5.5-6 10.5z" />
                </svg>
                <div class="min-w-0 leading-tight">
                  <p class="text-sm font-medium text-gray-900">Enviar a {{ shippingFirstName }}</p>
                  <p class="text-xs text-gray-600 truncate">{{ shippingAddressPreview }}</p>
                </div>
              </div>

              <p class="mt-1 text-sm" :class="agotado ? 'text-rose-700' : 'text-emerald-700'">
                {{ agotado ? 'No disponible' : 'Disponible' }}
              </p>

              <label class="mt-3 block text-sm text-gray-700">Cantidad</label>
              <select v-model.number="cantidad" :disabled="agotado" class="mt-1 w-full rounded border px-2 py-1">
                <option v-for="n in qtyOptions" :key="n" :value="n">{{ n }}</option>
              </select>

              <button
                class="mt-3 w-full rounded bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-medium py-2"
                :disabled="agotado"
                @click="agregar"
              >
                Agregar al Carrito
              </button>
              <button
                class="mt-2 w-full rounded bg-orange-500 hover:bg-orange-600 text-white font-medium py-2"
                :disabled="agotado"
                @click="comprarAhora"
              >
                Comprar ahora
              </button>

              <!-- Wishlist button -->
              <button
                v-if="auth.isAuthenticated"
                type="button"
                class="mt-2 w-full rounded border py-2 text-sm font-medium flex items-center justify-center gap-2 transition-colors"
                :class="isFavorito
                  ? 'border-rose-300 bg-rose-50 text-rose-600 hover:bg-rose-100'
                  : 'border-gray-300 text-gray-600 hover:border-rose-300 hover:text-rose-500'"
                @click="toggleFav"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" :fill="isFavorito ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                {{ isFavorito ? 'En tu lista de deseos' : 'Agregar a lista de deseos' }}
              </button>

              <p v-if="stockLow" class="mt-2 text-xs font-medium text-amber-700">Quedan {{ p.stock }} en inventario</p>

            </div>
            
          </aside>
        </div>

        <!-- Full-width details below grid -->
        <section class="mt-8 space-y-6">
          <!-- Long description -->
          <div v-if="p.descripcion_larga" class="border rounded-lg p-4 bg-white">
            <h2 class="text-lg font-semibold text-gray-900 mb-2">Descripción</h2>
            <div class="text-gray-700 whitespace-pre-wrap break-words" v-html="p.descripcion_larga"></div>
          </div>

          <!-- Specs / meta info -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="rounded-lg border p-4 bg-white">
              <h3 class="text-sm font-medium text-gray-900 mb-1">Categoría</h3>
              <p class="text-sm text-gray-700">{{ categoryName || 'Sin categoría' }}</p>
            </div>
            <div class="rounded-lg border p-4 bg-white">
              <h3 class="text-sm font-medium text-gray-900 mb-1">Marca</h3>
              <p class="text-sm text-gray-700">{{ p.marca || '—' }}</p>
            </div>
            <div class="rounded-lg border p-4 bg-white">
              <h3 class="text-sm font-medium text-gray-900 mb-1">Estado inventario</h3>
              <p class="text-sm text-gray-700">{{ p.estado_inventario || (agotado ? 'Agotado' : 'En stock') }}</p>
            </div>
          </div>

          <!-- Attributes -->
          <div v-if="Object.keys(p.atributos || {}).length" class="rounded-lg border p-4 bg-white">
            <h3 class="text-sm font-medium text-gray-900 mb-2">Atributos</h3>
            <div class="grid sm:grid-cols-2 gap-2 text-sm text-gray-700">
              <template v-for="(val, key) in p.atributos" :key="key">
                <div>
                  <span class="font-medium">{{ key }}:</span>
                  <span>
                    <template v-if="Array.isArray(val)">{{ val.join(', ') }}</template>
                    <template v-else>{{ val }}</template>
                  </span>
                </div>
              </template>
            </div>
          </div>
        </section>

        <section class="mt-10 space-y-8" v-if="hasAnyRelacionados">
          <div v-if="relacionadosLoading || relacionados.length">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-semibold text-gray-900">Productos relacionados</h2>
              <span v-if="relacionadosLoading" class="text-sm text-gray-500">Cargando...</span>
            </div>
            <div v-if="relacionadosLoading" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              <div
                v-for="i in 4"
                :key="`related-skeleton-${i}`"
                class="h-64 rounded-lg border border-dashed border-gray-200 bg-white animate-pulse"
              ></div>
            </div>
            <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              <ProductCard v-for="rel in relacionados" :key="rel.id" :producto="rel" />
            </div>
          </div>

          <div v-if="relacionadosCategoriaLoading || relacionadosCategoria.length">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-semibold text-gray-900">Más de esta categoría</h2>
              <span v-if="relacionadosCategoriaLoading" class="text-sm text-gray-500">Cargando...</span>
            </div>
            <div v-if="relacionadosCategoriaLoading" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              <div
                v-for="i in 4"
                :key="`related-category-skeleton-${i}`"
                class="h-64 rounded-lg border border-dashed border-gray-200 bg-white animate-pulse"
              ></div>
            </div>
            <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              <ProductCard v-for="rel in relacionadosCategoria" :key="`cat-${rel.id}`" :producto="rel" />
            </div>
          </div>
        </section>
      </div>

      <!-- Lightbox overlay -->
      <div v-if="lightboxOpen" class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center" @click.self="closeLightbox">
        <button class="absolute top-4 right-4 text-white text-2xl" @click="closeLightbox">×</button>
        <div class="relative max-w-5xl w-full px-4">
          <img :src="selectedImage || placeholder" :alt="p?.nombre || 'Imagen'" class="w-full max-h-[85vh] object-contain rounded" />
          <div class="absolute inset-y-0 left-0 flex items-center">
            <button class="p-3 text-white/80 hover:text-white" @click.stop="prevImage" aria-label="Anterior">‹</button>
          </div>
          <div class="absolute inset-y-0 right-0 flex items-center">
            <button class="p-3 text-white/80 hover:text-white" @click.stop="nextImage" aria-label="Siguiente">›</button>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { obtenerProducto, obtenerProductos } from '@/services/api'
import { getCategorias } from '@/api/productos'
import { useHead } from '@vueuse/head'
import { useCarritoStore } from '@/stores/carrito'
import { useAuthStore } from '@/stores/auth'
import { useBreadcrumbStore } from '@/stores/breadcrumb'
import { useWishlistStore } from '@/stores/wishlist'
import ProductCard from '@/components/ProductCard.vue'
import api from '@/axios'

const route = useRoute()
const producto = ref(null)
const cantidad = ref(1)
const carrito = useCarritoStore()
const auth = useAuthStore()
const wishlist = useWishlistStore()
const loading = ref(true)
const errorMsg = ref('')

// ── Admin: editar categoría ──
const adminPanelOpen = ref(false)
const adminCategories = ref([])   // árbol raíz (nivel 1)
const adminLevel1 = ref('')
const adminLevel2 = ref('')
const adminLevel3 = ref('')
const adminSaving = ref(false)
const adminSaveMsg = ref('')
const adminSaveError = ref(false)

watch(adminPanelOpen, (open) => { if (open) fetchAdminCategories() })

const adminLevel2Options = computed(() => {
  if (!adminLevel1.value) return []
  const cat = adminCategories.value.find(c => c.id === adminLevel1.value)
  return cat?.subcategorias ?? []
})
const adminLevel3Options = computed(() => {
  if (!adminLevel2.value) return []
  const cat = adminLevel2Options.value.find(c => c.id === adminLevel2.value)
  return cat?.subcategorias ?? []
})
const adminFinalCategoryId = computed(() => adminLevel3.value || adminLevel2.value || adminLevel1.value)

const onAdminLevel1Change = () => { adminLevel2.value = ''; adminLevel3.value = '' }
const onAdminLevel2Change = () => { adminLevel3.value = '' }

const fetchAdminCategories = async () => {
  if (adminCategories.value.length) return
  try {
    const { data } = await api.get('all-categories/')
    adminCategories.value = Array.isArray(data) ? data : []
  } catch { /* silencioso */ }
}

const saveAdminCategory = async () => {
  if (!adminFinalCategoryId.value) return
  adminSaving.value = true
  adminSaveMsg.value = ''
  adminSaveError.value = false
  try {
    await api.post(`productos/${producto.value?.id}/apply-category/`, {
      category_ids: [adminFinalCategoryId.value]
    })
    // Recargar producto para reflejar la nueva categoría
    const { data } = await obtenerProducto(route.params.id)
    producto.value = data
    adminSaveMsg.value = '✓ Categoría guardada'
    adminLevel1.value = ''
    adminLevel2.value = ''
    adminLevel3.value = ''
  } catch (e) {
    adminSaveError.value = true
    adminSaveMsg.value = e?.response?.data?.detail || 'Error al guardar'
  } finally {
    adminSaving.value = false
    setTimeout(() => { adminSaveMsg.value = '' }, 3000)
  }
}
const relacionados = ref([])
const relacionadosLoading = ref(false)
const relacionadosCategoria = ref([])
const relacionadosCategoriaLoading = ref(false)
const categoriasIndex = ref({})
const RELACIONADOS_LIMIT = 8
const VISIT_HISTORY_KEY = 'product_visit_history'
const MAX_HISTORY_ITEMS = 20
const categoryNameFromId = (maybeId) => {
  if (maybeId == null) return ''
  const key = String(
    typeof maybeId === 'object'
      ? maybeId.id ?? maybeId.pk ?? maybeId.categoria ?? maybeId.category ?? ''
      : maybeId
  ).trim()
  if (!key) return ''
  const entry = categoriasIndex.value[key] || categoriasIndex.value[Number(key)]
  if (!entry) return ''
  const val = entry.nombre ?? entry.name ?? entry.titulo ?? entry.title ?? entry.slug ?? ''
  return val ? String(val).trim() : ''
}
const normalizeCategoryName = (val) => {
  if (val == null) return ''
  if (typeof val === 'object' && !Array.isArray(val)) {
    const fromName = normalizeCategoryName(val.nombre ?? val.name ?? val.titulo ?? val.title)
    if (fromName) return fromName
    const fromId = categoryNameFromId(val.id ?? val.pk ?? val.categoria ?? val.category ?? '')
    if (fromId) return fromId
    return ''
  }
  const raw = String(val).trim()
  if (!raw) return ''
  const mapped = categoryNameFromId(raw)
  if (mapped) return mapped
  if (/^\d+$/.test(raw)) return ''
  return raw
}

const categoryBreadcrumb = computed(() => {
  const currentProduct = p.value
  if (!currentProduct) return []

  let path = []

  // Prioridad 0: Ruta completa entregada por la API (incluye padres/hijos)
  if (Array.isArray(currentProduct.categoria_ruta) && currentProduct.categoria_ruta.length > 0) {
    path = currentProduct.categoria_ruta.map((cat) => normalizeCategoryName(cat.nombre ?? cat)).filter(Boolean)
  }
  // Prioridad 1: Usar el array de categorías detallado si existe
  else if (Array.isArray(currentProduct.categorias_detalle) && currentProduct.categorias_detalle.length > 0) {
    path = currentProduct.categorias_detalle.map(cat => normalizeCategoryName(cat.nombre)).filter(Boolean)
  }
  // Prioridad 2: Usar la categoría principal detallada y sus padres
  else if (currentProduct.categoria_detalle && typeof currentProduct.categoria_detalle === 'object' && currentProduct.categoria_detalle.nombre) {
    let current = currentProduct.categoria_detalle
    const tempPath = []
    while (current) {
      const name = normalizeCategoryName(current.nombre)
      if (name) tempPath.unshift(name)
      // Asumiendo que el padre es un objeto anidado o null
      current = current.parent 
    }
    path = tempPath
  }
  // Fallback a la lógica anterior si los nuevos campos no están
  else if (currentProduct.categoria && typeof currentProduct.categoria === 'object' && currentProduct.categoria.nombre) {
    let current = currentProduct.categoria
    const tempPath = []
    while (current) {
      const name = normalizeCategoryName(current.nombre)
      if (name) tempPath.unshift(name)
      current = current.padre
    }
    path = tempPath
  }
  else if (Array.isArray(currentProduct.categorias) && currentProduct.categorias.length > 0) {
    path = currentProduct.categorias.map(c => normalizeCategoryName(c.nombre ?? c)).filter(Boolean)
  }
  else {
    const mainName = normalizeCategoryName(
      currentProduct.categoria_nombre || currentProduct.categoriaNombre || currentProduct.nombre_categoria || currentProduct.nombreCategoria || currentProduct.categoria || currentProduct.Categoria
    )
    if (mainName) {
      path.push(mainName)
    }
  }

  // Quitar duplicados
  return [...new Set(path)]
})
const categoryName = computed(() => {
  if (categoryBreadcrumb.value.length) {
    return categoryBreadcrumb.value[categoryBreadcrumb.value.length - 1]
  }
  const primary = getPrimaryCategoryId(producto.value)
  return categoryNameFromId(primary) || ''
})

const agregar = async () => {
  if (producto.value) {
    const qty = cantidad.value
    await carrito.agregar(producto.value, qty)
    producto.value.stock = Math.max(producto.value.stock - qty, 0)
    cantidad.value = producto.value.stock > 0 ? 1 : 0
  }
}

const comprarAhora = async () => {
  await agregar()
  // Aquí podrías redirigir a checkout
}

const getPrimaryCategoryId = (detail) => {
  if (!detail) return null
  const pickId = (val) => {
    if (!val) return null
    if (typeof val === 'object') return val.id ?? val.pk ?? val.categoria ?? val.category ?? null
    return val
  }
  if (Array.isArray(detail.categoria_ruta) && detail.categoria_ruta.length) {
    const deepest = detail.categoria_ruta[detail.categoria_ruta.length - 1]
    const id = pickId(deepest?.id ?? deepest)
    if (id) return id
  }
  const mainCandidates = [
    detail.categoria_id,
    detail.categoriaId,
    detail.categoria,
    detail.category_id,
    detail.categoryId
  ]
  for (const candidate of mainCandidates) {
    const id = pickId(candidate)
    if (id) return id
  }
  if (Array.isArray(detail.categorias) && detail.categorias.length) {
    for (const cat of detail.categorias) {
      const candidate = pickId(cat)
      if (candidate) return candidate
    }
  }
  return null
}

const canUseLocalStorage = () => typeof window !== 'undefined' && !!window.localStorage
const loadVisitHistory = () => {
  if (!canUseLocalStorage()) return []
  try {
    const raw = localStorage.getItem(VISIT_HISTORY_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed
      .map((entry) => ({
        id: entry?.id,
        categoriaId: entry?.categoriaId ?? null,
        ts: Number(entry?.ts) || 0
      }))
      .filter((entry) => entry.id != null)
      .sort((a, b) => b.ts - a.ts)
  } catch {
    return []
  }
}
const getHistoryCategory = (currentProductId) => {
  const history = loadVisitHistory()
  const found = history.find((entry) => entry.categoriaId && entry.id !== currentProductId)
  return found?.categoriaId ?? null
}
const persistVisitHistory = (entries) => {
  if (!canUseLocalStorage()) return
  try {
    localStorage.setItem(VISIT_HISTORY_KEY, JSON.stringify(entries.slice(0, MAX_HISTORY_ITEMS)))
  } catch (err) {
    console.warn('No se pudo guardar historial de visitas', err)
  }
}
const registerProductVisit = (detail) => {
  const id = detail?.id
  if (!id) return
  const categoriaId = getPrimaryCategoryId(detail)
  const history = loadVisitHistory().filter((entry) => entry.id !== id)
  history.unshift({ id, categoriaId: categoriaId ?? null, ts: Date.now() })
  persistVisitHistory(history)
}
const buildRecommendationCategories = (primaryCategoryId, currentProductId) => {
  const history = loadVisitHistory().filter((entry) => entry.id !== currentProductId)
  const ordered = []
  const seen = new Set()
  const pushCat = (catId) => {
    if (!catId || seen.has(catId)) return
    seen.add(catId)
    ordered.push(catId)
  }
  pushCat(primaryCategoryId)
  history.forEach((entry) => pushCat(entry.categoriaId))
  return ordered
}



const fetchRelatedProducts = async (categoriaId, currentProductId) => {
  relacionados.value = []
  let categoryOrder = buildRecommendationCategories(categoriaId, currentProductId).filter(Boolean)
  if (!categoryOrder.length) {
    const fallbackCat = getHistoryCategory(currentProductId)
    if (fallbackCat) categoryOrder = [fallbackCat]
  }
  // Fallback generico si no hay categorias en historial
  if (!categoryOrder.length) {
    relacionadosLoading.value = true
    try {
      const { data } = await obtenerProductos({ page_size: RELACIONADOS_LIMIT + 1 })
      const items = Array.isArray(data) ? data : data?.results || []
      relacionados.value = items.filter((item) => item.id !== currentProductId).slice(0, RELACIONADOS_LIMIT)
    } catch (err) {
      console.error('No se pudieron cargar productos relacionados', err)
      relacionados.value = []
    } finally {
      relacionadosLoading.value = false
    }
    return
  }

  relacionadosLoading.value = true
  const seen = new Set([currentProductId])
  const collected = []
  try {
    for (const cat of categoryOrder) {
      const { data } = await obtenerProductos({ categoria: cat, page_size: RELACIONADOS_LIMIT })
      const items = Array.isArray(data) ? data : data?.results || []
      for (const item of items) {
        if (seen.has(item.id)) continue
        seen.add(item.id)
        collected.push(item)
        if (collected.length >= RELACIONADOS_LIMIT) break
      }
      if (collected.length >= RELACIONADOS_LIMIT) break
    }
    relacionados.value = collected
  } catch (err) {
    console.error('No se pudieron cargar productos relacionados', err)
    relacionados.value = []
  } finally {
    relacionadosLoading.value = false
  }
}

const fetchCategoryProducts = async (categoriaId, currentProductId) => {
  relacionadosCategoria.value = []
  const targetCategory = categoriaId || getHistoryCategory(currentProductId)
  if (!targetCategory) return
  relacionadosCategoriaLoading.value = true
  try {
    const { data } = await obtenerProductos({ categoria: targetCategory, page_size: RELACIONADOS_LIMIT })
    const items = Array.isArray(data) ? data : data?.results || []
    const exclude = new Set([currentProductId, ...relacionados.value.map((item) => item.id)])
    relacionadosCategoria.value = items.filter((item) => !exclude.has(item.id)).slice(0, RELACIONADOS_LIMIT)
  } catch (err) {
    console.error('No se pudieron cargar productos de la misma categoria', err)
    relacionadosCategoria.value = []
  } finally {
    relacionadosCategoriaLoading.value = false
  }
}

const fetchCategoriasIndex = async () => {
  if (Object.keys(categoriasIndex.value).length) return
  try {
    const { data } = await getCategorias()
    const items = Array.isArray(data) ? data : data?.results || []
    const map = {}
    items.forEach((cat) => {
      if (cat?.id == null) return
      map[String(cat.id)] = cat
    })
    categoriasIndex.value = map
  } catch (err) {
    console.error('No se pudieron cargar categorias', err)
  }
}

// Cargar producto
onMounted(async () => {
  const categoriasPromise = fetchCategoriasIndex()
  try {
    const { data } = await obtenerProducto(route.params.id)
    producto.value = data
    registerProductVisit(data)
    useBreadcrumbStore().setLabel(data.nombre)

    // Meta-tags dinamicos
    useHead({
      title: data.nombre,
      meta: [
        { name: 'description', content: (data.descripcion_larga || '').slice(0, 155) }
      ]
    })
    const primaryCat = getPrimaryCategoryId(data)
    await categoriasPromise
    await fetchRelatedProducts(primaryCat, data.id)
    await fetchCategoryProducts(primaryCat, data.id)
  } catch (e) {
    console.error(e)
    errorMsg.value = 'No se pudo cargar el producto.'
  } finally {
    loading.value = false
  }
})

// --- Derived/computed helpers ---
const collapseAttributeValues = (buckets) => {
  const normalized = {}
  for (const [name, list] of Object.entries(buckets)) {
    const clean = list.map((v) => (v == null ? '' : String(v).trim())).filter(Boolean)
    if (!clean.length) continue
    normalized[name] = clean.length === 1 ? clean[0] : clean
  }
  return normalized
}

const normalizeAttributes = (detail, fallback = {}) => {
  if (Array.isArray(detail) && detail.length) {
    const buckets = {}
    for (const item of detail) {
      if (!item) continue
      const nombre = String(item?.atributo?.nombre ?? item?.nombre ?? '').trim()
      if (!nombre) continue
      const val = item?.valor ?? item?.value ?? ''
      if (Array.isArray(val)) {
        val.forEach((single) => {
          const normalized = single == null ? '' : String(single).trim()
          if (!normalized) return
          const bucket = buckets[nombre] || (buckets[nombre] = [])
          bucket.push(normalized)
        })
      } else {
        const normalized = val == null ? '' : String(val).trim()
        if (!normalized) continue
        const bucket = buckets[nombre] || (buckets[nombre] = [])
        bucket.push(normalized)
      }
    }
    return collapseAttributeValues(buckets)
  }

  if (typeof fallback === 'object' && fallback && !Array.isArray(fallback)) {
    return collapseAttributeValues(
      Object.entries(fallback).reduce((acc, [name, value]) => {
        if (!name) return acc
        const key = String(name).trim()
        if (!key) return acc
        if (Array.isArray(value)) acc[key] = value
        else if (value != null && value !== '') acc[key] = [value]
        return acc
      }, {})
    )
  }

  return {}
}

const p = computed(() => {
  const pr = producto.value || {}
  const attrDetail = Array.isArray(pr.atributos_detalle) ? pr.atributos_detalle : []
  const attrFallback = pr.atributos ?? pr.Atributos ?? {}
  return {
    id: pr.id,
    nombre: pr.nombre ?? '',
    descripcion_corta: pr.descripcion_corta ?? '',
    descripcion_larga: pr.descripcion_larga ?? '',
    precio_normal: pr.precio_normal ?? pr.precio ?? null,
    precio_rebajado: pr.precio_rebajado ?? null,
    imagen_principal: pr.imagen_principal ?? null,
    imagenes: pr.galeria ?? pr.imagenes ?? pr['Imagen productos'] ?? [],
    atributos: normalizeAttributes(attrDetail, attrFallback),
    atributos_detalle: attrDetail,
    stock: pr.stock ?? 0,
    categoria: pr.categoria ?? pr.Categoria ?? '',
    categoria_ruta: pr.categoria_ruta ?? [],
    categoria_detalle: pr.categoria_detalle ?? null,
    categorias_detalle: pr.categorias_detalle ?? [],
    marca: pr.marca ?? pr.Marca ?? '',
    estado_inventario: pr.estado_inventario ?? pr['Estado inventario'] ?? pr.estado ?? '',
    precios_escalonados: pr.precios_escalonados ?? [],
  }
})

const placeholder =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600"><rect width="100%" height="100%" fill="#ffffff"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#9ca3af" font-family="Arial" font-size="18">Sin imagen</text></svg>`
  )

// Build absolute media URLs from relative API paths
const MEDIA_BASE = (import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? 'http://localhost:8000' : (typeof window !== 'undefined' ? window.location.origin : ''))).replace(/\/+$/, '')
const toMedia = (u) => {
  if (!u) return null
  if (/^(data:|blob:|https?:)/i.test(u)) return u
  if (u.startsWith('/media/')) return `${MEDIA_BASE}${u}`
  return `${MEDIA_BASE}/media/${u.replace(/^\/+/, '')}`
}

const num = (v) => {
  if (v === undefined || v === null) return null
  if (typeof v === 'number') return Number.isFinite(v) ? v : null
  if (typeof v === 'string') {
    const cleaned = v.replace(/[^0-9.,-]/g, '').replace(',', '.').trim()
    if (cleaned === '') return null
    const n = Number(cleaned)
    return Number.isFinite(n) ? n : null
  }
  return null
}

const listPrice = computed(() => num(p.value.precio_normal))
const salePrice = computed(() => num(p.value.precio_rebajado))
const displayPrice = computed(() => (salePrice.value ?? listPrice.value ?? 0))
const hasDiscount = computed(
  () => listPrice.value != null && salePrice.value != null && salePrice.value > 0 && salePrice.value < listPrice.value
)
const discountPct = computed(() => (hasDiscount.value ? Math.round((1 - salePrice.value / listPrice.value) * 100) : 0))
const savings = computed(() => (hasDiscount.value ? listPrice.value - salePrice.value : 0))

const fmt = (n) => new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 2 }).format(n ?? 0)
const listPriceFormatted = computed(() => (listPrice.value != null ? fmt(listPrice.value) : ''))
const priceFormatted = computed(() => fmt(displayPrice.value))
const savingsFormatted = computed(() => (savings.value ? fmt(savings.value) : ''))

const priceMajor = computed(() => {
  const f = priceFormatted.value
  const m = f.match(/^(.*?)([.,](\d{2}))$/)
  return m ? m[1] : f
})
const priceSeparator = computed(() => {
  const f = priceFormatted.value
  const m = f.match(/([.,])\d{2}$/)
  return m ? m[1] : ''
})
const priceMinor = computed(() => {
  const f = priceFormatted.value
  const m = f.match(/([.,])(\d{2})$/)
  return m ? m[2] : '00'
})

const thumbs = computed(() => {
  const arr = []
  if (p.value.imagen_principal) arr.push(toMedia(p.value.imagen_principal))
  if (Array.isArray(p.value.imagenes)) {
    for (const it of p.value.imagenes) {
      const u = typeof it === 'string' ? it : it?.imagen || it?.url || it?.image || it?.src
      const full = toMedia(u)
      if (full) arr.push(full)
    }
  }
  return arr.length ? arr : [placeholder]
})
const selectedIndex = ref(0)
const selectedImage = computed(() => thumbs.value[selectedIndex.value] || null)
watch(() => thumbs.value, () => { selectedIndex.value = 0 }, { immediate: true })

// Lightbox controls
const lightboxOpen = ref(false)
const openLightbox = () => { if (thumbs.value.length) lightboxOpen.value = true }
const closeLightbox = () => { lightboxOpen.value = false }
const prevImage = () => { if (!thumbs.value.length) return; selectedIndex.value = (selectedIndex.value - 1 + thumbs.value.length) % thumbs.value.length }
const nextImage = () => { if (!thumbs.value.length) return; selectedIndex.value = (selectedIndex.value + 1) % thumbs.value.length }

const onKey = (e) => {
  if (!lightboxOpen.value) return
  if (e.key === 'Escape') closeLightbox()
  else if (e.key === 'ArrowLeft') prevImage()
  else if (e.key === 'ArrowRight') nextImage()
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))

const COLOR_ALIASES = Object.freeze({
  blanco: '#ffffff',
  negro: '#000000',
  gris: '#9ca3af',
  plata: '#d1d5db',
  rojo: '#ef4444',
  azul: '#1d4ed8',
  verde: '#22c55e',
  amarillo: '#facc15',
  naranja: '#fb923c',
  morado: '#a855f7',
  violet: '#8b5cf6',
  violeta: '#8b5cf6',
  rosa: '#ec4899',
  marron: '#92400e',
  cafe: '#6b4423',
  beige: '#f5f5dc',
})
const CSS_HEX_COLOR = /^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i
const CSS_FUNCTION_COLOR = /^(?:rgba?|hsla?)\(/i
const CSS_KEYWORD_COLOR = /^[a-z]+$/i

const normalizeColorValue = (value) => {
  if (value == null) return ''
  if (typeof value === 'object' && !Array.isArray(value)) {
    return normalizeColorValue(value.valor ?? value.value ?? value.nombre ?? '')
  }
  const raw = String(value).trim()
  if (!raw) return ''
  const lower = raw.toLowerCase()
  if (COLOR_ALIASES[lower]) return COLOR_ALIASES[lower]
  if (CSS_HEX_COLOR.test(raw) || CSS_FUNCTION_COLOR.test(raw) || CSS_KEYWORD_COLOR.test(raw)) return raw
  return ''
}

const collectColorTokens = (input) => {
  const tokens = []
  const pushValue = (val) => {
    if (val == null) return
    if (Array.isArray(val)) {
      val.forEach(pushValue)
      return
    }
    if (typeof val === 'object') {
      pushValue(val.valor ?? val.value ?? val.nombre ?? '')
      return
    }
    if (typeof val === 'string') {
      val
        .split(',')
        .map((piece) => piece.trim())
        .filter(Boolean)
        .forEach((piece) => tokens.push(piece))
      return
    }
    tokens.push(String(val))
  }
  pushValue(input)
  return tokens
}

const colors = computed(() => {
  const at = p.value.atributos || {}
  const raw = at.color || at.Color || at.colores || at.Colores
  if (!raw) return []
  return collectColorTokens(raw).map(normalizeColorValue).filter(Boolean)
})
const tamanos = computed(() => {
  const at = p.value.atributos || {}
  const raw = at.tamano || at.Tamano || at.talla || at.Talla || at.size || at.Size
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (typeof raw === 'string') return raw.split(',').map((s) => s.trim()).filter(Boolean)
  return []
})

const agotado = computed(() => (p.value?.stock ?? 0) <= 0)
const stockLow = computed(() => !agotado.value && Number(p.value.stock) < 10)
const qtyOptions = computed(() => {
  const s = Number(p.value.stock) || 0
  const max = Math.min(Math.max(s, 1), 10)
  return Array.from({ length: max }, (_, i) => i + 1)
})

const tienePreciosEscalonados = computed(() => {
  const pe = p.value.precios_escalonados
  return Array.isArray(pe) ? pe.length > 0 : !!pe
})

const SHIPPING_ESTIMATE_DAYS = 7
const entregaAproxTexto = computed(() => {
  const target = new Date()
  target.setDate(target.getDate() + SHIPPING_ESTIMATE_DAYS)
  const formatted = new Intl.DateTimeFormat('es-MX', { day: 'numeric', month: 'long' }).format(target)
  return `Entrega aproximada ${formatted}`
})

const shippingFirstName = computed(() => {
  if (!auth.isAuthenticated || !auth.user) return ''
  const source =
    auth.user.first_name ||
    auth.user.nombre ||
    auth.user?.perfil?.nombre ||
    auth.user?.perfil?.first_name ||
    ''
  if (!source) return ''
  return String(source).trim().split(/\s+/)[0] || ''
})

const shippingAddressPreview = computed(() => {
  if (!auth.isAuthenticated) return ''
  const dir = auth.user?.direccion_predeterminada || auth.user?.perfil?.direccion_predeterminada
  if (!dir) return ''
  const fragments = [dir.calle, dir.numero_exterior, dir.colonia, dir.ciudad].filter(Boolean)
  if (!fragments.length) return ''
  const preview = fragments.join(', ')
  return preview.length > 60 ? `${preview.slice(0, 57).trim()}…` : preview
})

const showShipToBlock = computed(() => Boolean(shippingFirstName.value && shippingAddressPreview.value))
const hasAnyRelacionados = computed(
  () =>
    relacionadosLoading.value ||
    relacionados.value.length > 0 ||
    relacionadosCategoriaLoading.value ||
    relacionadosCategoria.value.length > 0
)

const productoId = computed(() => producto.value?.id)
const isFavorito = computed(() => auth.isAuthenticated && wishlist.esFavorito(productoId.value))
const toggleFav = () => productoId.value && wishlist.toggle(productoId.value)
</script>
