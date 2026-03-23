<template>
  <main class="bg-slate-50 min-h-screen px-4 py-10">
    <div class="mx-auto max-w-4xl space-y-6">
      <header class="rounded-2xl border border-emerald-100 bg-white p-8 text-center shadow-sm space-y-3">
        <div v-if="mpStatus" class="mb-4">
          <h2 class="text-2xl font-semibold" :class="{
            'text-green-600': mpStatus === 'approved',
            'text-yellow-600': mpStatus === 'pending',
            'text-red-600': mpStatus === 'failure',
          }">
            Pago {{ mpStatusText }}
          </h2>
        </div>
        <div class="inline-flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500 text-white text-2xl">
          ✓
        </div>
        <h1 class="text-3xl font-semibold text-slate-900">¡Gracias por tu compra!</h1>
        <p class="text-slate-600">
          Tu pedido <span v-if="orderId" class="font-semibold text-slate-900">#{{ orderId }}</span>
          ha sido recibido y estamos preparando el envío.
        </p>
        <p v-if="summary" class="text-lg font-medium text-slate-900">
          Total pagado: <span class="text-emerald-600">{{ formatMoney(summary.total) }}</span>
        </p>
      </header>

      <section v-if="summary" class="rounded-2xl border bg-white p-6 shadow-sm">
        <h2 class="text-xl font-semibold text-slate-900 mb-4">Resumen del pedido</h2>
        <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <dt class="text-sm text-slate-500">Subtotal</dt>
            <dd class="text-lg font-medium text-slate-900">{{ formatMoney(summary.subtotal) }}</dd>
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
          Esta página dispara el evento <code class="px-1 py-0.5 bg-slate-100 rounded text-xs">checkout:purchase</code>
          y agrega los datos del pedido al <code class="px-1 py-0.5 bg-slate-100 rounded text-xs">window.dataLayer</code>.
          Conecta tus píxeles (Ads, Analytics, Meta, etc.) escuchando ese evento:
        </p>
        <pre class="mt-4 rounded bg-slate-900 p-4 text-xs text-slate-100 overflow-x-auto">
window.addEventListener('checkout:purchase', (event) => {
  const order = event.detail
  // Envía order a tu píxel favorito
  console.log('Compra confirmada', order)
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
import { getOrderByPreferenceId } from '@/services/pedidos'

const route = useRoute()
const router = useRouter()
const summary = ref(null)
const trackerSent = ref(false)
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

const dispatchTrackingEvents = (payload) => {
  if (!payload || trackerSent.value) return
  trackerSent.value = true
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

onMounted(async () => {
  const { status, preference_id } = route.query;

  if (status && preference_id) {
    mpStatus.value = status;
    if (status === 'approved') {
      try {
        const response = await getOrderByPreferenceId(preference_id);
        const orderData = response.data;
        summary.value = {
          id: orderData.id,
          total: orderData.total,
          subtotal: orderData.subtotal,
          shipping: orderData.costo_envio,
          tax: 0, // Ajustar si hay impuestos
          paymentMethod: orderData.metodo_pago_display,
          items: orderData.detalles.map(item => ({
            id: item.producto,
            name: item.producto_nombre,
            quantity: item.cantidad,
            price: item.precio_unitario,
            sku: item.producto_sku ?? null,
            image: item.producto_imagen ?? null,
          })),
        };
        dispatchTrackingEvents(summary.value);
      } catch (error) {
        console.error("Error fetching order by preference ID:", error);
      }
    }
  } else {
    const raw = sessionStorage.getItem('lastOrderSummary')
    if (raw) {
      try {
        summary.value = JSON.parse(raw)
        dispatchTrackingEvents(summary.value)
      } catch (err) {
        console.error('No se pudo leer el resumen del pedido', err)
      } finally {
        sessionStorage.removeItem('lastOrderSummary')
      }
    }
  }
})

const goHome = () => {
  router.push({ name: 'home' })
}
</script>
