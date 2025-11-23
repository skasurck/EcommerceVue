<template>
  <div>
    <div>
      <label>
        <input type="radio" value="transferencia" v-model="metodoPago" />
        Transferencia directa
      </label>
      <div v-if="metodoPago === 'transferencia'" class="border p-2 mt-2">
        <p>Banco: 0000</p>
        <p>CLABE: 000000000000000000</p>
      </div>
    </div>
    <div class="mt-2">
      <label>
        <input type="radio" value="tarjeta" v-model="metodoPago" />
        Pago con tarjeta
      </label>
      <div v-if="metodoPago === 'tarjeta'" class="border p-2 mt-2">
        <p>El pago se procesará mediante la pasarela seleccionada.</p>
      </div>
    </div>
    <div class="mt-2">
      <label>
        <input type="radio" value="mercadopago" v-model="metodoPago" />
        Mercado Pago
      </label>
      <div v-if="metodoPago === 'mercadopago'" class="border p-2 mt-2 space-y-3">
        <p>Serás redirigido a Mercado Pago para completar tu compra de forma segura.</p>
        <div>
          <div id="walletBrick_container" class="min-h-[48px]"></div>
          <p v-if="creatingPreference" class="text-sm text-gray-500 mt-2">
            Preparando tu checkout de Mercado Pago...
          </p>
          <p v-else-if="preferenceId" class="text-sm text-gray-500 mt-2">
            Usa el botón de Mercado Pago de arriba para completar el pago.
          </p>
        </div>
      </div>
    </div>
    <div class="mt-4 p-4 border rounded">
      <div class="flex justify-between">
        <span>Subtotal</span>
        <span>${{ subtotal.toFixed(2) }}</span>
      </div>
      <div class="flex justify-between">
        <span>Envío</span>
        <span>${{ envio.toFixed(2) }}</span>
      </div>
      <div class="flex justify-between font-bold">
        <span>Total</span>
        <span>${{ total.toFixed(2) }}</span>
      </div>
    </div>
    <div class="flex gap-2 mt-4">
      <button type="button" @click="emit('back')">Atrás</button>
      <button
        type="button"
        @click="finalizar"
        :disabled="disableFinalizeButton"
      >
        {{ finalizarLabel }}
      </button>
    </div>
    <p v-if="error" class="text-red-600 mt-2">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCheckoutStore } from '../stores/checkout'
import { useCarritoStore } from '../stores/carrito'
import { crearPedido } from '../services/checkout'
import { createMercadoPagoPreference } from '../services/pagos'

const emit = defineEmits(['back', 'complete'])
const router = useRouter()
const store = useCheckoutStore()
const carrito = useCarritoStore()
const auth = useAuthStore()
const metodoPago = ref(store.metodoPago || 'transferencia')
const error = ref('')
const creatingPreference = ref(false)
const preferenceId = ref(null)
const walletBrickController = ref(null)
const mpInstance = ref(null)
const mpPublicKey =
  import.meta.env.VITE_MP_PUBLIC_KEY ||
  import.meta.env.VITE_MP_PUBLIC_KEY_TEST ||
  ''

const buildItemsSnapshot = () => {
  if (!Array.isArray(carrito.items)) return []
  return carrito.items.map((item) => {
    const product = item.producto || {}
    const price =
      Number(
        product.precio_rebajado ??
          product.precio_normal ??
          product.precio ??
          0
      ) || carrito.precioUnitario(item)
    return {
      id: product.id ?? item.id,
      sku: product.sku ?? null,
      name: product.nombre ?? product.name ?? `Producto ${product.id ?? item.id}`,
      quantity: Number(item.cantidad ?? 0),
      price,
      producto: item.producto,
    }
  })
}

const waitForMercadoPago = () => {
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('Mercado Pago no está disponible en SSR'))
  }
  if (window.MercadoPago) return Promise.resolve(window.MercadoPago)
  return new Promise((resolve, reject) => {
    let attempts = 0
    const maxAttempts = 40
    const interval = setInterval(() => {
      attempts += 1
      if (window.MercadoPago) {
        clearInterval(interval)
        resolve(window.MercadoPago)
      } else if (attempts >= maxAttempts) {
        clearInterval(interval)
        reject(new Error('No se pudo cargar el SDK de Mercado Pago'))
      }
    }, 100)
  })
}

const cleanupMercadoPago = async () => {
  preferenceId.value = null
  if (walletBrickController.value?.unmount) {
    try {
      await walletBrickController.value.unmount()
    } catch (err) {
      console.warn('Error al desmontar el wallet brick', err)
    }
  }
  walletBrickController.value = null
  mpInstance.value = null
}

const renderWalletBrick = async (prefId) => {
  if (!mpPublicKey) {
    throw new Error('Configura VITE_MP_PUBLIC_KEY_TEST para usar el SDK de Mercado Pago')
  }
  const MercadoPago = await waitForMercadoPago()
  mpInstance.value = new MercadoPago(mpPublicKey, { locale: 'es-MX' })
  const bricksBuilder = mpInstance.value.bricks()

  if (walletBrickController.value?.unmount) {
    await walletBrickController.value.unmount()
  }

  walletBrickController.value = await bricksBuilder.create('wallet', 'walletBrick_container', {
    initialization: {
      preferenceId: prefId,
    },
    callbacks: {
      onError: (mpError) => {
        console.error('Error en Wallet Brick', mpError)
        error.value = 'No se pudo iniciar el checkout de Mercado Pago'
      },
    },
  })
}

const finalizar = async () => {
  if (metodoPago.value === 'mercadopago' && preferenceId.value) {
    error.value = ''
    return
  }

  store.metodoPago = metodoPago.value
  error.value = ''

  const direccionData = store.direccion || {}
  const { save, ...direccion } = direccionData
  const saveAddress = auth.isAuthenticated && save

  if (metodoPago.value === 'mercadopago') {
    try {
      creatingPreference.value = true
      const response = await crearPedido({
        direccion,
        metodo_envio: store.metodoEnvio?.id,
        metodo_pago: 'mercadopago',
        indicaciones: store.indicaciones,
        save_address: saveAddress,
      })

      const pedido = response.data
      const pedidoId = pedido.id
      const origin = window.location?.origin || 'http://localhost:5173'
      const preferencePayload = {
        items: carrito.items,
        external_reference: pedidoId,
        back_urls: {
          success: `${origin}/gracias`,
          failure: `${origin}/checkout?status=failure`,
          pending: `${origin}/checkout?status=pending`,
        },
        success_url: `${origin}/gracias`,
        failure_url: `${origin}/checkout?status=failure`,
        pending_url: `${origin}/checkout?status=pending`,
      }

      const preferenceResponse = await createMercadoPagoPreference(preferencePayload)
      const { init_point, preference_id } = preferenceResponse.data || {}

      if (preference_id && mpPublicKey) {
        preferenceId.value = preference_id
        await renderWalletBrick(preference_id)
        return
      }

      if (init_point) {
        window.location.href = init_point
        return
      }

      throw new Error('Mercado Pago no devolvió datos suficientes')
    } catch (e) {
      console.error(e)
      const backendError = e.response?.data?.error || e.response?.data?.detail
      error.value = backendError || e.message || 'No se pudo procesar el pago con Mercado Pago'
      await cleanupMercadoPago()
    } finally {
      creatingPreference.value = false
    }
    return
  }

  const snapshotItems = buildItemsSnapshot()
  const fallbackShipping = Number(store.metodoEnvio?.costo ?? 0)
  const fallbackSubtotal = Number(carrito.subtotal)
  const fallbackTotal = fallbackSubtotal + fallbackShipping
  try {
    const response = await crearPedido({
      direccion,
      metodo_envio: store.metodoEnvio?.id,
      metodo_pago: store.metodoPago,
      indicaciones: store.indicaciones,
      save_address: saveAddress,
    })
    const pedido = response?.data || {}
    const resumen = {
      id: pedido.id ?? pedido.pk ?? null,
      folio: pedido.numero ?? pedido.folio ?? null,
      total: Number(pedido.total ?? fallbackTotal),
      subtotal: Number(pedido.subtotal ?? fallbackSubtotal),
      shipping: Number(pedido.costo_envio ?? fallbackShipping),
      tax: Number(pedido.impuestos ?? 0),
      currency: pedido.moneda ?? 'MXN',
      paymentMethod: store.metodoPago,
      items: Array.isArray(pedido.items) && pedido.items.length
        ? pedido.items.map((item) => ({
            id: item.producto_id ?? item.id,
            sku: item.sku ?? item.producto?.sku ?? null,
            name: item.nombre ?? item.producto?.nombre ?? 'Producto',
            price: Number(item.precio_unitario ?? item.precio ?? 0),
            quantity: Number(item.cantidad ?? 0),
          }))
        : snapshotItems,
    }
    await carrito.cargar()
    const payload = { ...resumen, timestamp: Date.now() }
    try {
      sessionStorage.setItem('lastOrderSummary', JSON.stringify(payload))
    } catch (err) {
      console.warn('No se pudo guardar el resumen del pedido', err)
    }
    emit('complete', resumen)
    store.reset()
    const query = payload.id ? { pedido: payload.id } : {}
    await router.push({ name: 'gracias', query })
  } catch (e) {
    console.error(e)
    error.value = e.response?.data?.detail || 'No se pudo crear el pedido'
  }
}

const subtotal = computed(() => Number(carrito.subtotal))
const envio = computed(() => Number(store.metodoEnvio?.costo ?? 0))
const total = computed(() => subtotal.value + envio.value)

const disableFinalizeButton = computed(() => {
  if (creatingPreference.value) return true
  if (metodoPago.value === 'mercadopago' && preferenceId.value) return true
  return false
})

const finalizarLabel = computed(() => {
  if (creatingPreference.value) return 'Procesando...'
  if (metodoPago.value === 'mercadopago' && preferenceId.value) return 'Listo para pagar'
  return 'Finalizar'
})

watch(
  () => metodoPago.value,
  async (nuevo, anterior) => {
    store.metodoPago = nuevo
    if (nuevo !== 'mercadopago' && anterior === 'mercadopago') {
      await cleanupMercadoPago()
    }
    if (nuevo !== 'mercadopago') {
      error.value = ''
    }
  }
)

onBeforeUnmount(() => {
  cleanupMercadoPago()
})
</script>
