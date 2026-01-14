<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <h1 class="text-2xl font-semibold text-gray-800">Revisión de clasificaciones</h1>
        <p class="text-sm text-gray-500">
          Revisa las sugerencias generadas por la IA y asigna la categoría correcta a cada producto.
        </p>
      </div>
      <button
        type="button"
        class="inline-flex items-center rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-100 disabled:opacity-60"
        :disabled="loading"
        @click="fetchData"
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
      </div>

      <!-- Bulk Manual Categorization -->
      <div v-if="bulkSelectedProducts.size > 0" class="space-y-3 rounded-md border border-gray-300 bg-white p-3">
        <p class="text-sm font-medium text-gray-800">Asignar categoría manualmente a seleccionados</p>
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
          Guardar Manualmente ({{ bulkSelectedProducts.size }})
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
      No hay productos pendientes de revisión.
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

          <!-- Nuevas Sugerencias de IA como tags -->
          <div class="rounded-md bg-gray-50 p-3 text-sm">
            <p class="mb-2 text-sm font-medium text-gray-700">Categorías Asignadas por IA</p>
            <div v-if="product._displayCategories && product._displayCategories.length" class="flex flex-wrap gap-2">
              <span v-for="cat in product._displayCategories" :key="cat.id" class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800">
                {{ cat.nombre }}
              </span>
            </div>
            <p v-else class="text-gray-500">La IA no asignó categorías.</p>
          </div>

          <div class="space-y-3">
            <div>
<<<<<<< HEAD
              <label :for="`level1-${product.id}`" class="mb-1 block text-sm font-medium text-gray-700">Editar Categoría Principal (Nivel 1)</label>
=======
              <label :for="`level1-${product.id}`" class="mb-1 block text-sm font-medium text-gray-700">Categoría Nivel 1</label>
>>>>>>> parent of 7edc89b (multi-categorias funciona)
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
<<<<<<< HEAD
              <label :for="`level2-${product.id}`" class="mb-1 block text-sm font-medium text-gray-700">Nivel 2</label>
=======
              <label :for="`level2-${product.id}`" class="mb-1 block text-sm font-medium text-gray-700">Categoría Nivel 2</label>
>>>>>>> parent of 7edc89b (multi-categorias funciona)
              <select
                :id="`level2-${product.id}`"
                v-model="selectedLevel2[product.id]"
                @change="onLevel2Change(product.id)"
                :disabled="!getLevel2Categories(toNumberOrNull(selectedLevel1[product.id])).length"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Selecciona Nivel 2</option>
                <option v-for="category in getLevel2Categories(toNumberOrNull(selectedLevel1[product.id]))" :key="category.id" :value="category.id">{{ category.nombre }}</option>
              </select>
            </div>
            <div>
<<<<<<< HEAD
              <label :for="`level3-${product.id}`" class="mb-1 block text-sm font-medium text-gray-700">Nivel 3</label>
=======
              <label :for="`level3-${product.id}`" class="mb-1 block text-sm font-medium text-gray-700">Categoría Nivel 3</label>
>>>>>>> parent of 7edc89b (multi-categorias funciona)
              <select
                :id="`level3-${product.id}`"
                v-model="selectedLevel3[product.id]"
                :disabled="!getLevel3Categories(toNumberOrNull(selectedLevel1[product.id]), toNumberOrNull(selectedLevel2[product.id])).length"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Selecciona Nivel 3</option>
                <option v-for="category in getLevel3Categories(toNumberOrNull(selectedLevel1[product.id]), toNumberOrNull(selectedLevel2[product.id]))" :key="category.id" :value="category.id">{{ category.nombre }}</option>
              </select>
            </div>
          </div>

<<<<<<< HEAD
          <!-- Additional Categories -->
          <div class="mt-auto space-y-2 rounded-md border border-gray-200 bg-gray-50 p-3">
            <p class="text-sm font-medium text-gray-700">Editar Categorías Adicionales</p>
            <div class="max-h-32 overflow-y-auto space-y-1">
              <div
                v-for="category in flatCategories"
                :key="category.id"
                class="flex items-center"
                :style="{ paddingLeft: `${category.depth * 12}px` }"
              >
                <input
                  type="checkbox"
                  :id="`additional-cat-${product.id}-${category.id}`"
                  :value="category.id"
                  v-model="selectedAdditionalCategories[product.id]"
                  class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label :for="`additional-cat-${product.id}-${category.id}`" class="ml-2 text-sm text-gray-700">
                  {{ category.nombre }}
                </label>
              </div>
            </div>
          </div>

=======
>>>>>>> parent of 7edc89b (multi-categorias funciona)
          <div class="mt-auto space-y-2 pt-4">
            <button type="button" class="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-60" :disabled="saving[product.id] || bulkSaving" @click="saveManual(product)">Guardar Cambios</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import api, { ensureInterceptors } from '@/axios'

const loading = ref(false)
const products = ref([])
const categories = ref([])
const globalError = ref('')

// State for individual product selections
const selectedLevel1 = reactive({})
const selectedLevel2 = reactive({})
const selectedLevel3 = reactive({})
<<<<<<< HEAD
const selectedAdditionalCategories = reactive({})
=======
>>>>>>> parent of 7edc89b (multi-categorias funciona)
const saving = reactive({})

// State for bulk actions
const bulkSaving = ref(false)
const bulkSelectedProducts = ref(new Set())
const bulkSelectedLevel1 = ref(null)
const bulkSelectedLevel2 = ref(null)
const bulkSelectedLevel3 = ref(null)

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

// --- Helper Functions ---

const normalize = (value) => (value ?? '').toString().trim().toLowerCase()
const toNumberOrNull = (value) => {
  const number = Number(value)
  return value === undefined || value === null || value === '' || Number.isNaN(number) ? null : number
}
const normalizeCategoryId = (value) => {
  if (value === undefined || value === null || value === '') return null
  if (typeof value === 'object') {
    return toNumberOrNull(value.id ?? value.pk ?? value.categoria ?? value.category)
  }
  return toNumberOrNull(value)
}
const extractCategoryIds = (raw) => {
  if (!Array.isArray(raw)) return []
  const ids = raw.map((item) => normalizeCategoryId(item)).filter((id) => id !== null)
  return [...new Set(ids)]
}
const flattenCategories = (items, depth = 0, acc = []) => {
  for (const item of items || []) {
    const id = normalizeCategoryId(item)
    if (id !== null) {
      acc.push({
        id,
        nombre: item?.nombre ?? item?.name ?? `ID ${id}`,
        depth,
      })
    }
    if (item?.subcategorias?.length) {
      flattenCategories(item.subcategorias, depth + 1, acc)
    }
  }
  return acc
}
const flatCategories = computed(() => flattenCategories(categories.value))
const categoriesById = computed(() => {
  const map = {}
  for (const item of flatCategories.value) {
    map[item.id] = item
  }
  return map
})
const resolveCategoryName = (raw, id, index) => {
  const fromIndex = index?.[id]?.nombre
  if (fromIndex) return fromIndex
  if (Array.isArray(raw)) {
    const found = raw.find((item) => normalizeCategoryId(item) === id)
    const name = found?.nombre ?? found?.name
    if (name) return name
  }
  return `ID ${id}`
}

// --- Bulk Selection Logic ---

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    bulkSelectedProducts.value.clear()
  } else {
    products.value.forEach((p) => bulkSelectedProducts.value.add(p.id))
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
  const main = categories.value.find((cat) => normalize(cat.nombre) === normalize(mainName))
  if (!main) return null
  if (subName) {
    const sub = findSubcategoryByName(main, subName)
    if (sub) return sub.id
  }
  return main.id
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

const fetchData = async () => {
  loading.value = true
  globalError.value = ''
  try {
    ensureInterceptors()
    const [pendingRes, categoriesRes] = await Promise.all([api.get('ai/pending-review/'), api.get('all-categories/')])
    products.value = Array.isArray(pendingRes.data) ? pendingRes.data : []
    categories.value = Array.isArray(categoriesRes.data) ? categoriesRes.data : []
    bulkSelectedProducts.value.clear()
<<<<<<< HEAD
    
    // Initialize selections for each product
    const categoryIndex = categoriesById.value
    products.value.forEach(product => {
      const initialCategoryIds = extractCategoryIds(product.categorias)
      product._displayCategories = initialCategoryIds.map((id) => ({
        id,
        nombre: resolveCategoryName(product.categorias, id, categoryIndex),
      }))

      if (initialCategoryIds.length > 0) {
        const primaryCatId = initialCategoryIds[0]
        const path = findCategoryPath(primaryCatId, categories.value)
        selectedLevel1[product.id] = path.level1
        selectedLevel2[product.id] = path.level2
        selectedLevel3[product.id] = path.level3
        
        selectedAdditionalCategories[product.id] = [...initialCategoryIds]
      } else {
        selectedLevel1[product.id] = null
        selectedLevel2[product.id] = null
        selectedLevel3[product.id] = null
        selectedAdditionalCategories[product.id] = []
      }
    })

=======
>>>>>>> parent of 7edc89b (multi-categorias funciona)
  } catch (error) {
    globalError.value = error.response?.data?.detail || 'No se pudieron cargar los datos. Intenta nuevamente.'
  } finally {
    loading.value = false
  }
}

const applyCategoryToProduct = async (productId, categoryId) => {
  if (!categoryId) {
    globalError.value = 'Selecciona una categoría válida.'
    return
  }
  globalError.value = ''
  saving[productId] = true
  try {
    await api.post(`productos/${productId}/apply-category/`, { category_id: categoryId })
    products.value = products.value.filter((p) => p.id !== productId)
    bulkSelectedProducts.value.delete(productId)
  } catch (error) {
    globalError.value = error.response?.data?.detail || 'No se pudo aplicar la categoría.'
  } finally {
    delete saving[productId]
  }
}

const applyCategoryToProducts = async (payload) => {
  if (!payload.length) return
  globalError.value = ''
  bulkSaving.value = true
  try {
    // NOTE: This assumes a generic backend endpoint for bulk categorization
    await api.post('productos/bulk-apply-category/', { products: payload })
    const processedIds = new Set(payload.map((p) => p.product_id))
    products.value = products.value.filter((p) => !processedIds.has(p.id))
    bulkSelectedProducts.value.clear()
  } catch (error) {
    globalError.value = error.response?.data?.detail || 'Ocurrió un error al procesar la solicitud masiva.'
  } finally {
    bulkSaving.value = false
  }
}

// --- Button Click Handlers ---

<<<<<<< HEAD
const saveManual = async (product) => {
  const primaryCategoryId = toNumberOrNull(selectedLevel3[product.id]) || toNumberOrNull(selectedLevel2[product.id]) || toNumberOrNull(selectedLevel1[product.id])
  const additionalCategoryIds = (selectedAdditionalCategories[product.id] || [])
    .map(toNumberOrNull)
    .filter((id) => id !== null)

  let allCategoryIds = [];
  if (primaryCategoryId) {
    allCategoryIds.push(primaryCategoryId);
  }
  allCategoryIds = [...new Set([...allCategoryIds, ...additionalCategoryIds])]; // Ensure uniqueness

  if (allCategoryIds.length === 0) {
    globalError.value = 'Selecciona al menos una categoría para guardar.'
=======
const approveSuggestion = async (product) => {
  const finalId = findCategoryIdsBySuggestion(product.category_ai_main, product.category_ai_sub)
  if (!finalId) {
    globalError.value = 'No se encontró una categoría que coincida con la sugerencia de la IA.'
    return
  }
  await applyCategoryToProduct(product.id, finalId)
}

const saveManual = async (product) => {
  const finalId = toNumberOrNull(selectedLevel3[product.id]) || toNumberOrNull(selectedLevel2[product.id]) || toNumberOrNull(selectedLevel1[product.id])
  if (!finalId) {
    globalError.value = 'Selecciona al menos una categoría.'
>>>>>>> parent of 7edc89b (multi-categorias funciona)
    return
  }
  await applyCategoryToProduct(product.id, finalId)
}

<<<<<<< HEAD
=======
const approveBulkSuggestions = async () => {
  const productMap = new Map(products.value.map((p) => [p.id, p]))
  const payload = []
  for (const productId of bulkSelectedProducts.value) {
    const product = productMap.get(productId)
    if (!product) continue
    const categoryId = findCategoryIdsBySuggestion(product.category_ai_main, product.category_ai_sub)
    if (!categoryId) {
      globalError.value = `No se encontró una categoría válida para la sugerencia de IA del producto: "${product.nombre}". Abortando.`
      return
    }
    payload.push({ product_id: productId, category_id: categoryId })
  }
  await applyCategoryToProducts(payload)
}

>>>>>>> parent of 7edc89b (multi-categorias funciona)
const saveBulkManual = async () => {
  const categoryId = finalBulkCategoryId.value
  if (!categoryId) {
    globalError.value = 'Por favor, selecciona una categoría para aplicar masivamente.'
    return
  }
  const payload = Array.from(bulkSelectedProducts.value).map((productId) => ({
    product_id: productId,
    category_id: categoryId,
  }))
  await applyCategoryToProducts(payload)
}

onMounted(fetchData)
</script>
