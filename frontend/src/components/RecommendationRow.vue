<script setup>
import { ref, watch, onMounted } from 'vue'
import ProductRow from '@/components/ProductRow.vue'
import {
  obtenerRecomendacionesProducto,
  obtenerRecomendacionesHome,
} from '@/services/api'
import { trackEvento } from '@/composables/useTracking'

const props = defineProps({
  /** 'producto' = recomendaciones para PDP; 'home' = personalizadas */
  scope: { type: String, default: 'home' },
  /** Requerido si scope='producto' */
  productoId: { type: [Number, String], default: null },
  title: { type: String, default: 'Recomendados para ti' },
  to: { type: String, default: '/productos' },
  limit: { type: Number, default: 12 },
  /** Solo aplica al scope 'home': IDs de productos vistos recientemente */
  recientes: { type: Array, default: () => [] },
  /** Solo aplica al scope 'home': categorías sugeridas por el cliente */
  categorias: { type: Array, default: () => [] },
  /** IDs a excluir explícitamente */
  exclude: { type: Array, default: () => [] },
  /** Etiqueta interna para el tracking de impresiones/clicks */
  source: { type: String, default: '' },
})

const emit = defineEmits(['add-to-cart', 'loaded'])

const productos = ref([])
const loading = ref(true)
const errored = ref(false)

async function fetchData() {
  loading.value = true
  errored.value = false
  try {
    const { data } = props.scope === 'producto'
      ? await obtenerRecomendacionesProducto(props.productoId, { limit: props.limit })
      : await obtenerRecomendacionesHome({
          limit: props.limit,
          recientes: props.recientes,
          categorias: props.categorias,
          exclude: props.exclude,
        })
    productos.value = Array.isArray(data) ? data : []

    if (productos.value.length) {
      trackEvento('impression_rec', {
        producto_id: Number(props.productoId) || null,
        metadata: {
          tipo_rec: props.source || props.scope,
          producto_ids: productos.value.map((p) => p.id),
        },
      })
    }
    emit('loaded', productos.value)
  } catch (err) {
    console.error('[recomendaciones] fallo al cargar', err)
    errored.value = true
    productos.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
watch(
  () => [props.scope, props.productoId, props.limit, props.recientes.join(','), props.categorias.join(',')],
  fetchData,
)

function onAddToCart(producto) {
  const idx = productos.value.findIndex((p) => p.id === producto.id)
  trackEvento('click_rec', {
    producto_id: producto.id,
    metadata: {
      tipo_rec: props.source || props.scope,
      pos: idx >= 0 ? idx : null,
      origen_producto_id: Number(props.productoId) || null,
      action: 'add_cart',
    },
  })
  emit('add-to-cart', producto)
}
</script>

<template>
  <!-- Skeleton mientras carga: una fila vacía con el mismo alto, evita CLS -->
  <section v-if="loading" class="mb-8" aria-busy="true" aria-live="polite">
    <div class="flex items-center justify-between mb-3 px-2">
      <div class="h-5 w-48 rounded bg-slate-200 dark:bg-slate-700 animate-pulse"></div>
    </div>
    <div class="overflow-x-auto">
      <div class="flex gap-4 pr-4 pl-2">
        <div
          v-for="i in 6"
          :key="i"
          class="w-56 shrink-0 h-72 rounded-xl bg-slate-100 dark:bg-slate-800 animate-pulse"
        />
      </div>
    </div>
  </section>

  <ProductRow
    v-else-if="productos.length"
    :title="title"
    :productos="productos"
    :to="to"
    @add-to-cart="onAddToCart"
  />
  <!-- Si tras el fallback no hay nada, no renderizamos nada para no dejar hueco -->
</template>
