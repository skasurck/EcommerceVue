<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="flex flex-col gap-3">
      <h1 class="text-xl font-bold text-slate-800">Estadísticas</h1>

      <!-- Botones de período rápido -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="p in PERIODOS"
          :key="p.key"
          @click="aplicarPeriodo(p)"
          class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
          :class="periodoActivo === p.key
            ? 'bg-slate-800 text-white'
            : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'"
        >
          {{ p.label }}
        </button>
      </div>

      <!-- Rango personalizado en su propia fila -->
      <div class="flex flex-wrap items-center gap-2">
        <input
          type="date" v-model="desde"
          class="flex-1 min-w-0 text-sm border border-slate-200 rounded-lg px-2 py-1.5 text-slate-700"
        />
        <span class="text-slate-400 text-sm shrink-0">—</span>
        <input
          type="date" v-model="hasta"
          class="flex-1 min-w-0 text-sm border border-slate-200 rounded-lg px-2 py-1.5 text-slate-700"
        />
        <button
          @click="cargar"
          class="shrink-0 px-4 py-1.5 bg-cyan-600 text-white text-sm rounded-lg hover:bg-cyan-700 transition-colors"
        >
          Aplicar
        </button>
      </div>
    </div>

    <!-- Loading skeletons -->
    <div v-if="cargando" class="space-y-5">
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div v-for="i in 6" :key="i" class="bg-white rounded-xl p-4 shadow-sm animate-pulse h-24" />
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div class="bg-white rounded-xl p-5 shadow-sm animate-pulse h-64" />
        <div class="bg-white rounded-xl p-5 shadow-sm animate-pulse h-64" />
      </div>
    </div>

    <template v-else-if="datos">

      <!-- Tarjetas de métricas -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div
          v-for="m in metricas"
          :key="m.key"
          class="bg-white rounded-xl p-3 sm:p-4 shadow-sm border border-slate-100"
        >
          <p class="text-[11px] sm:text-xs text-slate-500 mb-1 truncate">{{ m.label }}</p>
          <p class="text-base sm:text-lg font-bold text-slate-800 truncate">{{ m.valor }}</p>
          <div v-if="datos.vs_anterior[m.key] !== null" class="mt-1.5 flex flex-wrap items-center gap-1">
            <span
              class="inline-flex items-center gap-0.5 text-xs font-semibold px-1.5 py-0.5 rounded shrink-0"
              :class="datos.vs_anterior[m.key] >= 0
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-red-50 text-red-700'"
            >
              {{ datos.vs_anterior[m.key] >= 0 ? '▲' : '▼' }}
              {{ Math.abs(datos.vs_anterior[m.key]) }}%
            </span>
            <span class="text-[10px] text-slate-400 hidden sm:inline">vs anterior</span>
          </div>
        </div>
      </div>

      <!-- Gráficas -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div class="bg-white rounded-xl p-4 sm:p-5 shadow-sm border border-slate-100">
          <h2 class="text-sm font-semibold text-slate-700 mb-4">Ventas totales</h2>
          <div class="relative h-52 sm:h-64">
            <Line :data="chartIngresos" :options="chartOpts('$')" />
          </div>
        </div>

        <div class="bg-white rounded-xl p-4 sm:p-5 shadow-sm border border-slate-100">
          <h2 class="text-sm font-semibold text-slate-700 mb-4">Pedidos</h2>
          <div class="relative h-52 sm:h-64">
            <Line :data="chartPedidos" :options="chartOpts('')" />
          </div>
        </div>
      </div>

      <!-- Tablas -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">

        <!-- Top Productos -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
          <div class="px-4 sm:px-5 py-3 sm:py-4 border-b border-slate-100">
            <h2 class="text-sm font-semibold text-slate-700">Principales productos</h2>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm min-w-[360px]">
              <thead>
                <tr class="text-xs text-slate-400 uppercase border-b border-slate-100 bg-slate-50">
                  <th class="px-4 sm:px-5 py-2 text-left font-medium">Producto</th>
                  <th class="px-4 sm:px-5 py-2 text-right font-medium w-20">Cant.</th>
                  <th class="px-4 sm:px-5 py-2 text-right font-medium w-28">Ventas</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-50">
                <tr v-for="p in datos.top_productos" :key="p.slug" class="hover:bg-slate-50">
                  <td class="px-4 sm:px-5 py-2.5">
                    <router-link
                      v-if="p.slug"
                      :to="{ name: 'producto', params: { slug: p.slug } }"
                      class="text-cyan-700 hover:underline font-medium line-clamp-1 text-xs sm:text-sm"
                    >{{ p.nombre }}</router-link>
                    <span v-else class="text-slate-700 line-clamp-1 text-xs sm:text-sm">{{ p.nombre }}</span>
                  </td>
                  <td class="px-4 sm:px-5 py-2.5 text-right text-slate-600 tabular-nums">{{ p.articulos }}</td>
                  <td class="px-4 sm:px-5 py-2.5 text-right text-slate-600 tabular-nums text-xs sm:text-sm">{{ fmt(p.ventas_netas) }}</td>
                </tr>
                <tr v-if="!datos.top_productos.length">
                  <td colspan="3" class="px-5 py-8 text-center text-slate-400 text-sm">Sin datos en este período</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Top Categorías -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
          <div class="px-4 sm:px-5 py-3 sm:py-4 border-b border-slate-100">
            <h2 class="text-sm font-semibold text-slate-700">Principales categorías</h2>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm min-w-[360px]">
              <thead>
                <tr class="text-xs text-slate-400 uppercase border-b border-slate-100 bg-slate-50">
                  <th class="px-4 sm:px-5 py-2 text-left font-medium">Categoría</th>
                  <th class="px-4 sm:px-5 py-2 text-right font-medium w-20">Cant.</th>
                  <th class="px-4 sm:px-5 py-2 text-right font-medium w-28">Ventas</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-50">
                <tr v-for="c in datos.top_categorias" :key="c.nombre" class="hover:bg-slate-50">
                  <td class="px-4 sm:px-5 py-2.5 font-medium text-slate-700 uppercase text-xs tracking-wide">{{ c.nombre }}</td>
                  <td class="px-4 sm:px-5 py-2.5 text-right text-slate-600 tabular-nums">{{ c.articulos }}</td>
                  <td class="px-4 sm:px-5 py-2.5 text-right text-slate-600 tabular-nums text-xs sm:text-sm">{{ fmt(c.ventas_netas) }}</td>
                </tr>
                <tr v-if="!datos.top_categorias.length">
                  <td colspan="3" class="px-5 py-8 text-center text-slate-400 text-sm">Sin datos en este período</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </template>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 text-red-700 rounded-xl p-5 text-sm flex items-center gap-2">
      <span>⚠️</span>
      <span>No se pudieron cargar las estadísticas.</span>
      <button @click="cargar" class="underline ml-1">Reintentar</button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale,
  PointElement, LineElement,
  Title, Tooltip, Legend, Filler,
} from 'chart.js'
import axios from 'axios'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

defineOptions({ name: 'AdminEstadisticas' })

// ── Período ──────────────────────────────────────────────────────────────────
const PERIODOS = [
  { key: 'hoy',       label: 'Hoy',        dias: 0  },
  { key: '7d',        label: '7 días',     dias: 6  },
  { key: '30d',       label: '30 días',    dias: 29 },
  { key: 'mes',       label: 'Este mes',   dias: null },
  { key: 'anio',      label: 'Este año',   dias: null },
]

const periodoActivo = ref('30d')
const hoy = () => new Date().toISOString().slice(0, 10)

const desde = ref('')
const hasta = ref('')

function aplicarPeriodo(p) {
  periodoActivo.value = p.key
  const ahora = new Date()
  hasta.value = hoy()

  if (p.key === 'mes') {
    desde.value = new Date(ahora.getFullYear(), ahora.getMonth(), 1).toISOString().slice(0, 10)
  } else if (p.key === 'anio') {
    desde.value = new Date(ahora.getFullYear(), 0, 1).toISOString().slice(0, 10)
  } else {
    const d = new Date(ahora)
    d.setDate(d.getDate() - (p.dias || 0))
    desde.value = d.toISOString().slice(0, 10)
  }
  cargar()
}

// ── Datos ─────────────────────────────────────────────────────────────────────
const datos   = ref(null)
const cargando = ref(false)
const error   = ref(false)

async function cargar() {
  cargando.value = true
  error.value = false
  try {
    const { data } = await axios.get('/api/pedidos/estadisticas/', {
      params: { desde: desde.value, hasta: hasta.value },
    })
    datos.value = data
  } catch {
    error.value = true
  } finally {
    cargando.value = false
  }
}

onMounted(() => aplicarPeriodo(PERIODOS.find(p => p.key === '30d')))

// ── Tarjetas ──────────────────────────────────────────────────────────────────
const metricas = computed(() => {
  if (!datos.value) return []
  const m = datos.value.metricas
  return [
    { key: 'ventas_totales',    label: 'Ventas totales',       valor: fmt(m.ventas_totales) },
    { key: 'ventas_netas',      label: 'Ventas netas',         valor: fmt(m.ventas_netas) },
    { key: 'total_pedidos',     label: 'Pedidos',              valor: m.total_pedidos },
    { key: 'valor_promedio',    label: 'Valor promedio',       valor: fmt(m.valor_promedio) },
    { key: 'productos_vendidos',label: 'Artículos vendidos',   valor: m.productos_vendidos },
    { key: 'envio_total',       label: 'Envío',                valor: fmt(m.envio_total) },
  ]
})

// ── Gráficas ──────────────────────────────────────────────────────────────────
const AZUL  = 'rgba(6,182,212,1)'
const AZUL_FILL = 'rgba(6,182,212,0.08)'

function buildChart(label, campo) {
  if (!datos.value) return { labels: [], datasets: [] }
  const dias = datos.value.por_dia
  return {
    labels: dias.map(d => {
      const [, m, day] = d.fecha.split('-')
      return `${day}/${m}`
    }),
    datasets: [{
      label,
      data: dias.map(d => d[campo]),
      borderColor: AZUL,
      backgroundColor: AZUL_FILL,
      fill: true,
      tension: 0.35,
      pointRadius: dias.length > 60 ? 0 : 3,
      pointHoverRadius: 5,
    }],
  }
}

const chartIngresos = computed(() => buildChart('Ventas ($)', 'ventas'))
const chartPedidos  = computed(() => buildChart('Pedidos',    'pedidos'))

function chartOpts(prefix) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => prefix === '$'
            ? ` ${fmt(ctx.parsed.y)}`
            : ` ${ctx.parsed.y} pedidos`,
        },
      },
    },
    scales: {
      x: { grid: { display: false }, ticks: { maxTicksLimit: 10, font: { size: 11 } } },
      y: {
        grid: { color: '#f1f5f9' },
        ticks: {
          font: { size: 11 },
          callback: v => prefix === '$' ? `$${Number(v).toLocaleString('es-MX')}` : v,
        },
      },
    },
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmt(n) {
  return `$${Number(n || 0).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}
</script>
