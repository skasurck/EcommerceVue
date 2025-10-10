<template>
  <div class="space-y-6">
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

    <div v-if="globalError" class="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
      {{ globalError }}
    </div>

    <div v-if="loading" class="flex items-center gap-2 text-gray-500">
      <svg class="h-5 w-5 animate-spin text-gray-400" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
        />
      </svg>
      Cargando productos pendientes...
    </div>

    <div v-else-if="!products.length" class="rounded-md border border-gray-200 bg-white p-6 text-center text-gray-500">
      No hay productos pendientes de revisión.
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="product in products"
        :key="product.id"
        class="flex h-full flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm"
      >
        <div class="flex h-48 items-center justify-center bg-gray-50">
          <img
            v-if="product.imagen_url"
            :src="product.imagen_url"
            :alt="product.nombre"
            class="h-full w-full object-contain"
          />
          <span v-else class="text-sm text-gray-400">Sin imagen</span>
        </div>

        <div class="flex flex-1 flex-col gap-4 p-4">
          <div>
            <h2 class="text-lg font-semibold text-gray-800">{{ product.nombre }}</h2>
          </div>

          <div class="rounded-md bg-gray-50 p-3 text-sm text-gray-600">
            <p class="mb-1 text-sm font-medium text-gray-700">Sugerencia de IA</p>
            <p>
              Principal:
              <span class="font-semibold text-gray-800">{{ product.category_ai_main || 'N/A' }}</span>
              <span v-if="product.category_ai_conf_main !== null" class="text-xs text-gray-500">
                ({{ formatConfidence(product.category_ai_conf_main) }})
              </span>
            </p>
            <p>
              Subcategoría:
              <span class="font-semibold text-gray-800">{{ product.category_ai_sub || 'N/A' }}</span>
              <span v-if="product.category_ai_conf_sub !== null" class="text-xs text-gray-500">
                ({{ formatConfidence(product.category_ai_conf_sub) }})
              </span>
            </p>
          </div>

          <div class="space-y-3">
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700" :for="`main-${product.id}`">
                Categoría principal
              </label>
              <select
                :id="`main-${product.id}`"
                v-model="selectedMain[product.id]"
                @change="onMainChange(product.id)"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Selecciona una categoría</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.nombre }}
                </option>
              </select>
            </div>

            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700" :for="`sub-${product.id}`">
                Subcategoría
              </label>
              <select
                :id="`sub-${product.id}`"
                v-model="selectedSub[product.id]"
                :disabled="!getSubcategories(toNumberOrNull(selectedMain[product.id])).length"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-400"
              >
                <option value="">Selecciona una subcategoría</option>
                <option
                  v-for="subcategory in getSubcategories(toNumberOrNull(selectedMain[product.id]))"
                  :key="subcategory.id"
                  :value="subcategory.id"
                >
                  {{ subcategory.nombre }}
                </option>
              </select>
            </div>
          </div>

          <div class="mt-auto space-y-2">
            <button
              type="button"
              class="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:opacity-60"
              :disabled="saving[product.id]"
              @click="approveSuggestion(product)"
            >
              Aprobar sugerencia
            </button>
            <button
              type="button"
              class="w-full rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100 disabled:opacity-60"
              :disabled="saving[product.id]"
              @click="saveManual(product)"
            >
              Guardar manualmente
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import api, { ensureInterceptors } from '@/axios'

const loading = ref(false)
const products = ref([])
const categories = ref([])
const globalError = ref('')
const selectedMain = reactive({})
const selectedSub = reactive({})
const saving = reactive({})

const normalize = (value) => (value ?? '').toString().trim().toLowerCase()

const toNumberOrNull = (value) => {
  if (value === undefined || value === null || value === '') return null
  const number = Number(value)
  return Number.isNaN(number) ? null : number
}

const formatConfidence = (value) => {
  if (value === undefined || value === null) return 'N/A'
  const num = Number(value)
  if (Number.isNaN(num)) return 'N/A'
  const percentage = num <= 1 ? num * 100 : num
  return `${percentage.toFixed(1)}%`
}

const findSubcategoryByName = (category, name) => {
  if (!category || !name) return null
  const target = normalize(name)
  const stack = [...(category.subcategorias || [])]
  while (stack.length) {
    const current = stack.shift()
    if (normalize(current.nombre) === target) {
      return current
    }
    if (current.subcategorias?.length) {
      stack.push(...current.subcategorias)
    }
  }
  return null
}

const findCategoryIds = (mainName, subName) => {
  const main = categories.value.find(
    (cat) => normalize(cat.nombre) === normalize(mainName)
  )
  if (!main) {
    return { mainId: null, subId: null, finalId: null }
  }
  if (subName) {
    const sub = findSubcategoryByName(main, subName)
    if (sub) {
      return { mainId: main.id, subId: sub.id, finalId: sub.id }
    }
  }
  return { mainId: main.id, subId: null, finalId: main.id }
}

const resetSelections = () => {
  Object.keys(selectedMain).forEach((key) => delete selectedMain[key])
  Object.keys(selectedSub).forEach((key) => delete selectedSub[key])
}

const initializeSelections = (items) => {
  resetSelections()
  items.forEach((product) => {
    const { mainId, subId } = findCategoryIds(
      product.category_ai_main,
      product.category_ai_sub
    )
    if (mainId) {
      selectedMain[product.id] = mainId
    }
    if (subId) {
      selectedSub[product.id] = subId
    }
  })
}

const getSubcategories = (mainId) => {
  if (!mainId) return []
  const category = categories.value.find((cat) => cat.id === mainId)
  return category?.subcategorias ?? []
}

const onMainChange = (productId) => {
  const mainId = toNumberOrNull(selectedMain[productId])
  if (mainId === null) {
    delete selectedMain[productId]
    delete selectedSub[productId]
    return
  }
  selectedMain[productId] = mainId
  const availableSubcategories = getSubcategories(mainId).map((sub) => sub.id)
  const currentSubId = toNumberOrNull(selectedSub[productId])
  if (!availableSubcategories.includes(currentSubId)) {
    delete selectedSub[productId]
  }
}

const fetchData = async () => {
  loading.value = true
  globalError.value = ''
  try {
    ensureInterceptors()
    const [pendingRes, categoriesRes] = await Promise.all([
      api.get('ai/pending-review/'),
      api.get('all-categories/'),
    ])
    const pendingProducts = Array.isArray(pendingRes.data) ? pendingRes.data : []
    const categoryTree = Array.isArray(categoriesRes.data) ? categoriesRes.data : []
    products.value = pendingProducts
    categories.value = categoryTree
    if (categoryTree.length) {
      initializeSelections(pendingProducts)
    } else {
      resetSelections()
    }
  } catch (error) {
    const detail =
      error.response?.data?.detail ||
      'No se pudieron cargar los datos. Intenta nuevamente.'
    globalError.value = detail
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
  try {
    saving[productId] = true
    await api.post(`productos/${productId}/apply-category/`, {
      category_id: categoryId,
    })
    products.value = products.value.filter((item) => item.id !== productId)
    delete selectedMain[productId]
    delete selectedSub[productId]
  } catch (error) {
    const detail =
      error.response?.data?.detail ||
      'No se pudo aplicar la categoría. Intenta nuevamente.'
    globalError.value = detail
  } finally {
    delete saving[productId]
  }
}

const approveSuggestion = async (product) => {
  const { finalId } = findCategoryIds(
    product.category_ai_main,
    product.category_ai_sub
  )
  if (!finalId) {
    globalError.value =
      'No se encontró una categoría que coincida con la sugerencia de la IA.'
    return
  }
  await applyCategoryToProduct(product.id, finalId)
}

const saveManual = async (product) => {
  const mainId = toNumberOrNull(selectedMain[product.id])
  const subId = toNumberOrNull(selectedSub[product.id])
  const finalId = subId || mainId
  if (!finalId) {
    globalError.value = 'Selecciona una categoría principal o una subcategoría.'
    return
  }
  await applyCategoryToProduct(product.id, finalId)
}

onMounted(fetchData)
</script>
