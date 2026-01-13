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
                <img v-if="p.miniatura" :src="p.miniatura" class="w-12 h-12 object-cover rounded border" alt="">
              </td>

              <!-- Nombre -->
              <td class="px-3 py-2">
                <span v-if="editingId !== p.id" class="font-medium text-slate-800">{{ p.nombre }}</span>
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
    <div class="flex items-center justify-between text-sm">
      <div class="text-slate-600">
        Página <span class="font-medium text-slate-800">{{ pagination.page }}</span>
        de <span class="font-medium text-slate-800">{{ pagination.totalPages }}</span>
      </div>
      <div class="flex gap-2">
        <button
          @click="cambiarPagina(pagination.page - 1)"
          :disabled="pagination.page === 1"
          class="px-3 py-1.5 rounded border border-slate-300 disabled:opacity-50 hover:bg-slate-100"
        >
          ← Anterior
        </button>
        <button
          @click="cambiarPagina(pagination.page + 1)"
          :disabled="pagination.page === pagination.totalPages"
          class="px-3 py-1.5 rounded border border-slate-300 disabled:opacity-50 hover:bg-slate-100"
        >
          Siguiente →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
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

const money = (v) => `\$${Number(v ?? 0).toFixed(2)}`
const formatDate = (d) => new Date(d).toLocaleDateString()
const unwrapList = (payload) => {
  if (Array.isArray(payload?.results)) return payload.results
  if (Array.isArray(payload)) return payload
  return []
}
const normalizeCategoryIds = (raw = []) => {
  if (!Array.isArray(raw)) return []
  const ids = raw
    .map((item) => {
      if (item && typeof item === 'object') {
        return Number(item.id ?? item.pk ?? item.categoria ?? item.category)
      }
      return Number(item)
    })
    .filter((id) => Number.isFinite(id))
  return [...new Set(ids)]
}

const onSearch = () => {
  pagination.page = 1
  fetchProductos()
}

function categoriasNombres(raw = []) {
  const ids = normalizeCategoryIds(raw)
  return ids.map(id => categorias.value.find(c => c.id === id)?.nombre || `ID ${id}`)
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
    productos.value = raw.map((p) => ({
      ...p,
      categorias: normalizeCategoryIds(p.categorias),
    }))

    const total = typeof res.data?.count === 'number' ? res.data.count : raw.length
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
    categorias_ids: p.categorias,
  }
  await api.patch(`productos/${p.id}/`, payload)
  editingId.value = null
  fetchProductos()
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
  await fetchFiltros()
  await fetchProductos()
  if (route.query.actualizado) {
    alert('Producto actualizado correctamente')
    router.replace({ query: {} })
  }
})
</script>
