<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <h1 class="text-2xl font-semibold text-gray-800">
          Revision de clasificaciones
          <span v-if="pagination.count > 0" class="ml-2 text-lg font-normal text-gray-500">({{ pagination.count }} en total)</span>
        </h1>
        <p class="text-sm text-gray-500">Revisa las sugerencias generadas por la IA y asigna la categoria correcta a cada producto.</p>
      </div>
      <button
        type="button"
        class="inline-flex items-center rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-100 disabled:opacity-60"
        :disabled="loading"
        @click="fetchInitialData"
      >
        Actualizar
      </button>
    </div>

    <!-- Global Error -->
    <div v-if="globalError" class="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
      {{ globalError }}
    </div>

    <!-- Bulk Actions Panel -->
    <div v-if="!loading && products.length" class="space-y-4 rounded-md border border-gray-200 bg-gray-50 p-4">
      <!-- Selection and AI Approve -->
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-3">
          <input
            id="select-all"
            type="checkbox"
            class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            :checked="isAllSelected"
            @change="toggleSelectAll"
          />
          <label for="select-all" class="text-sm font-medium text-gray-700">
            Seleccionar todo ({{ bulkSelectedProducts.size }} de {{ products.length }})
          </label>
        </div>
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-60"
          :disabled="bulkSaving || bulkSelectedProducts.size === 0"
          @click="approveBulkSuggestions"
        >
          <svg v-if="bulkSaving" class="mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          Aprobar sugerencias ({{ bulkSelectedProducts.size }})
        </button>
      </div>

      <!-- Bulk Manual Categorization -->
      <div v-if="bulkSelectedProducts.size > 0" class="space-y-3 rounded-md border border-gray-300 bg-white p-3">
        <p class="text-sm font-medium text-gray-800">Asignar categoria manualmente a seleccionados</p>
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <select
            v-model="bulkSelectedLevel1"
            @change="onBulkLevel1Change"
            class="w-full rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option :value="null">Selecciona Nivel 1</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
          </select>
          <select
            v-model="bulkSelectedLevel2"
            @change="onBulkLevel2Change"
            :disabled="!bulkLevel2Categories.length"
            class="w-full rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-100"
          >
            <option :value="null">Selecciona Nivel 2</option>
            <option v-for="cat in bulkLevel2Categories" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
          </select>
          <select
            v-model="bulkSelectedLevel3"
            :disabled="!bulkLevel3Categories.length"
            class="w-full rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-100"
          >
            <option :value="null">Selecciona Nivel 3</option>
            <option v-for="cat in bulkLevel3Categories" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
          </select>
        </div>
        <button
          type="button"
          class="w-full rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-100 disabled:opacity-60"
          :disabled="bulkSaving || !finalBulkCategoryId"
          @click="saveBulkManual"
        >
          Guardar manualmente ({{ bulkSelectedProducts.size }})
        </button>
      </div>
    </div>

    <!-- Loading/Empty State -->
    <div v-if="loading" class="flex items-center gap-2 text-gray-500">
      <svg class="h-5 w-5 animate-spin text-gray-400" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
      Cargando productos pendientes...
    </div>
    <div v-else-if="!products.length" class="rounded-md border border-gray-200 bg-white p-6 text-center text-gray-500">
      No hay productos pendientes de revision.
    </div>

    <!-- Product Grid -->
    <div v-else class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="product in products"
        :key="product.id"
        class="relative flex h-full flex-col overflow-hidden rounded-lg border-2 bg-white shadow-sm"
        :class="{ 'border-blue-500': bulkSelectedProducts.has(product.id) }"
      >
        <div class="absolute left-2 top-2 z-10 flex h-6 w-6 items-center justify-center rounded bg-white bg-opacity-75">
          <input
            type="checkbox"
            class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            :checked="bulkSelectedProducts.has(product.id)"
            @change="() => toggleBulkSelection(product.id)"
          />
        </div>

        <div class="flex h-48 items-center justify-center bg-gray-50">
          <img v-if="product.imagen_url" :src="product.imagen_url" :alt="product.nombre" class="h-full w-full object-contain" />
          <span v-else class="text-sm text-gray-400">Sin imagen</span>
        </div>

        <div class="flex flex-1 flex-col gap-4 p-4">
          <div>
            <h2 class="text-lg font-semibold text-gray-800">{{ product.nombre }}</h2>
          </div>

          <div class="rounded-md bg-gray-50 p-3 text-sm text-gray-600">
            <p class="mb-1 text-sm font-medium text-gray-700">Sugerencia de IA</p>
            <p>Principal: <span class="font-semibold text-gray-800">{{ product.category_ai_main || 'N/A' }}</span></p>
            <p>Subcategoria: <span class="font-semibold text-gray-800">{{ product.category_ai_sub || 'N/A' }}</span></p>
          </div>

          <div class="space-y-3">
            <div>
              <label :for="`level1-${product.id}`" class="mb-1 block text-sm font-medium text-gray-700">Categoria nivel 1</label>
              <select
                :id="`level1-${product.id}`"
                v-model="selectedLevel1[product.id]"
                @change="onLevel1Change(product.id)"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Selecciona Nivel 1</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.nombre }}</option>
              </select>
            </div>
            <div>
              <label :for="`level2-${product.id}`" class="mb-1 block text-sm font-medium text-gray-700">Categoria nivel 2</label>
              <select
                :id="`level2-${product.id}`"
                v-model="selectedLevel2[product.id]"
                @change="onLevel2Change(product.id)"
                :disabled="!getLevel2Categories(toNumberOrNull(selectedLevel1[product.id])).length"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Selecciona Nivel 2</option>
                <option v-for="category in getLevel2Categories(toNumberOrNull(selectedLevel1[product.id]))" :key="category.id" :value="category.id">
                  {{ category.nombre }}
                </option>
              </select>
            </div>
            <div>
              <label :for="`level3-${product.id}`" class="mb-1 block text-sm font-medium text-gray-700">Categoria nivel 3</label>
              <select
                :id="`level3-${product.id}`"
                v-model="selectedLevel3[product.id]"
                :disabled="!getLevel3Categories(toNumberOrNull(selectedLevel1[product.id]), toNumberOrNull(selectedLevel2[product.id])).length"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Selecciona Nivel 3</option>
                <option
                  v-for="category in getLevel3Categories(toNumberOrNull(selectedLevel1[product.id]), toNumberOrNull(selectedLevel2[product.id]))"
                  :key="category.id"
                  :value="category.id"
                >
                  {{ category.nombre }}
                </option>
              </select>
            </div>
          </div>

          <div class="mt-auto space-y-3">
            <div class="space-y-2 rounded-md border border-gray-200 bg-gray-50 p-3">
              <p class="text-sm font-medium text-gray-700">Categorias adicionales</p>
              <div class="max-h-32 overflow-y-auto space-y-1">
                <div v-for="category in flatCategories" :key="category.id" class="flex items-center">
                  <input
                    type="checkbox"
                    :id="`additional-cat-${product.id}-${category.id}`"
                    :value="category.id"
                    v-model="selectedAdditionalCategories[product.id]"
                    class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label :for="`additional-cat-${product.id}-${category.id}`" class="ml-2 text-sm text-gray-700">
                    {{ category.label }}
                  </label>
                </div>
              </div>
            </div>

            <button
              type="button"
              class="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-60"
              :disabled="saving[product.id] || bulkSaving"
              @click="approveSuggestion(product)"
            >
              Aprobar sugerencia
            </button>
            <button
              type="button"
              class="w-full rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-100 disabled:opacity-60"
              :disabled="saving[product.id] || bulkSaving"
              @click="saveManual(product)"
            >
              Guardar manualmente
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Load More Button -->
    <div v-if="pagination.next" class="pt-6 text-center">
      <button
        @click="loadMore"
        :disabled="loadingMore"
        class="inline-flex items-center rounded-md border border-gray-300 bg-white px-6 py-3 text-base font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 disabled:opacity-60"
      >
        <svg v-if="loadingMore" class="mr-3 h-5 w-5 animate-spin text-gray-700" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        Cargar más
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import api, { ensureInterceptors } from '@/axios'

const loading = ref(false)
const loadingMore = ref(false)
const products = ref([])
const categories = ref([])
const globalError = ref('')
const pagination = ref({
  count: 0,
  next: null,
  previous: null,
})

// State for individual product selections
const selectedLevel1 = reactive({})
const selectedLevel2 = reactive({})
const selectedLevel3 = reactive({})
const selectedAdditionalCategories = reactive({})
const saving = reactive({})

// State for bulk actions
const bulkSaving = ref(false)
const bulkSelectedProducts = ref(new Set())
const bulkSelectedLevel1 = ref(null)
const bulkSelectedLevel2 = ref(null)
const bulkSelectedLevel3 = ref(null)

// --- Helper Functions ---
const normalize = (value) => {
  const text = (value ?? '').toString().trim().toLowerCase()
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/['`"]/g, '')
    .replace(/[^\w\s>/-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

const INVALID_SUGGESTION_VALUES = new Set(['', 'n/a', 'na', 'none', 'null', 'sin subcategoria'])
const MAIN_CATEGORY_ALIASES = {
  // Cómputo (Hardware)
  almacenamiento: 'computo hardware',
  storage: 'computo hardware',
  hardware: 'computo hardware',
  computadoras: 'computo hardware',
  computo: 'computo hardware',
  'computo hardware': 'computo hardware',
  computacion: 'computo hardware',
  'tecnologia informatica': 'computo hardware',
  laptops: 'computo hardware',
  // Impresión y Copiado
  impresoras: 'impresion y copiado',
  impresion: 'impresion y copiado',
  'impresion y copiado': 'impresion y copiado',
  // Audio y Video
  audio: 'audio y video',
  video: 'audio y video',
  multimedia: 'audio y video',
  'audio y video': 'audio y video',
  proyectores: 'audio y video',
  // Seguridad y Vigilancia
  seguridad: 'seguridad y vigilancia',
  camaras: 'seguridad y vigilancia',
  vigilancia: 'seguridad y vigilancia',
  // Energía
  energia: 'energia',
  ups: 'energia',
  baterias: 'energia',
  // Punto de Venta (POS)
  pos: 'punto de venta pos',
  'punto de venta': 'punto de venta pos',
  // Software y Servicios
  software: 'software y servicios',
  servicios: 'software y servicios',
}

const getCategoryEntries = () => {
  const entries = []
  const walk = (nodes = [], root = null, path = []) => {
    nodes.forEach((node) => {
      const nextRoot = root || node
      const nextPath = [...path, node.nombre]
      entries.push({
        id: node.id,
        rootId: nextRoot.id,
        rootName: nextRoot.nombre,
        leafName: node.nombre,
        label: nextPath.join(' > '),
      })
      if (node.subcategorias?.length) walk(node.subcategorias, nextRoot, nextPath)
    })
  }
  walk(categories.value)
  return entries
}

const findMainByName = (mainName) => {
  const mainNormalized = normalize(mainName)
  if (!mainNormalized) return null

  const direct = categories.value.find((cat) => normalize(cat.nombre) === mainNormalized)
  if (direct) return direct

  const aliasTarget = MAIN_CATEGORY_ALIASES[mainNormalized]
  if (!aliasTarget) return null
  return categories.value.find((cat) => normalize(cat.nombre) === aliasTarget) || null
}

const toNumberOrNull = (value) => {
  const number = Number(value)
  return value === undefined || value === null || value === '' || Number.isNaN(number) ? null : number
}

const normalizeCategoryIds = (ids) => {
  const list = Array.isArray(ids) ? ids : [ids]
  const normalized = list.map(toNumberOrNull).filter(Boolean)
  return [...new Set(normalized)]
}

const flattenCategoryTree = (nodes, prefix = '') => {
  const flattened = []
  nodes.forEach((node) => {
    const label = prefix ? `${prefix} > ${node.nombre}` : node.nombre
    flattened.push({ id: node.id, label })
    if (node.subcategorias?.length) {
      flattened.push(...flattenCategoryTree(node.subcategorias, label))
    }
  })
  return flattened
}

const findCategoryPath = (categoryId, nodes) => {
  if (!categoryId) return { level1: null, level2: null, level3: null }
  const queue = nodes.map((node) => ({ node, path: [node.id] }))
  while (queue.length) {
    const { node, path } = queue.shift()
    if (node.id === categoryId) {
      return {
        level1: path[0] ?? null,
        level2: path[1] ?? null,
        level3: path[2] ?? null,
      }
    }
    const children = node.subcategorias || []
    for (const child of children) {
      queue.push({ node: child, path: [...path, child.id] })
    }
  }
  return { level1: null, level2: null, level3: null }
}

// --- Computed Properties ---
const isAllSelected = computed(() => {
  return products.value.length > 0 && bulkSelectedProducts.value.size === products.value.length
})

const bulkLevel2Categories = computed(() => {
  if (!bulkSelectedLevel1.value) return []
  const cat = categories.value.find((c) => c.id === bulkSelectedLevel1.value)
  return cat?.subcategorias ?? []
})

const bulkLevel3Categories = computed(() => {
  if (!bulkSelectedLevel2.value) return []
  const cat = bulkLevel2Categories.value.find((c) => c.id === bulkSelectedLevel2.value)
  return cat?.subcategorias ?? []
})

const finalBulkCategoryId = computed(() => {
  return bulkSelectedLevel3.value || bulkSelectedLevel2.value || bulkSelectedLevel1.value
})

const flatCategories = computed(() => flattenCategoryTree(categories.value))

// --- Bulk Selection Logic ---
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    bulkSelectedProducts.value.clear()
  } else {
    products.value.forEach((product) => bulkSelectedProducts.value.add(product.id))
  }
}

const toggleBulkSelection = (productId) => {
  if (bulkSelectedProducts.value.has(productId)) {
    bulkSelectedProducts.value.delete(productId)
  } else {
    bulkSelectedProducts.value.add(productId)
  }
}

// --- Category Logic ---
const findSubcategoryByName = (category, name) => {
  if (!category || !name) return null
  const target = normalize(name)
  const stack = [...(category.subcategorias || [])]
  while (stack.length) {
    const current = stack.shift()
    if (normalize(current.nombre) === target) return current
    if (current.subcategorias?.length) stack.push(...current.subcategorias)
  }
  return null
}

const findCategoryIdsBySuggestion = (mainName, subName) => {
  const main = findMainByName(mainName)
  const entries = getCategoryEntries()

  const normalizedSub = normalize(subName)
  if (!INVALID_SUGGESTION_VALUES.has(normalizedSub)) {
    const byFullPath = entries.find((entry) => normalize(entry.label) === normalizedSub)
    if (byFullPath) return byFullPath.id

    const bySuffix = entries.filter((entry) => normalize(entry.label).endsWith(normalizedSub))
    if (bySuffix.length === 1) return bySuffix[0].id
    if (main) {
      const bySuffixWithMain = bySuffix.find((entry) => entry.rootId === main.id)
      if (bySuffixWithMain) return bySuffixWithMain.id
    }

    const segments = subName
      .toString()
      .split('>')
      .map((segment) => segment.trim())
      .filter(Boolean)
    const leaf = segments.length ? segments[segments.length - 1] : subName
    const leafNormalized = normalize(leaf)
    if (leafNormalized && !INVALID_SUGGESTION_VALUES.has(leafNormalized)) {
      const byLeaf = entries.filter((entry) => normalize(entry.leafName) === leafNormalized)
      if (main) {
        const inMain = byLeaf.filter((entry) => entry.rootId === main.id)
        if (inMain.length) return inMain[0].id
      }
      if (byLeaf.length === 1) return byLeaf[0].id
    }

    if (main) {
      const subInMain = findSubcategoryByName(main, subName)
      if (subInMain) return subInMain.id
    }
  }

  return main?.id || null
}

const getLevel2Categories = (level1Id) => {
  if (!level1Id) return []
  const cat = categories.value.find((c) => c.id === level1Id)
  return cat?.subcategorias ?? []
}

const getLevel3Categories = (level1Id, level2Id) => {
  if (!level2Id) return []
  const catL2 = getLevel2Categories(level1Id).find((c) => c.id === level2Id)
  return catL2?.subcategorias ?? []
}

// --- Change Handlers ---
const onLevel1Change = (productId) => {
  delete selectedLevel2[productId]
  delete selectedLevel3[productId]
}

const onLevel2Change = (productId) => {
  delete selectedLevel3[productId]
}

const onBulkLevel1Change = () => {
  bulkSelectedLevel2.value = null
  bulkSelectedLevel3.value = null
}

const onBulkLevel2Change = () => {
  bulkSelectedLevel3.value = null
}

// --- API Calls & Data Handling ---
const fetchInitialData = async () => {
  loading.value = true
  globalError.value = ''
  try {
    ensureInterceptors()
    // Solo carga las categorías una vez
    if (categories.value.length === 0) {
      const categoriesRes = await api.get('all-categories/')
      categories.value = Array.isArray(categoriesRes.data) ? categoriesRes.data : []
    }

    const pendingRes = await api.get('ai/pending-review/')
    
    products.value = Array.isArray(pendingRes.data.results) ? pendingRes.data.results : []
    pagination.value.count = pendingRes.data.count
    pagination.value.next = pendingRes.data.next
    
    bulkSelectedProducts.value.clear()
    initializeProductState(products.value)
  } catch (error) {
    globalError.value = error.response?.data?.detail || 'No se pudieron cargar los datos. Intenta nuevamente.'
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  if (!pagination.value.next || loadingMore.value) return
  loadingMore.value = true
  globalError.value = ''
  try {
    const res = await api.get(pagination.value.next)
    const newProducts = Array.isArray(res.data.results) ? res.data.results : []
    products.value.push(...newProducts)
    pagination.value.next = res.data.next
    initializeProductState(newProducts)
  } catch {
    globalError.value = 'No se pudieron cargar más productos. Intenta nuevamente.'
  } finally {
    loadingMore.value = false
  }
}

const initializeProductState = (productsToInitialize) => {
  productsToInitialize.forEach((product) => {
    const initialCategories = Array.isArray(product.categorias) ? product.categorias : []
    if (initialCategories.length > 0) {
      const path = findCategoryPath(initialCategories[0], categories.value)
      selectedLevel1[product.id] = path.level1
      selectedLevel2[product.id] = path.level2
      selectedLevel3[product.id] = path.level3
    } else {
      selectedLevel1[product.id] = null
      selectedLevel2[product.id] = null
      selectedLevel3[product.id] = null
    }
    selectedAdditionalCategories[product.id] = [...initialCategories]
  })
}

const applyCategoryToProduct = async (productId, categoryIds) => {
  const normalizedIds = normalizeCategoryIds(categoryIds)
  if (!normalizedIds.length) {
    globalError.value = 'Selecciona una categoria valida.'
    return
  }
  globalError.value = ''
  saving[productId] = true
  try {
    await api.post(`productos/${productId}/apply-category/`, { category_ids: normalizedIds })
    products.value = products.value.filter((product) => product.id !== productId)
    pagination.value.count--
    bulkSelectedProducts.value.delete(productId)
  } catch (error) {
    globalError.value = error.response?.data?.detail || 'No se pudo aplicar la categoria.'
  } finally {
    delete saving[productId]
  }
}

const applyCategoryToProducts = async (payload) => {
  if (!payload.length) return
  globalError.value = ''
  bulkSaving.value = true
  try {
    await api.post('productos/bulk-apply-category/', { products: payload })
    const processedIds = new Set(payload.map((item) => item.product_id))
    products.value = products.value.filter((product) => !processedIds.has(product.id))
    pagination.value.count -= processedIds.size
    bulkSelectedProducts.value.clear()
  } catch (error) {
    globalError.value = error.response?.data?.detail || 'Ocurrio un error al procesar la solicitud masiva.'
  } finally {
    bulkSaving.value = false
  }
}

// --- Button Click Handlers ---
const approveSuggestion = async (product) => {
  const categoryId = findCategoryIdsBySuggestion(product.category_ai_main, product.category_ai_sub)
  if (!categoryId) {
    globalError.value = 'No se encontro una categoria que coincida con la sugerencia de la IA.'
    return
  }
  await applyCategoryToProduct(product.id, [categoryId])
}

const saveManual = async (product) => {
  const primaryCategoryId =
    toNumberOrNull(selectedLevel3[product.id]) || toNumberOrNull(selectedLevel2[product.id]) || toNumberOrNull(selectedLevel1[product.id])
  const additionalCategoryIds = selectedAdditionalCategories[product.id] || []
  const allCategoryIds = normalizeCategoryIds([primaryCategoryId, ...additionalCategoryIds])

  if (!allCategoryIds.length) {
    globalError.value = 'Selecciona al menos una categoria.'
    return
  }
  await applyCategoryToProduct(product.id, allCategoryIds)
}

const approveBulkSuggestions = async () => {
  const productMap = new Map(products.value.map((product) => [product.id, product]))
  const payload = []
  for (const productId of bulkSelectedProducts.value) {
    const product = productMap.get(productId)
    if (!product) continue
    const categoryId = findCategoryIdsBySuggestion(product.category_ai_main, product.category_ai_sub)
    if (!categoryId) {
      globalError.value = `No se encontro una categoria valida para la sugerencia de IA del producto: "${product.nombre}". Abortando.`
      return
    }
    payload.push({ product_id: productId, category_ids: [categoryId] })
  }
  await applyCategoryToProducts(payload)
}

const saveBulkManual = async () => {
  const categoryId = toNumberOrNull(finalBulkCategoryId.value)
  if (!categoryId) {
    globalError.value = 'Por favor, selecciona una categoria para aplicar masivamente.'
    return
  }
  const payload = Array.from(bulkSelectedProducts.value).map((productId) => ({
    product_id: productId,
    category_ids: [categoryId],
  }))
  await applyCategoryToProducts(payload)
}

onMounted(fetchInitialData)
</script>

