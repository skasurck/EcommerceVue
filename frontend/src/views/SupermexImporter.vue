<template>
  <div class="space-y-8">
    <header class="space-y-1">
      <h1 class="text-2xl font-semibold text-slate-900">Importar catálogo de Supermex</h1>
      <p class="text-sm text-slate-600">
        Ejecuta el scraper oficial, ajusta los parámetros y consulta los últimos productos sincronizados.
      </p>
    </header>

    <section class="bg-white border border-slate-200 rounded-xl shadow-sm p-6 space-y-6">
      <header class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 class="text-lg font-medium text-slate-800">Parámetros de ejecución</h2>
          <p class="text-sm text-slate-500">Elige entre rastrear una categoría o pegar URLs de producto directamente.</p>
        </div>
        <button
          type="button"
          class="text-sm text-blue-600 hover:text-blue-500"
          @click="resetForm"
        >
          Restablecer
        </button>
      </header>

      <form class="space-y-5" @submit.prevent="runScraper">
        <div class="grid gap-5 md:grid-cols-2">
          <div class="space-y-2">
            <label class="block text-sm font-medium text-slate-700" for="start-url">
              URL de listado (PLP)
            </label>
            <input
              id="start-url"
              v-model="form.startUrl"
              :disabled="hasProductUrls"
              type="url"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 disabled:bg-slate-100"
              placeholder="https://www.supermexdigital.mx/shop/monitores"
            />
            <p class="text-xs text-slate-500">
              Si rellenas URLs de producto abajo, este campo se ignorará.
            </p>
          </div>

          <div class="space-y-2">
            <label class="block text-sm font-medium text-slate-700" for="product-urls">
              URLs de producto (una por línea)
            </label>
            <textarea
              id="product-urls"
              v-model="form.productUrlsText"
              rows="4"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              placeholder="https://www.supermexdigital.mx/shop/123456-nombre-producto"
            ></textarea>
            <p class="text-xs text-slate-500">
              Usa este campo para ejecutar importaciones puntuales. Se omitirá la PLP.
            </p>
          </div>
        </div>

        <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div class="space-y-2">
            <label class="block text-sm font-medium text-slate-700" for="limit">
              Límite de productos
            </label>
            <input
              id="limit"
              v-model.number="form.limit"
              type="number"
              min="0"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
            <p class="text-xs text-slate-500">0 = sin límite.</p>
          </div>

          <div class="space-y-2">
            <label class="block text-sm font-medium text-slate-700" for="max-pages">
              Máximo de páginas
            </label>
            <input
              id="max-pages"
              v-model.number="form.maxPages"
              type="number"
              min="1"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
          </div>

          <div class="space-y-2">
            <label class="block text-sm font-medium text-slate-700" for="sleep-s">
              Pausa entre páginas (seg)
            </label>
            <input
              id="sleep-s"
              v-model.number="form.sleepSeconds"
              type="number"
              min="0"
              step="0.1"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
          </div>

          <div class="flex items-center gap-3 pt-6">
            <label class="inline-flex items-center gap-2 text-sm text-slate-700">
              <input type="checkbox" v-model="form.applyUpdates" class="rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
              Guardar cambios en la base de datos
            </label>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-4">
          <label class="inline-flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" v-model="form.http2" class="rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
            Forzar HTTP/2
          </label>
          <button
            type="submit"
            class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="running"
          >
            <span v-if="running" class="animate-spin">⏳</span>
            <span v-else>🚀</span>
            <span>{{ running ? 'Ejecutando...' : 'Ejecutar scraper' }}</span>
          </button>
          <p v-if="runError" class="text-sm text-red-600">{{ runError }}</p>
          <p v-else-if="runSummary" class="text-sm text-slate-500">
            {{ runSummary.processed_count }} productos actualizados de {{ runSummary.collected_count }} URLs.
          </p>
        </div>
      </form>
    </section>

    <section v-if="runSummary" class="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
      <h2 class="text-lg font-medium text-slate-800 mb-4">Resultado de la última ejecución</h2>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">Estado</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">SKU</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">Nombre</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">Precio proveedor</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">Disponibilidad</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">Producto Django</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">URL</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="result in runSummary.results" :key="result.url">
              <td class="px-4 py-2">
                <span
                  class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium"
                  :class="statusPillClass(result.status)"
                >
                  <span v-if="result.status === 'ok'">✅</span>
                  <span v-else-if="result.status === 'skipped'">⏭️</span>
                  <span v-else>⚠️</span>
                  {{ statusLabel(result.status) }}
                </span>
                <p v-if="result.error" class="mt-1 text-xs text-red-600">{{ result.error }}</p>
              </td>
              <td class="px-4 py-2 text-slate-700">
                {{ result.product?.supplier_sku || '—' }}
              </td>
              <td class="px-4 py-2 text-slate-700">
                <div class="max-w-xs truncate" :title="result.product?.name || result.url">
                  {{ result.product?.name || '—' }}
                </div>
              </td>
              <td class="px-4 py-2 text-slate-700">
                {{ formatCurrency(result.product?.price_supplier) }}
              </td>
              <td class="px-4 py-2 text-slate-700">
                <div class="flex flex-col">
                  <span>{{ availabilityLabel(result.product) }}</span>
                  <span class="text-xs text-slate-500">Stock eficaz: {{ valueOrDash(result.product?.effective_qty) }}</span>
                </div>
              </td>
              <td class="px-4 py-2 text-slate-700">
                <div v-if="result.django_product" class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span class="font-medium">{{ result.django_product.sku }}</span>
                    <span
                      class="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600"
                    >
                      {{ result.django_product.action === 'created' ? 'Creado' : 'Actualizado' }}
                    </span>
                  </div>
                  <p class="text-xs text-slate-500">ID: {{ result.django_product.id }}</p>
                  <p class="text-xs text-slate-500 truncate" :title="result.django_product.nombre">
                    {{ result.django_product.nombre }}
                  </p>
                </div>
                <div v-else class="text-slate-400">—</div>
                <p v-if="result.note" class="mt-1 text-xs text-amber-600">{{ result.note }}</p>
              </td>
              <td class="px-4 py-2 text-blue-600">
                <a :href="result.url" target="_blank" rel="noopener" class="hover:underline">Ver producto</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
      <header class="mb-4 flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 class="text-lg font-medium text-slate-800">Últimos productos importados</h2>
          <p class="text-sm text-slate-500">
            Información reciente en base de datos. Refresca después de cada ejecución para ver los cambios.
          </p>
        </div>
        <div class="flex items-center gap-3">
          <input
            v-model="search"
            type="search"
            placeholder="Buscar por SKU o nombre"
            class="w-64 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
          />
          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            @click="fetchLatest"
            :disabled="latestLoading"
          >
            <span v-if="latestLoading" class="animate-spin">⏳</span>
            <span v-else>🔄</span>
            Actualizar
          </button>
        </div>
      </header>

      <p v-if="latestError" class="text-sm text-red-600">{{ latestError }}</p>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">SKU</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">Nombre</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">Precio proveedor</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">Disponible</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">Stock real</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">Stock eficaz</th>
              <th class="px-4 py-2 text-left font-semibold text-slate-600">Última actualización</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-if="!latestLoading && !latestProducts.length">
              <td colspan="7" class="px-4 py-6 text-center text-slate-500">
                Aún no hay registros para mostrar.
              </td>
            </tr>
            <tr v-for="product in filteredProducts" :key="product.id">
              <td class="px-4 py-2 font-medium text-slate-700">{{ product.supplier_sku }}</td>
              <td class="px-4 py-2 text-slate-700">
                <div class="max-w-sm truncate" :title="product.name">{{ product.name }}</div>
              </td>
              <td class="px-4 py-2 text-slate-700">{{ formatCurrency(product.price_supplier) }}</td>
              <td class="px-4 py-2 text-slate-700">
                <span :class="product.in_stock ? 'text-emerald-600' : 'text-red-600'">
                  {{ product.in_stock ? 'En stock' : 'Agotado' }}
                </span>
              </td>
              <td class="px-4 py-2 text-slate-700">{{ product.available_qty }}</td>
              <td class="px-4 py-2 text-slate-700">{{ product.effective_qty }}</td>
              <td class="px-4 py-2 text-slate-700">{{ formatDate(product.last_seen) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import api, { ensureInterceptors } from '@/axios'

defineOptions({ name: 'SupermexImporter' })

const defaultForm = () => ({
  startUrl: 'https://www.supermexdigital.mx/shop/monitores',
  productUrlsText: '',
  limit: 20,
  maxPages: 3,
  sleepSeconds: 0.6,
  applyUpdates: true,
  http2: true,
})

const form = reactive(defaultForm())
const running = ref(false)
const runError = ref('')
const runSummary = ref(null)

const latestProducts = ref([])
const latestLoading = ref(false)
const latestError = ref('')
const search = ref('')

const hasProductUrls = computed(() => form.productUrlsText.trim().length > 0)

const parseProductUrls = () =>
  form.productUrlsText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)

const resetForm = () => {
  Object.assign(form, defaultForm())
}

const statusLabel = (status) => {
  if (status === 'ok') return 'Importado'
  if (status === 'skipped') return 'Omitido'
  return 'Error'
}

const statusPillClass = (status) => {
  if (status === 'ok') return 'bg-emerald-100 text-emerald-700'
  if (status === 'skipped') return 'bg-slate-100 text-slate-600'
  return 'bg-red-100 text-red-600'
}

const availabilityLabel = (product) => {
  if (!product) return '—'
  return product.in_stock ? 'Disponible' : 'Agotado'
}

const formatCurrency = (value) => {
  if (value === undefined || value === null || value === '') return '—'
  const amount = Number(value)
  if (Number.isNaN(amount)) return value
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
    minimumFractionDigits: 2,
  }).format(amount)
}

const formatDate = (isoString) => {
  if (!isoString) return '—'
  try {
    const date = new Date(isoString)
    return new Intl.DateTimeFormat('es-MX', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(date)
  } catch {
    return isoString
  }
}

const valueOrDash = (value) => {
  if (value === undefined || value === null || value === '') return '—'
  return value
}

const filteredProducts = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return latestProducts.value
  return latestProducts.value.filter((product) => {
    return (
      product.supplier_sku.toLowerCase().includes(term) ||
      product.name.toLowerCase().includes(term)
    )
  })
})

const runScraper = async () => {
  if (!hasProductUrls.value && !form.startUrl) {
    runError.value = 'Debes proporcionar una URL de listado o URLs de producto.'
    return
  }

  runError.value = ''
  running.value = true

  try {
    ensureInterceptors()
    const payload = {
      apply_updates: form.applyUpdates,
      http2: form.http2,
      max_pages: form.maxPages,
      sleep_s: form.sleepSeconds,
    }

    if (typeof form.limit === 'number' && form.limit >= 0) {
      payload.limit = form.limit
    }

    const urls = parseProductUrls()
    if (urls.length) {
      payload.product_urls = urls
    } else {
      payload.start_url = form.startUrl
    }

    const { data } = await api.post(
      'suppliers/supermex/run/', 
      payload,
      { timeout: 600000 } // Timeout de 10 minutos SOLO para el scraper
    )
    runSummary.value = data
    await fetchLatest()
  } catch (error) {
    runError.value =
      error.response?.data?.detail ||
      error.message ||
      'No se pudo ejecutar la importación. Intenta nuevamente.'
  } finally {
    running.value = false
  }
}

const fetchLatest = async () => {
  latestLoading.value = true
  latestError.value = ''

  try {
    ensureInterceptors()
    const params = { limit: 50 }
    if (search.value.trim()) {
      params.search = search.value.trim()
    }
    const { data } = await api.get('suppliers/supermex/products/', { params })
    latestProducts.value = Array.isArray(data) ? data : []
  } catch (error) {
    latestError.value =
      error.response?.data?.detail ||
      'No se pudo obtener la información más reciente.'
  } finally {
    latestLoading.value = false
  }
}

onMounted(fetchLatest)
</script>
