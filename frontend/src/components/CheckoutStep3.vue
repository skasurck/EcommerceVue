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
      <button type="button" @click="finalizar">Finalizar</button>
    </div>
    <p v-if="error" class="text-red-600 mt-2">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useCheckoutStore } from '../stores/checkout';
import { useCarritoStore } from '../stores/carrito';
import { crearPedido } from '../services/checkout';

const emit = defineEmits(['back', 'complete']);
const router = useRouter();
const store = useCheckoutStore();
const carrito = useCarritoStore();
const auth = useAuthStore();
const metodoPago = ref(store.metodoPago || 'transferencia');
const error = ref('');

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
    }
  })
}

const finalizar = async () => {
  store.metodoPago = metodoPago.value;
  const { save, ...direccion } = store.direccion;
  error.value = '';
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
      save_address: auth.isAuthenticated && save,
    });
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
    await carrito.cargar();
    const payload = { ...resumen, timestamp: Date.now() }
    try {
      sessionStorage.setItem('lastOrderSummary', JSON.stringify(payload))
    } catch (err) {
      console.warn('No se pudo guardar el resumen del pedido', err)
    }
    emit('complete', resumen);
    store.reset();
    const query = payload.id ? { pedido: payload.id } : {}
    await router.push({ name: 'gracias', query })
  } catch (e) {
    console.error(e)
    error.value = e.response?.data?.detail || 'No se pudo crear el pedido';
  }
};

const subtotal = computed(() => Number(carrito.subtotal));
const envio = computed(() => Number(store.metodoEnvio?.costo ?? 0));
const total = computed(() => subtotal.value + envio.value);
</script>
