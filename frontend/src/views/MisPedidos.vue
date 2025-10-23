<template>
  <div class="max-w-6xl mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-4">Mis pedidos</h1>

    <!-- Mensajes de estado -->
    <p v-if="cargando" class="mb-4 text-gray-600">Cargando pedidos…</p>
    <p v-if="errorMsg" class="mb-4 text-red-700">{{ errorMsg }}</p>

    <!-- Detalle -->
    <div v-if="detalle" class="mb-4 border rounded p-4 bg-white">
      <h3 class="font-semibold mb-2">Pedido #{{ detalle?.id ?? '—' }}</h3>
      <p class="mb-2">
        Total: {{ detalle?.total ?? '—' }} — Estado: {{ detalle?.estado ?? '—' }}
      </p>

      <div class="grid sm:grid-cols-2 gap-4 text-sm">
        <div>
          <h4 class="font-medium">Productos</h4>
          <ul class="list-disc ml-5">
            <li
              v-for="(it, i) in (detalle?.detalles ?? [])"
              :key="it?.producto ?? `det-${i}`"
            >
              {{ it?.producto_nombre ?? '—' }}
              — {{ it?.cantidad ?? '—' }}
              × {{ it?.precio_unitario ?? '—' }}
              = {{ it?.subtotal ?? '—' }}
            </li>
          </ul>
        </div>

        <div>
          <h4 class="font-medium">Envío</h4>
          <p>
            {{ detalle?.direccion?.calle ?? '' }}
            {{ detalle?.direccion?.numero_exterior ?? '' }},
            {{ detalle?.direccion?.ciudad ?? '' }}
          </p>

          <h4 class="mt-2 font-medium">Pago</h4>
          <p>{{ detalle?.metodo_pago_display ?? '—' }}</p>
        </div>
      </div>
    </div>

    <!-- Listado -->
    <ul class="space-y-2" v-if="!cargando">
      <li
        v-for="(p, i) in pedidosFiltrados"
        :key="p?.id ?? `row-${i}`"
        class="flex items-center justify-between border p-3 rounded bg-white"
      >
        <div>
          <div>
            Pedido #{{ p?.id ?? '—' }} ·
            <span class="text-gray-600">Estado:</span>
            {{ p?.estado ?? '—' }}
          </div>
          <div class="text-sm text-gray-600">
            Total: {{ p?.total ?? '—' }}
          </div>
        </div>

        <button
          class="text-blue-700 hover:underline disabled:opacity-50"
          @click="ver(p?.id)"
          :disabled="!p?.id || cargandoDetalle"
        >
          {{ cargandoDetalle && detalle?.id === p?.id ? 'Cargando…' : 'Ver detalle' }}
        </button>
      </li>

      <li v-if="pedidosFiltrados.length === 0" class="text-gray-600">
        No hay pedidos para mostrar.
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { obtenerPedidos, obtenerPedido } from '@/services/account'

const pedidos = ref([])          // siempre array
const detalle = ref(null)        // objeto o null
const cargando = ref(false)
const cargandoDetalle = ref(false)
const errorMsg = ref('')

/**
 * Computado: filtra nulos por seguridad.
 */
const pedidosFiltrados = computed(() =>
  Array.isArray(pedidos.value) ? pedidos.value.filter(Boolean) : []
)

/**
 * Acciones
 */
const cargarPedidos = async () => {
  cargando.value = true
  errorMsg.value = ''
  try {
    const r = await obtenerPedidos()
    // DRF: si hay paginación viene como { results: [...] }
    const rows = Array.isArray(r?.data)
      ? r.data
      : Array.isArray(r?.data?.results)
        ? r.data.results
        : []
    pedidos.value = rows.filter(Boolean)
  } catch (e) {
    pedidos.value = []
    errorMsg.value =
      e?.response?.status === 403
        ? 'No autorizado para ver pedidos. Inicia sesión.'
        : 'Error al cargar pedidos.'
    console.error('Error al cargar pedidos', e)
  } finally {
    cargando.value = false
  }
}

const ver = async (id) => {
  if (!id) return
  cargandoDetalle.value = true
  errorMsg.value = ''
  try {
    const r = await obtenerPedido(id)
    // Normalmente el detalle viene directo en data
    detalle.value = r?.data ?? null
  } catch (e) {
    console.error('Error al cargar detalle', e)
    detalle.value = null
    if (e?.response?.status === 404 || e?.response?.status === 403) {
      errorMsg.value = 'Pedido no encontrado o sin acceso.'
    } else {
      errorMsg.value = 'Error al cargar detalle del pedido.'
    }
  } finally {
    cargandoDetalle.value = false
  }
}

/**
 * Ciclo de vida
 */
onMounted(cargarPedidos)
</script>
