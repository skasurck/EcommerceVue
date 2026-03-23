<template>
  <div class="space-y-5">
    <!-- Título + acción -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-slate-800">Gestión de productos</h1>
      <RouterLink
        to="/admin/productos/nuevo"
        class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm"
      >
        ➕ Nuevo producto
      </RouterLink>
    </div>

    <!-- Filtros -->
    <section class="bg-white border rounded-xl p-4 shadow-sm">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <div class="lg:col-span-2">
          <label class="block text-xs font-medium text-slate-500 mb-1">Buscar</label>
          <input
            v-model="filtros.search"
            @input="onSearch"
            type="search"
            placeholder="Nombre, SKU…"
            class="w-full h-10 rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Categoría</label>
          <select
            v-model="filtros.categoria"
            @change="fetchProductos"
            class="w-full h-10 rounded-md border border-slate-300 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas</option>
            <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Estado</label>
          <select
            v-model="filtros.estado"
            @change="fetchProductos"
            class="w-full h-10 rounded-md border border-slate-300 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="en_existencia">En existencia</option>
            <option value="agotado">Agotado</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Marca</label>
          <select
            v-model="filtros.marca"
            @change="fetchProductos"
            class="w-full h-10 rounded-md border border-slate-300 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas</option>
            <option v-for="m in marcas" :key="m.id" :value="m.id">{{ m.nombre }}</option>
          </select>
        </div>
      </div>
    </section>

    <!-- Tabla -->
    <section class="bg-white border rounded-xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-slate-50 text-slate-600 sticky top-0 z-10">
            <tr class="border-b">
              <th class="text-left font-semibold px-3 py-2 w-16">Imagen</th>
              <th class="text-left font-semibold px-3 py-2">Nombre</th>
              <th class="text-left font-semibold px-3 py-2">SKU</th>
              <th class="text-right font-semibold px-3 py-2">Stock</th>
              <th class="text-right font-semibold px-3 py-2">Precio</th>
              <th class="text-right font-semibold px-3 py-2">Rebajado</th>
              <th class="text-left font-semibold px-3 py-2">Categorías</th>
              <th class="text-left font-semibold px-3 py-2">Fecha</th>
              <th class="text-right font-semibold px-3 py-2 w-48">Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr v-if="loading" class="border-b last:border-0">
              <td colspan="9" class="px-3 py-6 text-center text-slate-500">Cargando productos...</td>
            </tr>
            <tr v-else-if="error" class="border-b last:border-0">
              <td colspan="9" class="px-3 py-6 text-center text-rose-500">{{ error }}</td>
            </tr>
            <tr v-else-if="!productos.length" class="border-b last:border-0">
              <td colspan="9" class="px-3 py-6 text-center text-slate-500">No se encontraron productos.</td>
            </tr>
            <template v-else>
              <tr v-for="p in productos" :key="p.id" class="border-b last:border-0 hover:bg-slate-50">
              <!-- Imagen -->
              <td class="px-3 py-2">
                <img v-if="p.imagen_principal" :src="p.imagen_principal" class="w-12 h-12 object-cover rounded border" alt="">
              </td>

              <!-- Nombre -->
              <td class="px-3 py-2">
                <div v-if="editingId !== p.id" class="flex flex-col gap-0.5">
                  <span class="font-medium text-slate-800">{{ p.nombre }}</span>
                  <span v-if="destacadosMap[p.id]?.tipo === 'manual'"
                        class="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5 w-fit">
                    ⭐ Manual
                  </span>
                  <span v-else-if="destacadosMap[p.id]?.tipo === 'automatico'"
                        class="inline-flex items-center gap-1 text-[10px] font-semibold text-blue-600 bg-blue-50 border border-blue-200 rounded px-1.5 py-0.5 w-fit">
                    🤖 Auto
                  </span>
                </div>
                <input
                  v-else v-model="p.nombre"
                  class="w-full h-9 rounded border border-slate-300 px-2 focus:ring-2 focus:ring-blue-500"
                />
              </td>

              <!-- SKU -->
              <td class="px-3 py-2">
                <span v-if="editingId !== p.id" class="text-slate-700">{{ p.sku }}</span>
                <input
                  v-else v-model="p.sku"
                  class="w-full h-9 rounded border border-slate-300 px-2 focus:ring-2 focus:ring-blue-500"
                />
              </td>

              <!-- Stock -->
              <td class="px-3 py-2 text-right">
                <span v-if="editingId !== p.id"
                      :class="p.stock > 0 ? 'text-emerald-700' : 'text-rose-600'">
                  {{ p.stock }}
                </span>
                <input
                  v-else type="number" v-model.number="p.stock"
                  class="w-24 h-9 text-right rounded border border-slate-300 px-2 focus:ring-2 focus:ring-blue-500"
                />
              </td>

              <!-- Precio -->
              <td class="px-3 py-2 text-right">
                <span v-if="editingId !== p.id">{{ money(p.precio_normal) }}</span>
                <input
                  v-else type="number" step="0.01" v-model.number="p.precio_normal"
                  class="w-28 h-9 text-right rounded border border-slate-300 px-2 focus:ring-2 focus:ring-blue-500"
                />
              </td>

              <!-- Rebajado -->
              <td class="px-3 py-2 text-right">
                <span v-if="editingId !== p.id" :class="p.precio_rebajado ? 'text-amber-700' : 'text-slate-500'">
                  {{ p.precio_rebajado ? money(p.precio_rebajado) : '—' }}
                </span>
                <input
                  v-else type="number" step="0.01" v-model.number="p.precio_rebajado"
                  class="w-28 h-9 text-right rounded border border-slate-300 px-2 focus:ring-2 focus:ring-blue-500"
                />
              </td>

              <!-- Categorías -->
              <td class="px-3 py-2">
                <template v-if="editingId !== p.id">
                  <span v-for="(n,i) in categoriasNombres(p.categorias)" :key="i"
                        class="inline-flex items-center px-2 py-0.5 mr-1 mb-1 rounded-full text-[11px] bg-slate-100 border text-slate-700">
                    {{ n }}
                  </span>
                </template>
                <select
                  v-else multiple v-model="p.categorias"
                  class="w-full min-h-[2.25rem] rounded border border-slate-300 px-2 focus:ring-2 focus:ring-blue-500"
                >
                  <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
                </select>
              </td>

              <!-- Fecha -->
              <td class="px-3 py-2 text-slate-600">
                {{ formatDate(p.fecha_creacion) }}
              </td>

              <!-- Acciones -->
              <td class="px-3 py-2">
                <div class="flex justify-end gap-2">
                  <template v-if="editingId === p.id">
                    <button @click="guardar(p)"
                            class="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-700 text-white">
                      Guardar
                    </button>
                    <button @click="cancelar(p)"
                            class="px-3 py-1.5 rounded border border-slate-300 hover:bg-slate-100">
                      Cancelar
                    </button>
                  </template>
                  <template v-else>
                    <!-- Botón destacar / quitar destacado -->
                    <button
                      v-if="!destacadosMap[p.id]"
                      @click="destacar(p)"
                      :disabled="togglingId === p.id"
                      class="px-3 py-1.5 rounded border border-amber-300 text-amber-700 bg-amber-50 hover:bg-amber-100 disabled:opacity-50"
                      title="Marcar como destacado manual"
                    >
                      ⭐ Destacar
                    </button>
                    <button
                      v-else-if="destacadosMap[p.id]?.tipo === 'manual'"
                      @click="quitarDestacado(p)"
                      :disabled="togglingId === p.id"
                      class="px-3 py-1.5 rounded border border-slate-300 text-slate-600 hover:bg-slate-100 disabled:opacity-50"
                      title="Quitar destacado manual"
                    >
                      ✕ Destacado
                    </button>
                    <span
                      v-else
                      class="px-3 py-1.5 rounded border border-blue-200 text-blue-500 text-xs select-none cursor-default"
                      title="Destacado automáticamente por el algoritmo"
                    >
                      🤖 Auto
                    </span>

                    <button @click="editar(p)"
                            class="px-3 py-1.5 rounded border border-slate-300 hover:bg-slate-100">
                      Edición rápida
                    </button>
                    <RouterLink
                      :to="`/admin/productos/editar/${p.id}`"
                      class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      Editar
                  </RouterLink>
                  <button @click="eliminarProducto(p.id)"
                          class="px-3 py-1.5 rounded bg-rose-600 hover:bg-rose-700 text-white">
                    Eliminar
                  </button>
                  </template>
                </div>
              </td>
            </tr>
            </template>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Paginación -->
    <div v-if="pagination.totalPages > 0" class="flex flex-col sm:flex-row items-center justify-between gap-3 text-sm">

      <!-- Info + page size -->
      <div class="flex items-center gap-3 text-slate-500">
        <span>
          {{ totalItems }} producto{{ totalItems !== 1 ? 's' : '' }} ·
          Página <strong class="text-slate-800">{{ pagination.page }}</strong> de
          <strong class="text-slate-800">{{ pagination.totalPages }}</strong>
        </span>
        <select
          v-model.number="pagination.pageSize"
          @change="() => { pagination.page = 1; fetchProductos() }"
          class="h-8 rounded border border-slate-300 px-2 text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option :value="10">10 / pág.</option>
          <option :value="25">25 / pág.</option>
          <option :value="50">50 / pág.</option>
        </select>
      </div>

      <!-- Números de página -->
      <div class="flex items-center gap-1">
        <button
          @click="cambiarPagina(1)"
          :disabled="pagination.page === 1"
          class="px-2 py-1.5 rounded border border-slate-300 disabled:opacity-40 hover:bg-slate-100 transition-colors"
          title="Primera página"
        >«</button>

        <button
          @click="cambiarPagina(pagination.page - 1)"
          :disabled="pagination.page === 1"
          class="px-2 py-1.5 rounded border border-slate-300 disabled:opacity-40 hover:bg-slate-100 transition-colors"
        >‹</button>

        <template v-for="n in paginas" :key="n">
          <span v-if="n === '…'" class="px-2 py-1.5 text-slate-400 select-none">…</span>
          <button
            v-else
            @click="cambiarPagina(n)"
            class="min-w-[2rem] px-2 py-1.5 rounded border transition-colors"
            :class="n === pagination.page
              ? 'bg-blue-600 text-white border-blue-600 font-semibold'
              : 'border-slate-300 hover:bg-slate-100 text-slate-700'"
          >{{ n }}</button>
        </template>

        <button
          @click="cambiarPagina(pagination.page + 1)"
          :disabled="pagination.page === pagination.totalPages"
          class="px-2 py-1.5 rounded border border-slate-300 disabled:opacity-40 hover:bg-slate-100 transition-colors"
        >›</button>

        <button
          @click="cambiarPagina(pagination.totalPages)"
          :disabled="pagination.page === pagination.totalPages"
          class="px-2 py-1.5 rounded border border-slate-300 disabled:opacity-40 hover:bg-slate-100 transition-colors"
          title="Última página"
        >»</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/axios'

defineOptions({ name: 'AdminProductos' })

const router = useRouter()
const route = useRoute()
const productos = ref([])
const categorias = ref([])
const marcas = ref([])
const filtros = reactive({ search: '', categoria: '', estado: '', marca: '' })
const pagination = reactive({ page: 1, totalPages: 1, pageSize: 10 })
const editingId = ref(null)
const cache = ref({})
const loading = ref(false)
const error = ref(null)
// destacadosMap: { [productoId]: { id: destacadoId, tipo: 'manual'|'automatico' } }
const destacadosMap = ref({})
const togglingId = ref(null)

const totalItems = ref(0)

const paginas = computed(() => {
  const t = pagination.totalPages
  const c = pagination.page
  if (t <= 7) return Array.from({ length: t }, (_, i) => i + 1)
  const set = new Set([1, t, c, c - 1, c + 1].filter(n => n >= 1 && n <= t))
  const sorted = [...set].sort((a, b) => a - b)
  const result = []
  for (let i = 0; i < sorted.length; i++) {
    if (i > 0 && sorted[i] - sorted[i - 1] > 1) result.push('…')
    result.push(sorted[i])
  }
  return result
})

const money = (v) => `\$${Number(v ?? 0).toFixed(2)}`
const formatDate = (d) => new Date(d).toLocaleDateString()
const unwrapList = (payload) => {
  if (Array.isArray(payload?.results)) return payload.results
  if (Array.isArray(payload)) return payload
  return []
}

const onSearch = () => {
  pagination.page = 1
  fetchProductos()
}

function categoriasNombres(ids = []) {
  return ids.map(id => categorias.value.find(c => c.id === id)?.nombre || id)
}

async function fetchFiltros() {
  const [catRes, marcaRes] = await Promise.all([
    api.get('categorias/'),
    api.get('marcas/')
  ])
  categorias.value = unwrapList(catRes.data)
  marcas.value = unwrapList(marcaRes.data)
}

async function fetchProductos() {
  loading.value = true
  error.value = null
  try {
    const currentPage = pagination.page
    const params = {
      page: currentPage,
      page_size: pagination.pageSize,
    }
    if (filtros.search) params.search = filtros.search
    if (filtros.categoria) params.categoria = filtros.categoria
    if (filtros.estado) params.estado_inventario = filtros.estado
    if (filtros.marca) params.marca = filtros.marca

    const res = await api.get('productos/', { params })
    const raw = unwrapList(res.data)
    productos.value = raw

    const total = typeof res.data?.count === 'number' ? res.data.count : raw.length
    totalItems.value = total
    const totalPages = Math.max(1, Math.ceil(total / pagination.pageSize))
    if (currentPage > totalPages && total > 0) {
      pagination.page = totalPages
      await fetchProductos()
      return
    }
    pagination.totalPages = totalPages
  } catch (err) {
    console.error('Error cargando productos (admin):', err)
    error.value = 'No se pudieron cargar los productos. Intenta nuevamente más tarde.'
    productos.value = []
    pagination.totalPages = 1
  } finally {
    loading.value = false
  }
}

function cambiarPagina(page) {
  if (page < 1 || page > pagination.totalPages) return
  pagination.page = page
  fetchProductos()
}

function editar(p) {
  editingId.value = p.id
  cache.value = { ...p }
}

function cancelar(p) {
  Object.assign(p, cache.value)
  editingId.value = null
}

async function guardar(p) {
  const payload = {
    nombre: p.nombre,
    sku: p.sku,
    stock: p.stock,
    precio_normal: p.precio_normal,
    precio_rebajado: p.precio_rebajado,
    categorias: p.categorias
  }
  await api.patch(`productos/${p.id}/`, payload)
  editingId.value = null
  fetchProductos()
}

async function fetchDestacados() {
  try {
    // page_size grande para traer todos en una sola petición
    const res = await api.get('admin/destacados/', { params: { page_size: 200 } })
    const lista = Array.isArray(res.data?.results) ? res.data.results : Array.isArray(res.data) ? res.data : []
    const map = {}
    for (const d of lista) {
      map[d.producto] = { id: d.id, tipo: d.tipo }
    }
    destacadosMap.value = map
  } catch (err) {
    console.error('Error cargando destacados:', err)
  }
}

async function destacar(p) {
  togglingId.value = p.id
  try {
    const res = await api.post('admin/destacados/', { producto: p.id, tipo: 'manual' })
    destacadosMap.value = { ...destacadosMap.value, [p.id]: { id: res.data.id, tipo: 'manual' } }
  } catch (err) {
    console.error('Error destacando producto:', err)
    alert('No se pudo destacar el producto.')
  } finally {
    togglingId.value = null
  }
}

async function quitarDestacado(p) {
  const entrada = destacadosMap.value[p.id]
  if (!entrada) return
  togglingId.value = p.id
  try {
    await api.delete(`admin/destacados/${entrada.id}/`)
    const nuevo = { ...destacadosMap.value }
    delete nuevo[p.id]
    destacadosMap.value = nuevo
  } catch (err) {
    console.error('Error quitando destacado:', err)
    alert('No se pudo quitar el destacado.')
  } finally {
    togglingId.value = null
  }
}

async function eliminarProducto(id) {
  if (confirm('¿Estás seguro de que quieres eliminar este producto?')) {
    try {
      await api.delete(`productos/${id}/`)
      await fetchProductos()
    } catch (err) {
      console.error('Error eliminando producto:', err)
      alert('No se pudo eliminar el producto.')
    }
  }
}

onMounted(async () => {
  await Promise.all([fetchFiltros(), fetchDestacados()])
  await fetchProductos()
  if (route.query.actualizado) {
    alert('Producto actualizado correctamente')
    router.replace({ query: {} })
  }
})
</script>
