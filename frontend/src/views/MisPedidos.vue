<template>
  <div class="max-w-3xl mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-4">Mis pedidos</h1>

    <p v-if="cargando" class="text-gray-500">Cargando pedidos…</p>
    <p v-else-if="errorMsg" class="text-red-700">{{ errorMsg }}</p>

    <template v-else>
      <ul class="space-y-2">
        <li
          v-for="(p, i) in pedidos"
          :key="p?.id ?? `row-${i}`"
          class="flex items-center justify-between border p-4 rounded-lg bg-white"
        >
          <div class="space-y-0.5">
            <p class="font-medium">
              Pedido #{{ p.id }}
              <span
                class="ml-2 rounded-full px-2 py-0.5 text-xs font-medium"
                :class="estadoClase(p.estado)"
              >{{ p.estado }}</span>
            </p>
            <p class="text-sm text-gray-500">{{ formatFecha(p.creado) }}</p>
            <p class="text-sm font-semibold">${{ Number(p.total).toFixed(2) }}</p>
          </div>
          <router-link
            :to="`/mis-pedidos/${p.id}`"
            class="text-sm text-blue-700 hover:underline"
          >
            Ver detalle
          </router-link>
        </li>

        <li v-if="pedidos.length === 0" class="text-gray-500 text-center py-10">
          No tienes pedidos todavía.
        </li>
      </ul>

      <!-- Paginación -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-1 mt-6">
        <button
          class="px-3 py-1.5 rounded border text-sm disabled:opacity-40 hover:bg-slate-100 transition-colors"
          :disabled="page === 1"
          @click="cambiarPagina(page - 1)"
        >
          ‹
        </button>

        <template v-for="n in paginas" :key="n">
          <span v-if="n === '…'" class="px-2 py-1.5 text-sm text-gray-400">…</span>
          <button
            v-else
            class="px-3 py-1.5 rounded border text-sm transition-colors"
            :class="n === page ? 'bg-slate-900 text-white border-slate-900' : 'hover:bg-slate-100'"
            @click="cambiarPagina(n)"
          >
            {{ n }}
          </button>
        </template>

        <button
          class="px-3 py-1.5 rounded border text-sm disabled:opacity-40 hover:bg-slate-100 transition-colors"
          :disabled="page === totalPages"
          @click="cambiarPagina(page + 1)"
        >
          ›
        </button>
      </div>

      <p v-if="total > 0" class="text-center text-xs text-gray-400 mt-2">
        {{ total }} pedido{{ total !== 1 ? 's' : '' }} en total
      </p>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { obtenerPedidos } from '@/services/account'

const pedidos   = ref([])
const cargando  = ref(false)
const errorMsg  = ref('')
const page      = ref(1)
const total     = ref(0)
const pageSize  = 10

const totalPages = computed(() => Math.ceil(total.value / pageSize))

const paginas = computed(() => {
  const t = totalPages.value
  const c = page.value
  if (t <= 7) return Array.from({ length: t }, (_, i) => i + 1)
  const pages = new Set([1, t, c, c - 1, c + 1].filter(n => n >= 1 && n <= t))
  const sorted = [...pages].sort((a, b) => a - b)
  const result = []
  for (let i = 0; i < sorted.length; i++) {
    if (i > 0 && sorted[i] - sorted[i - 1] > 1) result.push('…')
    result.push(sorted[i])
  }
  return result
})

const estadoClase = (estado) => ({
  pendiente:  'bg-yellow-100 text-yellow-800',
  pagado:     'bg-blue-100 text-blue-800',
  confirmado: 'bg-blue-100 text-blue-800',
  enviado:    'bg-purple-100 text-purple-800',
  entregado:  'bg-green-100 text-green-800',
  cancelado:  'bg-red-100 text-red-800',
}[estado] ?? 'bg-gray-100 text-gray-700')

const formatFecha = (iso) =>
  iso ? new Date(iso).toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' }) : '—'

const cargarPedidos = async () => {
  cargando.value = true
  errorMsg.value = ''
  try {
    const { data } = await obtenerPedidos(page.value)
    if (Array.isArray(data)) {
      pedidos.value = data.filter(Boolean)
      total.value = data.length
    } else {
      pedidos.value = (data.results ?? []).filter(Boolean)
      total.value = data.count ?? 0
    }
  } catch (e) {
    pedidos.value = []
    errorMsg.value = e?.response?.status === 403
      ? 'No autorizado. Inicia sesión.'
      : 'Error al cargar pedidos.'
  } finally {
    cargando.value = false
  }
}

const cambiarPagina = (n) => {
  if (n < 1 || n > totalPages.value || n === page.value) return
  page.value = n
  cargarPedidos()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(cargarPedidos)
</script>
