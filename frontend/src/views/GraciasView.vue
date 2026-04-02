<template>
  <main class="bg-slate-50 min-h-screen px-4 py-10">
    <div class="mx-auto max-w-4xl space-y-6">
      <header class="rounded-2xl bg-white p-8 text-center shadow-sm space-y-3" :class="headerClasses">
        <div v-if="mpStatus" class="mb-4">
          <h2 class="text-2xl font-semibold" :class="{
            'text-green-600': mpStatus === 'approved',
            'text-yellow-600': mpStatus === 'pending',
            'text-red-600': mpStatus === 'failure',
          }">
            Pago {{ mpStatusText }}
          </h2>
        </div>
        <div class="inline-flex h-12 w-12 items-center justify-center rounded-full text-white text-2xl" :class="iconClasses">
          {{ statusIcon }}
        </div>
        <h1 class="text-3xl font-semibold text-slate-900">{{ heroTitle }}</h1>
        <p class="text-slate-600">
          {{ heroMessage }}<span v-if="orderId" class="font-semibold text-slate-900"> #{{ orderId }}</span>.
        </p>
        <p v-if="summary" class="text-lg font-medium text-slate-900">
          {{ totalLabel }} <span :class="totalValueClasses">{{ formatMoney(summary.total) }}</span>
        </p>
      </header>

      <section v-if="summary" class="rounded-2xl border bg-white p-6 shadow-sm">
        <h2 class="text-xl font-semibold text-slate-900 mb-4">Resumen del pedido</h2>
        <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <dt class="text-sm text-slate-500">Subtotal</dt>
            <dd class="text-lg font-medium text-slate-900">{{ formatMoney(summary.subtotal) }}</dd>
          </div>
          <div v-if="summary.descuento > 0">
            <dt class="text-sm text-emerald-600">
              Descuento
              <span v-if="summary.cuponCodigo" class="font-mono">({{ summary.cuponCodigo }})</span>
            </dt>
            <dd class="text-lg font-medium text-emerald-600">-{{ formatMoney(summary.descuento) }}</dd>
          </div>
          <div>
            <dt class="text-sm text-slate-500">Envío</dt>
            <dd class="text-lg font-medium text-slate-900">{{ formatMoney(summary.shipping) }}</dd>
          </div>
          <div>
            <dt class="text-sm text-slate-500">Impuestos</dt>
            <dd class="text-lg font-medium text-slate-900">{{ formatMoney(summary.tax) }}</dd>
          </div>
          <div>
            <dt class="text-sm text-slate-500">Pago con</dt>
            <dd class="text-lg font-medium text-slate-900">{{ summary.paymentMethod || 'No disponible' }}</dd>
          </div>
        </dl>
      </section>

      <!-- Datos de transferencia bancaria -->
      <section
        v-if="summary?.paymentMethod?.toLowerCase().includes('transferencia')"
        class="rounded-2xl border-2 border-blue-200 bg-blue-50 p-6 shadow-sm"
      >
        <h2 class="text-xl font-semibold text-blue-900 mb-4 flex items-center gap-2">
          🏦 Datos para depósito / transferencia
        </h2>
        <div v-if="datosBanco" class="space-y-3">
          <dl class="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div v-if="datosBanco.banco">
              <dt class="text-xs font-semibold uppercase tracking-wide text-blue-600">Banco</dt>
              <dd class="mt-0.5 text-lg font-medium text-slate-900">{{ datosBanco.banco }}</dd>
            </div>
            <div v-if="datosBanco.beneficiario">
              <dt class="text-xs font-semibold uppercase tracking-wide text-blue-600">Beneficiario</dt>
              <dd class="mt-0.5 text-lg font-medium text-slate-900">{{ datosBanco.beneficiario }}</dd>
            </div>
            <div v-if="datosBanco.clabe">
              <dt class="text-xs font-semibold uppercase tracking-wide text-blue-600">CLABE interbancaria</dt>
              <dd class="mt-0.5 text-lg font-mono font-semibold text-slate-900 tracking-wider">{{ datosBanco.clabe }}</dd>
            </div>
            <div v-if="datosBanco.numero_cuenta">
              <dt class="text-xs font-semibold uppercase tracking-wide text-blue-600">Número de cuenta</dt>
              <dd class="mt-0.5 text-lg font-mono font-semibold text-slate-900 tracking-wider">{{ datosBanco.numero_cuenta }}</dd>
            </div>
          </dl>
          <p v-if="datosBanco.instrucciones" class="mt-3 text-sm text-blue-800 bg-blue-100 rounded-lg p-3">
            {{ datosBanco.instrucciones }}
          </p>
        </div>
        <p v-else class="text-sm text-blue-700 animate-pulse">Cargando datos bancarios…</p>

        <!-- WhatsApp CTA -->
        <div class="mt-5 flex flex-col sm:flex-row items-center gap-3 rounded-xl bg-green-50 border border-green-200 p-4">
          <div class="text-3xl">💬</div>
          <div class="flex-1 text-center sm:text-left">
            <p class="font-semibold text-slate-900">Envía tu comprobante de pago por WhatsApp</p>
            <p class="text-sm text-slate-600">Una vez realizada la transferencia, mándanos el comprobante para confirmar tu pedido.</p>
          </div>
          <a
            href="https://wa.me/525571666346"
            target="_blank"
            rel="noopener noreferrer"
            class="shrink-0 inline-flex items-center gap-2 rounded-full bg-green-500 hover:bg-green-600 px-5 py-2.5 text-white font-semibold shadow-sm transition-colors"
          >
            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
            </svg>
            Enviar comprobante
          </a>
        </div>
      </section>

      <section v-if="summary?.items?.length" class="rounded-2xl border bg-white p-6 shadow-sm">
        <h2 class="text-xl font-semibold text-slate-900 mb-4">Artículos del pedido</h2>
        <ul class="divide-y divide-slate-200">
          <li v-for="item in summary.items" :key="`${item.id}-${item.sku}`" class="py-3 flex items-center gap-4">
            <img
              v-if="item.image"
              :src="item.image"
              :alt="item.name"
              class="h-14 w-14 rounded object-cover shrink-0"
            />
            <div class="flex-1 min-w-0">
              <p class="font-medium text-slate-900">{{ item.name }}</p>
              <p class="text-sm text-slate-500">
                SKU: {{ item.sku || 'N/D' }} · Cantidad: {{ item.quantity }}
              </p>
            </div>
            <p class="font-semibold text-slate-900 shrink-0">{{ formatMoney(item.price) }}</p>
          </li>
        </ul>
      </section>

      <section class="rounded-2xl border border-dashed border-slate-300 bg-white p-6 shadow-sm">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-600 mb-2">Rastreadores de compra</h2>
        <p class="text-sm text-slate-600">
          Esta página dispara siempre <code class="px-1 py-0.5 bg-slate-100 rounded text-xs">checkout:payment-return</code>
          y solo cuando el pago queda aprobado también <code class="px-1 py-0.5 bg-slate-100 rounded text-xs">checkout:purchase</code>.
          Ambos eventos agregan datos del pedido al <code class="px-1 py-0.5 bg-slate-100 rounded text-xs">window.dataLayer</code>.
        </p>
        <pre class="mt-4 rounded bg-slate-900 p-4 text-xs text-slate-100 overflow-x-auto">
window.addEventListener('checkout:payment-return', (event) => {
  console.log('Retorno de pago', event.detail.status, event.detail.order)
})

window.addEventListener('checkout:purchase', (event) => {
  console.log('Compra confirmada', event.detail)
})
        </pre>
      </section>

      <div class="text-center">
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-full bg-slate-900 px-6 py-3 text-white font-semibold shadow-sm hover:bg-slate-800"
          @click="goHome"
        >
          Seguir comprando
        </button>
      </div>

      <p v-if="!summary" class="text-center text-sm text-slate-500">
        No encontramos los datos del pedido reciente. Si ya realizaste una compra, revisa tu correo.
      </p>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHead } from '@vueuse/head'
import { getOrderByPreferenceId, registrarRetornoMP } from '@/services/pedidos'
import api from '@/axios'
import { useCarritoStore } from '@/stores/carrito'

const route = useRoute()
const router = useRouter()
const carrito = useCarritoStore()
const MP_PENDING_KEY = 'mp_pending_order'
const summary = ref(null)
const purchaseTrackerSent = ref(false)
const returnTrackerSent = ref(false)
const datosBanco = ref(null)
const mpStatus = ref(null)
const mpStatusText = computed(() => {
  if (!mpStatus.value) return ''
  const statuses = {
    approved: 'Aprobado',
    pending: 'Pendiente',
    failure: 'Rechazado',
  }
  return statuses[mpStatus.value] || 'Desconocido'
})

const currencyFormatter = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' })

useHead({ title: 'Gracias por tu compra' })

const orderId = computed(() => summary.value?.id ?? route.query.pedido ?? null)
const formatMoney = (value) => currencyFormatter.format(Number(value || 0))

const paidStates = new Set(['pagado', 'confirmado', 'enviado'])
const pendingStates = new Set(['pendiente'])
const failedStates = new Set(['cancelado', 'fallido'])

const headerClasses = computed(() => ({
  'border border-emerald-100': mpStatus.value === 'approved' || !mpStatus.value,
  'border border-yellow-200': mpStatus.value === 'pending',
  'border border-red-100': mpStatus.value === 'failure',
}))

const iconClasses = computed(() => ({
  'bg-emerald-500': mpStatus.value === 'approved' || !mpStatus.value,
  'bg-yellow-500': mpStatus.value === 'pending',
  'bg-red-500': mpStatus.value === 'failure',
}))

const statusIcon = computed(() => {
  if (mpStatus.value === 'pending') return '⏳'
  if (mpStatus.value === 'failure') return '✕'
  return '✓'
})

const heroTitle = computed(() => {
  if (mpStatus.value === 'pending') return 'Tu pago está en proceso'
  if (mpStatus.value === 'failure') return 'Tu pago no se completó'
  return '¡Gracias por tu compra!'
})

const heroMessage = computed(() => {
  if (mpStatus.value === 'pending') return 'Estamos esperando la confirmación del pago para el pedido'
  if (mpStatus.value === 'failure') return 'Registramos el intento de pago para el pedido'
  return 'Tu pedido ha sido recibido y estamos preparando el envío'
})

const totalLabel = computed(() => {
  if (mpStatus.value === 'pending') return 'Total del pedido:'
  if (mpStatus.value === 'failure') return 'Intento de cobro por:'
  return 'Total pagado:'
})

const totalValueClasses = computed(() => ({
  'text-emerald-600': mpStatus.value === 'approved' || !mpStatus.value,
  'text-yellow-600': mpStatus.value === 'pending',
  'text-red-600': mpStatus.value === 'failure',
}))

const loadPendingOrder = () => {
  try {
    const raw = sessionStorage.getItem(MP_PENDING_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

const clearPendingOrder = () => {
  try {
    sessionStorage.removeItem(MP_PENDING_KEY)
  } catch {
    // noop
  }
}

const normalizeMpStatus = (value, orderState = null) => {
  const raw = String(value || '').toLowerCase()
  if (raw === 'approved' || raw === 'success') return 'approved'
  if (raw === 'pending' || raw === 'in_process' || raw === 'in_process_contingency') return 'pending'
  if (raw === 'failure' || raw === 'rejected' || raw === 'cancelled' || raw === 'cancelado') return 'failure'
  if (paidStates.has(orderState)) return 'approved'
  if (pendingStates.has(orderState)) return 'pending'
  if (failedStates.has(orderState)) return 'failure'
  return null
}

const buildSummary = (orderData) => ({
  id: orderData.id,
  total: orderData.total,
  subtotal: orderData.subtotal,
  descuento: Number(orderData.descuento ?? 0),
  cuponCodigo: orderData.cupon ?? null,
  shipping: orderData.costo_envio,
  tax: 0,
  paymentMethod: orderData.metodo_pago_display,
  items: Array.isArray(orderData.detalles)
    ? orderData.detalles.map(item => ({
        id: item.producto,
        name: item.producto_nombre,
        quantity: item.cantidad,
        price: item.precio_unitario,
        sku: item.producto_sku ?? null,
        image: item.producto_imagen ?? null,
      }))
    : [],
})

const dispatchPurchaseEvent = (payload) => {
  if (!payload || purchaseTrackerSent.value) return
  purchaseTrackerSent.value = true
  const ecommercePayload = {
    transaction_id: payload.id || payload.folio || `pedido-${Date.now()}`,
    value: Number(payload.total || 0),
    currency: payload.currency || 'MXN',
    tax: Number(payload.tax || 0),
    shipping: Number(payload.shipping || 0),
    items: Array.isArray(payload.items)
      ? payload.items.map((item) => ({
          item_id: item.id ?? item.sku,
          item_name: item.name,
          price: Number(item.price || 0),
          quantity: Number(item.quantity || 0),
        }))
      : [],
  }

  window.dataLayer = window.dataLayer || []
  window.dataLayer.push({ event: 'purchase', ecommerce: ecommercePayload })

  window.dispatchEvent(
    new CustomEvent('checkout:purchase', {
      detail: { ...payload, ecommerce: ecommercePayload },
    })
  )
}

const dispatchReturnEvent = (payload, status) => {
  if (!payload || !status || returnTrackerSent.value) return
  returnTrackerSent.value = true

  const ecommercePayload = {
    transaction_id: payload.id || payload.folio || `pedido-${Date.now()}`,
    value: Number(payload.total || 0),
    currency: payload.currency || 'MXN',
    tax: Number(payload.tax || 0),
    shipping: Number(payload.shipping || 0),
    items: Array.isArray(payload.items)
      ? payload.items.map((item) => ({
          item_id: item.id ?? item.sku,
          item_name: item.name,
          price: Number(item.price || 0),
          quantity: Number(item.quantity || 0),
        }))
      : [],
  }

  window.dataLayer = window.dataLayer || []
  window.dataLayer.push({
    event: 'payment_return',
    payment_status: status,
    ecommerce: ecommercePayload,
  })

  window.dispatchEvent(
    new CustomEvent('checkout:payment-return', {
      detail: { status, order: payload, ecommerce: ecommercePayload },
    })
  )
}

const fetchDatosBanco = async () => {
  try {
    const { data } = await api.get('pagos/transferencia/config/')
    datosBanco.value = data
  } catch (err) {
    console.error('No se pudieron cargar los datos bancarios', err)
  }
}

const reconcileOrderStatus = async (orderData, status) => {
  if (!orderData?.id || !status) return orderData

  if (['approved', 'pending', 'failure'].includes(status)) {
    try {
      const { data } = await registrarRetornoMP(orderData.id, status)
      return { ...orderData, estado: data.estado }
    } catch (err) {
      console.error('No se pudo registrar el retorno de Mercado Pago', err)
    }
  }

  return orderData
}

const loadMercadoPagoOrder = async () => {
  const preferenceId = route.query.preference_id || null
  const pendingOrder = loadPendingOrder()

  if (!preferenceId) return false

  const response = await getOrderByPreferenceId(preferenceId)

  const queryStatus =
    route.query.mp_return ||
    route.query.status ||
    route.query.collection_status ||
    null
  let orderData = response.data
  mpStatus.value = normalizeMpStatus(queryStatus, orderData.estado)
  orderData = await reconcileOrderStatus(orderData, mpStatus.value)
  mpStatus.value = normalizeMpStatus(queryStatus, orderData.estado)
  summary.value = buildSummary(orderData)

  dispatchReturnEvent(summary.value, mpStatus.value)

  if (mpStatus.value && pendingOrder?.pedidoId) {
    await carrito.limpiar()
    clearPendingOrder()
  }

  if (mpStatus.value === 'approved' || paidStates.has(orderData.estado)) {
    dispatchPurchaseEvent(summary.value)
  }

  if (summary.value.paymentMethod?.toLowerCase().includes('transferencia')) {
    fetchDatosBanco()
  }

  return true
}

onMounted(async () => {
  try {
    const loadedMpOrder = await loadMercadoPagoOrder()
    if (loadedMpOrder) return
  } catch (error) {
    console.error('Error fetching Mercado Pago order summary:', error)
  }

  const raw = sessionStorage.getItem('lastOrderSummary')
  if (raw) {
    try {
      summary.value = JSON.parse(raw)
      dispatchPurchaseEvent(summary.value)
      if (summary.value.paymentMethod?.toLowerCase().includes('transferencia')) {
        fetchDatosBanco()
      }
    } catch (err) {
      console.error('No se pudo leer el resumen del pedido', err)
    } finally {
      sessionStorage.removeItem('lastOrderSummary')
    }
  }
})

const goHome = () => {
  router.push({ name: 'home' })
}
</script>
