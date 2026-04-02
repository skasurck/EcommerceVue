<template>
  <main class="min-h-screen bg-slate-50 dark:bg-slate-900 px-4 py-8">
    <div class="mx-auto max-w-3xl space-y-5">

      <RouterLink to="/mis-pedidos" class="inline-flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 transition-colors font-medium">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Mis pedidos
      </RouterLink>

      <!-- Cargando -->
      <div v-if="cargando" class="space-y-4">
        <div class="h-20 rounded-2xl bg-slate-200 dark:bg-slate-700 animate-pulse" />
        <div class="h-48 rounded-2xl bg-slate-200 dark:bg-slate-700 animate-pulse" />
      </div>

      <!-- Error -->
      <div v-else-if="errorMsg" class="rounded-2xl border border-red-200 bg-red-50 dark:bg-red-950/30 dark:border-red-800 p-5 text-red-700 dark:text-red-400 text-sm">
        {{ errorMsg }}
      </div>

      <template v-else-if="pedido">

        <!-- Estado -->
        <header class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6 shadow-sm">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 class="text-xl font-bold text-slate-900 dark:text-slate-100">Pedido #{{ pedido.id }}</h1>
              <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{{ fechaFormateada }}</p>
            </div>
            <span class="rounded-full px-3 py-1.5 text-sm font-semibold" :class="estadoClase">
              {{ estadoTexto }}
            </span>
          </div>
        </header>

        <!-- Número de guía -->
        <div
          v-if="pedido.estado === 'enviado' && pedido.numero_guia"
          class="rounded-2xl border border-purple-200 dark:border-purple-800 bg-purple-50 dark:bg-purple-950/30 px-5 py-4 shadow-sm flex items-start gap-3"
        >
          <div class="shrink-0 mt-0.5 text-purple-500 dark:text-purple-400">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1-4H9m0 0a2 2 0 100 4m0-4a2 2 0 110 4" />
            </svg>
          </div>
          <div>
            <p class="text-sm font-semibold text-purple-900 dark:text-purple-200">Tu pedido está en camino 🚚</p>
            <p class="text-xs text-purple-600 dark:text-purple-400 mt-0.5">Número de guía de rastreo</p>
            <p class="mt-1 font-mono text-lg font-bold text-purple-900 dark:text-purple-100 tracking-wide">{{ pedido.numero_guia }}</p>
          </div>
        </div>

        <!-- Artículos -->
        <section class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6 shadow-sm">
          <h2 class="text-base font-semibold text-slate-900 dark:text-slate-100 mb-4">Artículos</h2>
          <ul class="divide-y divide-slate-100 dark:divide-slate-700">
            <li
              v-for="(it, i) in pedido.detalles ?? []"
              :key="it.producto ?? `det-${i}`"
              class="py-3 flex items-center gap-4"
            >
              <img
                v-if="it.producto_imagen"
                :src="it.producto_imagen"
                :alt="it.producto_nombre"
                class="h-14 w-14 rounded-lg object-cover shrink-0 border border-slate-100 dark:border-slate-600"
              />
              <div v-else class="h-14 w-14 rounded-lg border border-slate-100 dark:border-slate-600 bg-slate-100 dark:bg-slate-700 shrink-0" />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-slate-900 dark:text-slate-100 leading-snug">{{ it.producto_nombre ?? '—' }}</p>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  SKU: {{ it.producto_sku ?? 'N/D' }} · Cantidad: {{ it.cantidad }}
                </p>
              </div>
              <p class="text-sm font-semibold text-slate-900 dark:text-slate-100 shrink-0">
                {{ formatMoney(it.subtotal) }}
              </p>
            </li>
          </ul>

          <!-- Totales -->
          <div class="mt-4 border-t border-slate-100 dark:border-slate-700 pt-4 space-y-2">
            <div class="flex justify-between text-sm text-slate-600 dark:text-slate-400">
              <span>Subtotal</span><span>{{ formatMoney(pedido.subtotal) }}</span>
            </div>
            <div v-if="Number(pedido.descuento) > 0" class="flex justify-between text-sm text-emerald-600 dark:text-emerald-400">
              <span>Descuento</span><span>-{{ formatMoney(pedido.descuento) }}</span>
            </div>
            <div class="flex justify-between text-sm text-slate-600 dark:text-slate-400">
              <span>Envío</span><span>{{ formatMoney(pedido.costo_envio) }}</span>
            </div>
            <div class="flex justify-between text-base font-bold text-slate-900 dark:text-slate-100 pt-1 border-t border-slate-100 dark:border-slate-700">
              <span>Total</span><span>{{ formatMoney(pedido.total) }}</span>
            </div>
          </div>
        </section>

        <!-- ── Califica tus productos ── -->
        <section
          v-if="puedeCalificar && productosParaCalificar.length"
          class="rounded-2xl border border-amber-200 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-800 p-6 shadow-sm space-y-4"
        >
          <div class="flex items-center gap-2">
            <span class="text-xl">⭐</span>
            <h2 class="text-base font-semibold text-amber-900 dark:text-amber-200">¿Cómo te fue con tu compra?</h2>
          </div>
          <p class="text-sm text-amber-700 dark:text-amber-400 -mt-1">Tu opinión ayuda a otros compradores. ¡Solo toma un segundo!</p>

          <div class="space-y-4">
            <div
              v-for="item in productosParaCalificar"
              :key="item.producto"
              class="bg-white dark:bg-slate-800 rounded-xl border border-amber-100 dark:border-slate-700 p-4 flex flex-col sm:flex-row gap-4 items-start"
            >
              <!-- Imagen + nombre -->
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <img
                  v-if="item.producto_imagen"
                  :src="item.producto_imagen"
                  :alt="item.producto_nombre"
                  class="h-14 w-14 rounded-lg object-cover shrink-0 border"
                />
                <div v-else class="h-14 w-14 rounded-lg bg-slate-100 dark:bg-slate-700 shrink-0" />
                <p class="text-sm font-medium text-slate-800 dark:text-slate-100 leading-snug line-clamp-2">
                  {{ item.producto_nombre }}
                </p>
              </div>

              <!-- Ya calificado -->
              <div v-if="misResenas[item.producto]" class="shrink-0 flex flex-col items-center gap-1">
                <div class="flex">
                  <svg v-for="n in 5" :key="n" viewBox="0 0 20 20"
                    :class="['h-5 w-5', n <= misResenas[item.producto].calificacion ? 'text-amber-400' : 'text-slate-200']"
                    fill="currentColor">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.958a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.448a1 1 0 00-.364 1.118l1.287 3.957c.3.922-.755 1.688-1.54 1.118l-3.37-2.447a1 1 0 00-1.175 0l-3.37 2.447c-.784.57-1.838-.196-1.54-1.118l1.287-3.957a1 1 0 00-.364-1.118L2.063 9.385c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69L9.049 2.927z"/>
                  </svg>
                </div>
                <span class="text-xs text-slate-500 dark:text-slate-400">
                  {{ misResenas[item.producto].aprobada ? 'Publicada' : 'Pendiente de aprobación' }}
                </span>
              </div>

              <!-- Formulario de calificación -->
              <div v-else class="shrink-0 flex flex-col items-end gap-2">
                <!-- Estrellas interactivas -->
                <div class="flex gap-1">
                  <button
                    v-for="n in 5" :key="n"
                    type="button"
                    @click="setCalificacion(item.producto, n)"
                    @mouseenter="hovers[item.producto] = n"
                    @mouseleave="hovers[item.producto] = 0"
                    class="focus:outline-none"
                  >
                    <svg viewBox="0 0 20 20"
                      :class="['h-7 w-7 transition-colors', n <= (hovers[item.producto] || calificaciones[item.producto] || 0) ? 'text-amber-400' : 'text-slate-300']"
                      fill="currentColor">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.958a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.448a1 1 0 00-.364 1.118l1.287 3.957c.3.922-.755 1.688-1.54 1.118l-3.37-2.447a1 1 0 00-1.175 0l-3.37 2.447c-.784.57-1.838-.196-1.54-1.118l1.287-3.957a1 1 0 00-.364-1.118L2.063 9.385c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69L9.049 2.927z"/>
                    </svg>
                  </button>
                </div>
                <!-- Comentario (expandible al elegir estrellas) -->
                <template v-if="calificaciones[item.producto]">
                  <textarea
                    v-model="comentarios[item.producto]"
                    rows="2"
                    placeholder="Comentario opcional…"
                    class="w-52 rounded-lg border border-slate-200 dark:border-slate-600 px-3 py-1.5 text-sm bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-amber-400 resize-none"
                  />
                  <button
                    @click="enviarCalificacion(item.producto)"
                    :disabled="enviando[item.producto]"
                    class="px-4 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-white text-sm font-medium"
                  >{{ enviando[item.producto] ? 'Enviando…' : 'Enviar reseña' }}</button>
                </template>
                <p v-if="errores[item.producto]" class="text-xs text-rose-500">{{ errores[item.producto] }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Info adicional -->
        <div class="grid sm:grid-cols-2 gap-4">
          <section class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
            <h2 class="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3">Dirección de envío</h2>
            <address class="not-italic text-sm text-slate-600 dark:text-slate-400 space-y-0.5 leading-relaxed">
              <p class="font-medium text-slate-800 dark:text-slate-200">{{ pedido.direccion?.nombre }} {{ pedido.direccion?.apellidos }}</p>
              <p>{{ pedido.direccion?.calle }} {{ pedido.direccion?.numero_exterior }}</p>
              <p>{{ pedido.direccion?.colonia }}, {{ pedido.direccion?.ciudad }}</p>
              <p>{{ pedido.direccion?.estado }}, CP {{ pedido.direccion?.codigo_postal }}</p>
            </address>
          </section>

          <section class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
            <h2 class="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3">Pago</h2>
            <p class="text-sm text-slate-600 dark:text-slate-400">{{ pedido.metodo_pago_display ?? '—' }}</p>
            <h2 class="text-sm font-semibold text-slate-900 dark:text-slate-100 mt-4 mb-1">Fecha del pedido</h2>
            <p class="text-sm text-slate-600 dark:text-slate-400">{{ fechaFormateada }}</p>
          </section>
        </div>

      </template>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { obtenerPedido } from '@/services/account'
import axios from '@/axios'

const route   = useRoute()
const pedido  = ref(null)
const cargando = ref(false)
const errorMsg = ref('')

// ── Calificaciones ──
const misResenas   = ref({})   // { productoId: resenaObj }
const calificaciones = ref({}) // { productoId: 1-5 }
const comentarios  = ref({})   // { productoId: string }
const hovers       = ref({})   // { productoId: 0-5 }
const enviando     = ref({})   // { productoId: bool }
const errores      = ref({})   // { productoId: string }

const ESTADOS_CALIFICABLES = ['pagado', 'confirmado', 'enviado', 'entregado']

const puedeCalificar = computed(() =>
  ESTADOS_CALIFICABLES.includes(pedido.value?.estado)
)

const productosParaCalificar = computed(() =>
  pedido.value?.detalles?.filter(it => it.producto) ?? []
)

function setCalificacion(productoId, n) {
  calificaciones.value = { ...calificaciones.value, [productoId]: n }
}

async function cargarMisResenas() {
  const ids = productosParaCalificar.value.map(it => it.producto).join(',')
  if (!ids) return
  try {
    const res = await axios.get(`resenas/?productos=${ids}&mias=1`)
    const lista = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
    const map = {}
    lista.forEach(r => { map[r.producto] = r })
    misResenas.value = map
  } catch { /* silencioso */ }
}

async function enviarCalificacion(productoId) {
  if (!calificaciones.value[productoId]) return
  enviando.value = { ...enviando.value, [productoId]: true }
  errores.value  = { ...errores.value,  [productoId]: '' }
  try {
    const res = await axios.post('resenas/', {
      producto: productoId,
      calificacion: calificaciones.value[productoId],
      comentario: comentarios.value[productoId] ?? '',
    })
    misResenas.value = { ...misResenas.value, [productoId]: res.data }
  } catch (e) {
    errores.value = { ...errores.value, [productoId]: e.response?.data?.detail || 'Error al enviar.' }
  } finally {
    enviando.value = { ...enviando.value, [productoId]: false }
  }
}

const estadoClase = computed(() => ({
  pendiente:  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300',
  pagado:     'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
  confirmado: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
  enviado:    'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300',
  entregado:  'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
  cancelado:  'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
}[pedido.value?.estado] ?? 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'))

const estadoTexto = computed(() => ({
  pendiente: 'Pendiente', pagado: 'Pagado', confirmado: 'Confirmado',
  enviado: 'Enviado', entregado: 'Entregado', cancelado: 'Cancelado',
}[pedido.value?.estado] ?? pedido.value?.estado ?? '—'))

const fechaFormateada = computed(() => {
  if (!pedido.value?.creado) return '—'
  return new Date(pedido.value.creado).toLocaleDateString('es-MX', {
    year: 'numeric', month: 'long', day: 'numeric',
  })
})

const formatMoney = (v) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(Number(v || 0))

onMounted(async () => {
  cargando.value = true
  try {
    const { data } = await obtenerPedido(route.params.id)
    pedido.value = data
    if (ESTADOS_CALIFICABLES.includes(data.estado)) {
      cargarMisResenas()
    }
  } catch (e) {
    const code = e?.response?.status
    errorMsg.value = code === 404 ? 'Pedido no encontrado.' : 'No se pudo cargar el pedido.'
  } finally {
    cargando.value = false
  }
})
</script>
