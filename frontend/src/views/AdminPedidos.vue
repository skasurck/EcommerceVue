<template>
  <div class="space-y-5">
    <!-- Título + CTA -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-slate-800">Gestión de pedidos</h1>
      <RouterLink
        to="/admin/pedidos/nuevo"
        class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm"
      >
        ➕ Nuevo pedido
      </RouterLink>
    </div>

    <!-- Filtros -->
    <section class="bg-white border rounded-xl p-4 shadow-sm">
      <div class="flex flex-wrap items-center gap-4">
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Estado</label>
          <select
            v-model="estadoFiltro"
            @change="fetchPedidos(1)"
            class="h-10 rounded-md border border-slate-300 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="pendiente">Pendiente</option>
            <option value="pagado">Pagado</option>
            <option value="confirmado">Confirmado</option>
            <option value="enviado">Enviado</option>
            <option value="cancelado">Cancelado</option>
          </select>
        </div>

        <div class="flex items-center gap-2 mt-6 sm:mt-7">
          <label class="relative inline-flex items-center cursor-pointer select-none">
            <input type="checkbox" class="sr-only peer" v-model="verPapelera" @change="fetchPedidos(1)" />
            <div
              class="w-10 h-6 bg-slate-300 rounded-full peer peer-checked:bg-rose-500 transition-colors"
            ></div>
            <div
              class="absolute left-0.5 top-0.5 w-5 h-5 bg-white rounded-full shadow transform transition-transform peer-checked:translate-x-4"
            ></div>
          </label>
          <span class="text-sm text-slate-700">Ver papelera</span>
        </div>
      </div>
    </section>

    <!-- Acciones masivas -->
    <section v-if="seleccionados.length" class="bg-amber-50 border border-amber-200 rounded-xl p-4">
      <div class="flex flex-wrap items-center gap-3">
        <span class="text-sm text-slate-700">
          Seleccionados: <span class="font-semibold">{{ seleccionados.length }}</span>
        </span>

        <select
          v-model="estadoBulk"
          class="h-9 rounded-md border border-amber-300 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500"
        >
          <option disabled value="">Estado…</option>
          <option value="pendiente">Pendiente</option>
          <option value="pagado">Pagado</option>
          <option value="confirmado">Confirmado</option>
          <option value="enviado">Enviado</option>
          <option value="cancelado">Cancelado</option>
        </select>

        <button
          @click="aplicarBulk"
          class="px-3 py-1.5 rounded bg-amber-600 hover:bg-amber-700 text-white text-sm"
        >
          Aplicar
        </button>

        <div class="ml-auto flex gap-2">
          <button
            v-if="!verPapelera"
            @click="bulkTrash"
            class="px-3 py-1.5 rounded border border-slate-300 hover:bg-slate-100 text-sm"
          >
            Mover a papelera
          </button>
          <button
            v-else
            @click="bulkRestore"
            class="px-3 py-1.5 rounded border border-slate-300 hover:bg-slate-100 text-sm"
          >
            Restaurar
          </button>
          <button
            v-if="verPapelera"
            @click="bulkDestroy"
            class="px-3 py-1.5 rounded bg-rose-600 hover:bg-rose-700 text-white text-sm"
          >
            Eliminar definitivamente
          </button>
        </div>
      </div>
    </section>

    <!-- Tabla -->
    <section class="bg-white border rounded-xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-slate-50 text-slate-600 sticky top-0 z-10">
            <tr class="border-b">
              <th class="px-3 py-2 w-10">
                <input type="checkbox" v-model="seleccionarTodo" @change="toggleTodo" />
              </th>
              <th class="text-left font-semibold px-3 py-2 w-20">ID</th>
              <th class="text-left font-semibold px-3 py-2">Cliente</th>
              <th class="text-left font-semibold px-3 py-2">Fecha</th>
              <th class="text-left font-semibold px-3 py-2">Estado</th>
              <th class="text-left font-semibold px-3 py-2">Dirección</th>
              <th class="text-right font-semibold px-3 py-2 w-24">Total</th>
              <th class="text-right font-semibold px-3 py-2 w-64">Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="pedido in pedidos" :key="pedido.id" class="border-b last:border-0 hover:bg-slate-50">
              <td class="px-3 py-2">
                <input type="checkbox" v-model="seleccionados" :value="pedido.id" />
              </td>
              <td class="px-3 py-2 font-medium text-slate-800">#{{ pedido.id }}</td>
              <td class="px-3 py-2 text-slate-800">
                {{ pedido.cliente_nombre_completo }}
              </td>
              <td class="px-3 py-2 text-slate-600">
                {{ formatFecha(pedido.creado) }}
              </td>
              <td class="px-3 py-2">
                <select
                  v-model="pedido.estado"
                  @change="cambiarEstado(pedido)"
                  class="h-9 rounded-md border border-slate-300 px-2 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="pendiente">Pendiente</option>
                  <option value="pagado">Pagado</option>
                  <option value="confirmado">Confirmado</option>
                  <option value="enviado">Enviado</option>
                  <option value="cancelado">Cancelado</option>
                </select>
              </td>
              <td class="px-3 py-2 text-slate-700">
                {{ pedido.direccion_resumen }}
              </td>
              <td class="px-3 py-2 text-right font-medium text-slate-800">
                {{ money(pedido.total) }}
              </td>
              <td class="px-3 py-2">
                <div class="flex justify-end gap-2">
                  <button
                    @click="verDetalle(pedido.id)"
                    class="px-3 py-1.5 rounded border border-slate-300 hover:bg-slate-100"
                  >
                    Ver / Editar
                  </button>
                  <button
                    v-if="!pedido.papelera"
                    @click="moverPapelera(pedido.id)"
                    class="px-3 py-1.5 rounded border border-slate-300 hover:bg-slate-100"
                  >
                    Papelera
                  </button>
                  <button
                    v-else
                    @click="restaurar(pedido.id)"
                    class="px-3 py-1.5 rounded border border-slate-300 hover:bg-slate-100"
                  >
                    Restaurar
                  </button>
                  <button
                    v-if="pedido.papelera"
                    @click="eliminar(pedido.id)"
                    class="px-3 py-1.5 rounded bg-rose-600 hover:bg-rose-700 text-white"
                  >
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Paginación -->
    <div class="flex items-center justify-between text-sm">
      <div class="text-slate-600">Página <span class="font-medium">{{ pagina }}</span></div>
      <div class="flex gap-2">
        <button
          :disabled="pagina<=1"
          @click="fetchPedidos(pagina-1)"
          class="px-3 py-1.5 rounded border border-slate-300 disabled:opacity-50 hover:bg-slate-100"
        >
          ← Anterior
        </button>
        <button
          :disabled="!siguiente"
          @click="fetchPedidos(pagina+1)"
          class="px-3 py-1.5 rounded border border-slate-300 disabled:opacity-50 hover:bg-slate-100"
        >
          Siguiente →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from '@/axios'
import { money, formatFecha } from '@/utils/formatters'
import { useRouter, RouterLink } from 'vue-router'

const pedidos = ref([])
const pagina = ref(1)
const siguiente = ref(false)
const estadoFiltro = ref('')
const seleccionados = ref([])
const seleccionarTodo = ref(false)
const estadoBulk = ref('')
const verPapelera = ref(false)
const router = useRouter()
const unwrapList = (payload) => {
  if (Array.isArray(payload?.results)) return payload.results
  if (Array.isArray(payload)) return payload
  return []
}

async function fetchPedidos(p = 1) {
  pagina.value = p
  const params = { page: p }
  if (estadoFiltro.value) params.estado = estadoFiltro.value
  if (verPapelera.value) params.papelera = 1
  const res = await axios.get('pedidos/', { params })
  pedidos.value = unwrapList(res.data)
  siguiente.value = Boolean(res.data?.next)
  seleccionados.value = []
  seleccionarTodo.value = false
}

function toggleTodo() {
  if (seleccionarTodo.value) {
    seleccionados.value = pedidos.value.map(p => p.id)
  } else {
    seleccionados.value = []
  }
}

async function cambiarEstado(pedido) {
  if (!confirm('¿Cambiar estado del pedido?')) {
    fetchPedidos(pagina.value)
    return
  }
  await axios.patch(`pedidos/${pedido.id}/`, { estado: pedido.estado })
  fetchPedidos(pagina.value)
}

async function aplicarBulk() {
  if (!estadoBulk.value) return
  if (!confirm('¿Aplicar cambio de estado a seleccionados?')) return
  const res = await axios.post('pedidos/bulk_update_estado/', { ids: seleccionados.value, estado: estadoBulk.value })
  alert(`Actualizados: ${res.data.updated}, Fallidos: ${res.data.failed.length}`)
  fetchPedidos(pagina.value)
}

function verDetalle(id) {
  router.push(`/admin/pedidos/${id}`)
}

async function moverPapelera(id) {
  if (!confirm('¿Mover pedido a papelera?')) return
  await axios.post(`pedidos/${id}/trash/`)
  fetchPedidos(pagina.value)
}

async function restaurar(id) {
  if (!confirm('¿Restaurar pedido?')) return
  await axios.post(`pedidos/${id}/restore/`)
  fetchPedidos(pagina.value)
}

async function eliminar(id) {
  if (!confirm('¿Eliminar definitivamente?')) return
  await axios.delete(`pedidos/${id}/`)
  fetchPedidos(pagina.value)
}

async function bulkTrash() {
  if (!confirm('¿Mover seleccionados a papelera?')) return
  const res = await axios.post('pedidos/bulk_trash/', { ids: seleccionados.value })
  alert(`Actualizados: ${res.data.updated}, Fallidos: ${res.data.failed.length}`)
  fetchPedidos(pagina.value)
}

async function bulkRestore() {
  if (!confirm('¿Restaurar seleccionados?')) return
  const res = await axios.post('pedidos/bulk_restore/', { ids: seleccionados.value })
  alert(`Actualizados: ${res.data.updated}, Fallidos: ${res.data.failed.length}`)
  fetchPedidos(pagina.value)
}

async function bulkDestroy() {
  if (!confirm('¿Eliminar definitivamente los seleccionados?')) return
  const res = await axios.post('pedidos/bulk_destroy/', { ids: seleccionados.value })
  alert(`Eliminados: ${res.data.updated}, Fallidos: ${res.data.failed.length}`)
  fetchPedidos(pagina.value)
}

fetchPedidos()
</script>
