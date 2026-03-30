<template>
  <main class="min-h-screen bg-slate-50 dark:bg-slate-900 px-4 py-8">
    <div class="mx-auto max-w-3xl space-y-5">

      <div class="flex items-center gap-3">
        <RouterLink to="/mi-cuenta" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </RouterLink>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-slate-100">Mis pedidos</h1>
      </div>

      <!-- Cargando -->
      <div v-if="cargando" class="space-y-3">
        <div v-for="n in 3" :key="n" class="h-24 rounded-2xl bg-slate-200 dark:bg-slate-700 animate-pulse" />
      </div>

      <!-- Error -->
      <div v-else-if="errorMsg" class="rounded-2xl border border-red-200 bg-red-50 dark:bg-red-950/30 dark:border-red-800 p-5 text-red-700 dark:text-red-400 text-sm">
        {{ errorMsg }}
      </div>

      <template v-else>
        <!-- Sin pedidos -->
        <div v-if="pedidos.length === 0" class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-12 text-center shadow-sm">
          <div class="inline-flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-700 mb-4">
            <svg class="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20 7H4a2 2 0 00-2 2v9a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2zM16 3H8a2 2 0 00-2 2v2h12V5a2 2 0 00-2-2z" />
            </svg>
          </div>
          <p class="text-slate-600 dark:text-slate-400 font-medium">No tienes pedidos todavía</p>
          <RouterLink to="/" class="mt-3 inline-block text-sm text-emerald-600 dark:text-emerald-400 hover:underline font-medium">
            Ir a la tienda →
          </RouterLink>
        </div>

        <!-- Lista de pedidos -->
        <ul v-else class="space-y-3">
          <li
            v-for="(p, i) in pedidos"
            :key="p?.id ?? `row-${i}`"
          >
            <RouterLink
              :to="`/mis-pedidos/${p.id}`"
              class="group block rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm hover:shadow-md hover:border-slate-300 dark:hover:border-slate-600 transition-all"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="space-y-1 min-w-0">
                  <div class="flex items-center gap-2 flex-wrap">
                    <span class="text-sm font-bold text-slate-900 dark:text-slate-100">Pedido #{{ p.id }}</span>
                    <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="estadoClase(p.estado)">
                      {{ estadoTexto(p.estado) }}
                    </span>
                  </div>
                  <p class="text-xs text-slate-500 dark:text-slate-400">{{ formatFecha(p.creado) }}</p>
                </div>
                <div class="flex items-center gap-3 shrink-0">
                  <span class="text-base font-bold text-slate-900 dark:text-slate-100">
                    {{ formatMoney(p.total) }}
                  </span>
                  <svg class="h-4 w-4 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </RouterLink>
          </li>
        </ul>

        <!-- Paginación -->
        <div v-if="totalPages > 1" class="flex items-center justify-center gap-1 pt-2">
          <button
            class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-300 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
            :disabled="page === 1"
            @click="cambiarPagina(page - 1)"
          >‹</button>

          <template v-for="n in paginas" :key="n">
            <span v-if="n === '…'" class="px-2 py-1.5 text-sm text-slate-400">…</span>
            <button
              v-else
              class="px-3 py-1.5 rounded-lg border text-sm font-medium transition-colors"
              :class="n === page
                ? 'bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 border-slate-900 dark:border-slate-100'
                : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'"
              @click="cambiarPagina(n)"
            >{{ n }}</button>
          </template>

          <button
            class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-300 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
            :disabled="page === totalPages"
            @click="cambiarPagina(page + 1)"
          >›</button>
        </div>

        <p v-if="total > 0" class="text-center text-xs text-slate-400 dark:text-slate-500">
          {{ total }} pedido{{ total !== 1 ? 's' : '' }} en total
        </p>
      </template>

    </div>
  </main>
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
  pendiente:  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300',
  pagado:     'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
  confirmado: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
  enviado:    'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300',
  entregado:  'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
  cancelado:  'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
}[estado] ?? 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300')

const estadoTexto = (estado) => ({
  pendiente: 'Pendiente',
  pagado: 'Pagado',
  confirmado: 'Confirmado',
  enviado: 'Enviado',
  entregado: 'Entregado',
  cancelado: 'Cancelado',
}[estado] ?? estado)

const formatFecha = (iso) =>
  iso ? new Date(iso).toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' }) : '—'

const formatMoney = (v) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(Number(v || 0))

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
