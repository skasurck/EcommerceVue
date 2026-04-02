<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Reseñas</h1>
        <p v-if="totalPendientes > 0" class="text-sm text-amber-600 font-medium mt-0.5">
          {{ totalPendientes }} pendiente{{ totalPendientes !== 1 ? 's' : '' }} de aprobación
        </p>
      </div>
      <!-- Tabs -->
      <div class="flex gap-1 rounded-lg border p-1 bg-white text-sm">
        <button
          v-for="tab in tabs" :key="tab.value"
          @click="vistaActual = tab.value; fetchResenas()"
          :class="['px-3 py-1.5 rounded-md font-medium transition-colors',
            vistaActual === tab.value ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100']"
        >{{ tab.label }}</button>
      </div>
    </div>

    <!-- Tabla -->
    <section class="bg-white border rounded-xl shadow-sm overflow-hidden">
      <div v-if="cargando" class="p-8 text-center text-slate-400">Cargando…</div>

      <div v-else-if="!resenas.length" class="p-8 text-center text-slate-400">
        No hay reseñas{{ vistaActual === 'pendientes' ? ' pendientes' : '' }}.
      </div>

      <div v-else class="divide-y">
        <div v-for="r in resenas" :key="r.id" class="p-4 flex flex-col sm:flex-row gap-4">
          <!-- Info producto -->
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 mb-1">
              <!-- Estrellas -->
              <div class="flex">
                <svg v-for="n in 5" :key="n" viewBox="0 0 20 20"
                  :class="['h-4 w-4', n <= r.calificacion ? 'text-amber-400' : 'text-slate-200']"
                  fill="currentColor">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.958a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.448a1 1 0 00-.364 1.118l1.287 3.957c.3.922-.755 1.688-1.54 1.118l-3.37-2.447a1 1 0 00-1.175 0l-3.37 2.447c-.784.57-1.838-.196-1.54-1.118l1.287-3.957a1 1 0 00-.364-1.118L2.063 9.385c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69L9.049 2.927z"/>
                </svg>
              </div>
              <span class="font-semibold text-slate-800 text-sm">{{ r.usuario_nombre }}</span>
              <span v-if="r.verificado" class="text-xs bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded">Compra verificada</span>
              <span class="text-xs text-slate-400">{{ formatFecha(r.creado) }}</span>
            </div>

            <!-- Producto -->
            <p class="text-xs text-slate-500 mb-1">
              Producto #{{ r.producto }}
              <RouterLink :to="`/producto/${r.producto}`" target="_blank" class="text-blue-600 hover:underline ml-1">ver →</RouterLink>
            </p>

            <!-- Comentario -->
            <p v-if="r.comentario" class="text-sm text-slate-700">{{ r.comentario }}</p>
            <p v-else class="text-xs text-slate-400 italic">Sin comentario</p>

            <!-- Estado -->
            <div class="mt-2">
              <span v-if="r.aprobada" class="inline-flex items-center gap-1 text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full">
                <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 00-1.414 0L8 12.586 4.707 9.293a1 1 0 00-1.414 1.414l4 4a1 1 0 001.414 0l8-8a1 1 0 000-1.414z" clip-rule="evenodd"/></svg>
                Aprobada
              </span>
              <span v-else class="inline-flex items-center gap-1 text-xs bg-amber-50 text-amber-700 border border-amber-200 px-2 py-0.5 rounded-full">
                <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/></svg>
                Pendiente
              </span>
            </div>
          </div>

          <!-- Acciones -->
          <div class="flex sm:flex-col gap-2 shrink-0">
            <button v-if="!r.aprobada"
              @click="aprobar(r)"
              :disabled="r._loading"
              class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-sm font-medium"
            >Aprobar</button>
            <button v-else
              @click="rechazar(r)"
              :disabled="r._loading"
              class="px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-100 disabled:opacity-50 text-slate-700 text-sm"
            >Rechazar</button>
            <button
              @click="eliminar(r)"
              :disabled="r._loading"
              class="px-3 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-600 text-sm border border-rose-200"
            >Eliminar</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Paginación -->
    <div v-if="siguiente || pagina > 1" class="flex items-center justify-between text-sm">
      <div class="text-slate-600">Página <span class="font-medium">{{ pagina }}</span></div>
      <div class="flex gap-2">
        <button :disabled="pagina <= 1" @click="fetchResenas(pagina - 1)"
          class="px-3 py-1.5 rounded border border-slate-300 disabled:opacity-50 hover:bg-slate-100">← Anterior</button>
        <button :disabled="!siguiente" @click="fetchResenas(pagina + 1)"
          class="px-3 py-1.5 rounded border border-slate-300 disabled:opacity-50 hover:bg-slate-100">Siguiente →</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import axios from '@/axios'
import { formatFecha } from '@/utils/formatters'

const tabs = [
  { label: 'Pendientes', value: 'pendientes' },
  { label: 'Aprobadas', value: 'aprobadas' },
  { label: 'Todas', value: 'todas' },
]

const vistaActual = ref('pendientes')
const resenas = ref([])
const cargando = ref(false)
const pagina = ref(1)
const siguiente = ref(false)
const totalPendientes = ref(0)

async function fetchResenas(p = 1) {
  pagina.value = p
  cargando.value = true
  try {
    const params = { page: p }
    if (vistaActual.value === 'pendientes') params.pendiente = 1
    else if (vistaActual.value === 'aprobadas') params.aprobada = 1
    const res = await axios.get('resenas/', { params })
    const data = res.data
    resenas.value = (Array.isArray(data?.results) ? data.results : data).map(r => ({ ...r, _loading: false }))
    siguiente.value = Boolean(data?.next)
  } finally {
    cargando.value = false
  }
}

async function fetchPendientesCount() {
  try {
    const res = await axios.get('resenas/', { params: { pendiente: 1, page_size: 1 } })
    totalPendientes.value = res.data?.count ?? 0
  } catch { /* silencioso */ }
}

async function aprobar(r) {
  r._loading = true
  await axios.patch(`resenas/${r.id}/`, { aprobada: true })
  r._loading = false
  fetchResenas(pagina.value)
  fetchPendientesCount()
}

async function rechazar(r) {
  r._loading = true
  await axios.patch(`resenas/${r.id}/`, { aprobada: false })
  r._loading = false
  fetchResenas(pagina.value)
}

async function eliminar(r) {
  if (!confirm('¿Eliminar esta reseña definitivamente?')) return
  r._loading = true
  await axios.delete(`resenas/${r.id}/`)
  fetchResenas(pagina.value)
  fetchPendientesCount()
}

onMounted(() => {
  fetchResenas()
  fetchPendientesCount()
})
</script>
