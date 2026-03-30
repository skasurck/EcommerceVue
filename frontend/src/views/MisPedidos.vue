<template>
  <main class="min-h-screen bg-slate-50 dark:bg-slate-900 px-4 py-8">
    <div class="mx-auto max-w-4xl space-y-5">

      <!-- Encabezado -->
      <div class="flex items-center gap-3">
        <RouterLink to="/mi-cuenta" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </RouterLink>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-slate-100">Mis pedidos</h1>
        <span v-if="total > 0" class="text-sm text-slate-500 dark:text-slate-400">
          ({{ total }} pedido{{ total !== 1 ? 's' : '' }})
        </span>
      </div>

      <!-- Cargando (skeletons) -->
      <div v-if="cargando" class="space-y-4">
        <div v-for="n in 3" :key="n" class="rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div class="h-12 bg-slate-100 dark:bg-slate-700 animate-pulse" />
          <div class="p-5 flex gap-4">
            <div class="h-16 w-16 rounded-lg bg-slate-200 dark:bg-slate-600 animate-pulse shrink-0" />
            <div class="flex-1 space-y-2">
              <div class="h-4 bg-slate-200 dark:bg-slate-600 rounded animate-pulse w-3/4" />
              <div class="h-3 bg-slate-200 dark:bg-slate-600 rounded animate-pulse w-1/2" />
            </div>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="errorMsg" class="rounded-2xl border border-red-200 bg-red-50 dark:bg-red-950/30 dark:border-red-800 p-5 text-red-700 dark:text-red-400 text-sm">
        {{ errorMsg }}
      </div>

      <template v-else>
        <!-- Sin pedidos -->
        <div v-if="pedidos.length === 0" class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-14 text-center shadow-sm">
          <div class="inline-flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-700 mb-4">
            <svg class="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20 7H4a2 2 0 00-2 2v9a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2zM16 3H8a2 2 0 00-2 2v2h12V5a2 2 0 00-2-2z" />
            </svg>
          </div>
          <p class="text-slate-600 dark:text-slate-400 font-medium text-lg mb-1">No tienes pedidos todavía</p>
          <p class="text-slate-500 dark:text-slate-500 text-sm mb-4">Cuando realices una compra aparecerá aquí.</p>
          <RouterLink to="/" class="inline-flex items-center gap-1.5 text-sm text-emerald-600 dark:text-emerald-400 hover:underline font-semibold">
            Ir a la tienda →
          </RouterLink>
        </div>

        <!-- Lista estilo Amazon -->
        <ul v-else class="space-y-4">
          <li
            v-for="(p, i) in pedidos"
            :key="p?.id ?? `row-${i}`"
            class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm overflow-hidden"
          >
            <!-- ── Cabecera del pedido ── -->
            <div class="bg-slate-50 dark:bg-slate-700/50 border-b border-slate-200 dark:border-slate-700 px-5 py-3">
              <div class="flex flex-wrap items-start justify-between gap-x-6 gap-y-1 text-xs">
                <!-- Izquierda: meta -->
                <div class="flex flex-wrap gap-x-6 gap-y-1">
                  <div>
                    <p class="uppercase font-semibold tracking-wide text-slate-500 dark:text-slate-400">Pedido realizado</p>
                    <p class="text-slate-800 dark:text-slate-200 font-medium mt-0.5">{{ formatFecha(p.creado) }}</p>
                  </div>
                  <div>
                    <p class="uppercase font-semibold tracking-wide text-slate-500 dark:text-slate-400">Total</p>
                    <p class="text-slate-800 dark:text-slate-200 font-medium mt-0.5">{{ formatMoney(p.total) }}</p>
                  </div>
                  <div v-if="p.direccion?.nombre || p.cliente_nombre_completo">
                    <p class="uppercase font-semibold tracking-wide text-slate-500 dark:text-slate-400">Enviar a</p>
                    <p class="text-slate-800 dark:text-slate-200 font-medium mt-0.5">
                      {{ p.cliente_nombre_completo || `${p.direccion?.nombre} ${p.direccion?.apellidos}` }}
                    </p>
                  </div>
                </div>

                <!-- Derecha: número + link -->
                <div class="text-right shrink-0">
                  <p class="uppercase font-semibold tracking-wide text-slate-500 dark:text-slate-400">Pedido N.º {{ p.id }}</p>
                  <RouterLink
                    :to="`/mis-pedidos/${p.id}`"
                    class="mt-0.5 inline-block text-emerald-600 dark:text-emerald-400 hover:underline font-medium"
                  >
                    Ver detalles del pedido
                  </RouterLink>
                </div>
              </div>
            </div>

            <!-- ── Cuerpo: estado + items + acciones ── -->
            <div class="flex flex-col sm:flex-row">
              <!-- Items -->
              <div class="flex-1 p-5 space-y-4 min-w-0">
                <!-- Estado -->
                <div>
                  <p class="text-base font-semibold" :class="estadoColor(p.estado)">
                    {{ estadoTitulo(p.estado, p.numero_guia) }}
                  </p>
                  <p v-if="p.estado === 'enviado' && p.numero_guia" class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-mono">
                    Guía: {{ p.numero_guia }}
                  </p>
                </div>

                <!-- Lista de productos -->
                <div class="space-y-3">
                  <div
                    v-for="(it, j) in (p.detalles ?? []).slice(0, 3)"
                    :key="it.producto ?? `it-${j}`"
                    class="flex items-start gap-3"
                  >
                    <img
                      v-if="it.producto_imagen"
                      :src="it.producto_imagen"
                      :alt="it.producto_nombre"
                      class="h-16 w-16 rounded-lg object-cover border border-slate-100 dark:border-slate-600 shrink-0"
                    />
                    <div v-else class="h-16 w-16 rounded-lg bg-slate-100 dark:bg-slate-700 shrink-0 border border-slate-200 dark:border-slate-600" />
                    <div class="min-w-0">
                      <RouterLink
                        :to="`/mis-pedidos/${p.id}`"
                        class="text-sm font-medium text-slate-900 dark:text-slate-100 hover:text-emerald-600 dark:hover:text-emerald-400 leading-snug line-clamp-2 transition-colors"
                      >
                        {{ it.producto_nombre }}
                      </RouterLink>
                      <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        Cantidad: {{ it.cantidad }}
                      </p>
                    </div>
                  </div>

                  <!-- Indicador si hay más de 3 productos -->
                  <p v-if="(p.detalles ?? []).length > 3" class="text-xs text-slate-500 dark:text-slate-400 pl-0.5">
                    y {{ (p.detalles ?? []).length - 3 }} producto{{ (p.detalles ?? []).length - 3 !== 1 ? 's' : '' }} más en este pedido.
                  </p>
                </div>
              </div>

              <!-- Acciones -->
              <div class="sm:w-52 shrink-0 border-t sm:border-t-0 sm:border-l border-slate-100 dark:border-slate-700 p-5 flex sm:flex-col gap-2">
                <RouterLink
                  :to="`/mis-pedidos/${p.id}`"
                  class="w-full text-center rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2 text-sm font-medium text-slate-800 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors"
                >
                  Ver detalle del pedido
                </RouterLink>
                <a
                  v-if="p.estado === 'enviado' && p.numero_guia"
                  :href="`https://www.fedex.com/fedextrack/?tracknumbers=${p.numero_guia}`"
                  target="_blank"
                  rel="noopener"
                  class="w-full text-center rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2 text-sm font-medium text-slate-800 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors"
                >
                  Rastrear paquete
                </a>
              </div>
            </div>
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

const estadoColor = (estado) => ({
  pendiente:  'text-yellow-600 dark:text-yellow-400',
  pagado:     'text-blue-600 dark:text-blue-400',
  confirmado: 'text-blue-700 dark:text-blue-400',
  enviado:    'text-purple-600 dark:text-purple-400',
  entregado:  'text-emerald-600 dark:text-emerald-400',
  cancelado:  'text-red-600 dark:text-red-400',
}[estado] ?? 'text-slate-600 dark:text-slate-400')

const estadoTitulo = (estado, guia) => ({
  pendiente:  'Pendiente de confirmación',
  pagado:     'Pago recibido',
  confirmado: 'Pedido confirmado',
  enviado:    guia ? 'En camino' : 'Enviado',
  entregado:  'Entregado',
  cancelado:  'Pedido cancelado',
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
