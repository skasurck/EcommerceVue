<template>
  <div class="space-y-5">
    <!-- Título + CTA -->
    <div class="flex items-center justify-between flex-wrap gap-2">
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
      <div class="flex flex-col sm:flex-row gap-3 sm:items-end">
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

        <div class="flex items-center gap-2 h-10">
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

    <!-- Tabla (desktop lg+) -->
    <section class="bg-white border rounded-xl shadow-sm overflow-hidden">
      <div class="hidden lg:block overflow-x-auto">
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
                  class="h-9 rounded-md border px-2 font-medium text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                  :class="estadoClasses(pedido.estado)"
                >
                  <option value="pendiente">Pendiente</option>
                  <option value="pagado">Pagado</option>
                  <option value="confirmado">Confirmado</option>
                  <option value="enviado">Enviado</option>
                  <option value="cancelado">Cancelado</option>
                  <option value="en_disputa">En disputa</option>
                  <option value="contracargo">Contracargo</option>
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

      <!-- Tarjetas móvil (< lg) -->
      <div class="lg:hidden space-y-3 p-3">
        <div
          v-for="pedido in pedidos"
          :key="pedido.id"
          class="border border-slate-200 rounded-lg p-4 bg-white shadow-sm space-y-3"
        >
          <!-- Fila superior: checkbox + ID + select de estado -->
          <div class="flex items-center gap-3">
            <input type="checkbox" v-model="seleccionados" :value="pedido.id" class="shrink-0" />
            <span class="font-semibold text-slate-800 text-sm">#{{ pedido.id }}</span>
            <div class="ml-auto">
              <select
                v-model="pedido.estado"
                @change="cambiarEstado(pedido)"
                class="h-8 rounded-md border px-2 font-medium text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                :class="estadoClasses(pedido.estado)"
              >
                <option value="pendiente">Pendiente</option>
                <option value="pagado">Pagado</option>
                <option value="confirmado">Confirmado</option>
                <option value="enviado">Enviado</option>
                <option value="cancelado">Cancelado</option>
                <option value="en_disputa">En disputa</option>
                <option value="contracargo">Contracargo</option>
              </select>
            </div>
          </div>

          <!-- Datos del pedido -->
          <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
            <div>
              <span class="text-xs font-medium text-slate-500 block">Cliente</span>
              <span class="text-slate-800">{{ pedido.cliente_nombre_completo }}</span>
            </div>
            <div>
              <span class="text-xs font-medium text-slate-500 block">Fecha</span>
              <span class="text-slate-600">{{ formatFecha(pedido.creado) }}</span>
            </div>
            <div class="col-span-2 mt-1">
              <span class="text-xs font-medium text-slate-500 block">Total</span>
              <span class="text-slate-800 font-semibold">{{ money(pedido.total) }}</span>
            </div>
          </div>

          <!-- Botones de acción -->
          <div class="flex flex-wrap gap-2 pt-1 border-t border-slate-100">
            <button
              @click="verDetalle(pedido.id)"
              class="px-3 py-1.5 rounded border border-slate-300 hover:bg-slate-100 text-sm"
            >
              Ver / Editar
            </button>
            <button
              v-if="!pedido.papelera"
              @click="moverPapelera(pedido.id)"
              class="px-3 py-1.5 rounded border border-slate-300 hover:bg-slate-100 text-sm"
            >
              Papelera
            </button>
            <button
              v-else
              @click="restaurar(pedido.id)"
              class="px-3 py-1.5 rounded border border-slate-300 hover:bg-slate-100 text-sm"
            >
              Restaurar
            </button>
            <button
              v-if="pedido.papelera"
              @click="eliminar(pedido.id)"
              class="px-3 py-1.5 rounded bg-rose-600 hover:bg-rose-700 text-white text-sm"
            >
              Eliminar
            </button>
          </div>
        </div>
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

    <!-- Modal número de guía -->
    <div
      v-if="modalGuia.visible"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      @click.self="cancelarGuia"
    >
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold text-slate-800 mb-1">Marcar como enviado</h3>
        <p class="text-sm text-slate-500 mb-4">
          Ingresa el número de guía de rastreo. Se enviará al cliente por correo.
        </p>
        <label class="block text-xs font-medium text-slate-600 mb-1">Número de guía</label>
        <input
          v-model="modalGuia.numero"
          type="text"
          placeholder="Ej: 1Z9999999999999999"
          class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          @keyup.enter="confirmarGuia"
          ref="inputGuia"
        />
        <p class="text-xs text-slate-400 mt-1">Puedes dejarlo vacío si no tienes guía todavía.</p>
        <div class="flex justify-end gap-3 mt-5">
          <button
            @click="cancelarGuia"
            class="px-4 py-2 rounded border border-slate-300 text-sm hover:bg-slate-100"
          >
            Cancelar
          </button>
          <button
            @click="confirmarGuia"
            class="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium"
          >
            Confirmar envío
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from '@/axios'
import { money, formatFecha } from '@/utils/formatters'

const ESTADO_CLASSES = {
  pendiente:   'bg-amber-50  border-amber-300  text-amber-800',
  pagado:      'bg-emerald-50 border-emerald-400 text-emerald-800',
  confirmado:  'bg-blue-50   border-blue-300   text-blue-800',
  enviado:     'bg-indigo-50 border-indigo-300 text-indigo-800',
  cancelado:   'bg-red-50    border-red-300    text-red-800',
  en_disputa:  'bg-orange-50 border-orange-300 text-orange-800',
  contracargo: 'bg-rose-100  border-rose-400   text-rose-900',
}
const estadoClasses = (estado) =>
  ESTADO_CLASSES[estado] ?? 'bg-slate-50 border-slate-300 text-slate-800'
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
const inputGuia = ref(null)

// Modal de número de guía
const modalGuia = ref({ visible: false, numero: '', pedido: null, bulk: false })

function abrirModalGuia(pedido = null, bulk = false) {
  modalGuia.value = { visible: true, numero: '', pedido, bulk }
  nextTick(() => inputGuia.value?.focus())
}

function cancelarGuia() {
  // Revertir el select si fue un cambio individual
  if (modalGuia.value.pedido) {
    fetchPedidos(pagina.value)
  }
  modalGuia.value.visible = false
}

async function confirmarGuia() {
  const guia = modalGuia.value.numero.trim()
  if (modalGuia.value.bulk) {
    await _aplicarBulkEnviado(guia)
  } else {
    await _cambiarEstadoEnviado(modalGuia.value.pedido, guia)
  }
  modalGuia.value.visible = false
}
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
  if (pedido.estado === 'enviado') {
    abrirModalGuia(pedido, false)
    return
  }
  if (!confirm('¿Cambiar estado del pedido?')) {
    fetchPedidos(pagina.value)
    return
  }
  await axios.patch(`pedidos/${pedido.id}/`, { estado: pedido.estado })
  fetchPedidos(pagina.value)
}

async function _cambiarEstadoEnviado(pedido, numeroGuia) {
  await axios.patch(`pedidos/${pedido.id}/`, { estado: 'enviado', numero_guia: numeroGuia })
  fetchPedidos(pagina.value)
}

async function aplicarBulk() {
  if (!estadoBulk.value) return
  if (estadoBulk.value === 'enviado') {
    abrirModalGuia(null, true)
    return
  }
  if (!confirm('¿Aplicar cambio de estado a seleccionados?')) return
  const res = await axios.post('pedidos/bulk_update_estado/', { ids: seleccionados.value, estado: estadoBulk.value })
  alert(`Actualizados: ${res.data.updated}, Fallidos: ${res.data.failed.length}`)
  fetchPedidos(pagina.value)
}

async function _aplicarBulkEnviado(numeroGuia) {
  if (!confirm('¿Marcar seleccionados como enviados?')) return
  const res = await axios.post('pedidos/bulk_update_estado/', {
    ids: seleccionados.value,
    estado: 'enviado',
    numero_guia: numeroGuia,
  })
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
