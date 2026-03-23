<template>
  <div class="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
    <h1 class="text-2xl font-semibold text-gray-900 mb-6">Mi lista de deseos</h1>

    <!-- Loading -->
    <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
      <div v-for="n in 4" :key="n" class="h-64 rounded-lg bg-gray-100 animate-pulse"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="!wishlist.items.length" class="flex flex-col items-center justify-center py-20 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
      <p class="text-lg font-medium text-gray-700">Tu lista de deseos está vacía</p>
      <p class="mt-1 text-sm text-gray-500">Guarda los productos que te interesan para encontrarlos fácilmente.</p>
      <RouterLink to="/productos" class="mt-6 inline-block rounded bg-yellow-400 hover:bg-yellow-500 px-5 py-2 text-sm font-medium text-gray-900">
        Explorar tienda
      </RouterLink>
    </div>

    <!-- Grid -->
    <div v-else>
      <p class="text-sm text-gray-500 mb-4">{{ wishlist.items.length }} {{ wishlist.items.length === 1 ? 'producto guardado' : 'productos guardados' }}</p>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        <div
          v-for="item in wishlist.items"
          :key="item.id"
          class="relative bg-white rounded-lg border shadow-sm group"
        >
          <!-- Remove button -->
          <button
            type="button"
            class="absolute top-2 right-2 z-10 rounded-full bg-white p-1.5 text-rose-400 hover:bg-rose-50 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
            aria-label="Quitar de favoritos"
            @click="quitar(item)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
              <path fill-rule="evenodd" d="M5.47 5.47a.75.75 0 0 1 1.06 0L12 10.94l5.47-5.47a.75.75 0 1 1 1.06 1.06L13.06 12l5.47 5.47a.75.75 0 1 1-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 0 1-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
            </svg>
          </button>

          <RouterLink :to="{ name: 'producto', params: { id: item.producto_id } }" class="block">
            <!-- Image -->
            <div class="relative">
              <img
                :src="item.imagen || placeholder"
                :alt="item.nombre"
                loading="lazy"
                class="aspect-square w-full rounded-t-lg object-cover bg-gray-100"
                :class="isAgotado(item) ? 'opacity-50 grayscale' : ''"
              />
              <div v-if="isAgotado(item)" class="absolute top-2 left-2 rounded-md bg-gray-700 px-2 py-0.5 text-white text-xs font-semibold tracking-wide">
                Agotado
              </div>
            </div>
            <div class="p-3">
              <!-- Price -->
              <div class="flex items-baseline gap-2">
                <p class="text-gray-900 font-semibold">
                  <span class="text-lg">{{ fmt(item.precio_rebajado ?? item.precio_normal) }}</span>
                </p>
                <p v-if="item.precio_rebajado && item.precio_rebajado < item.precio_normal" class="text-xs text-gray-400 line-through">
                  {{ fmt(item.precio_normal) }}
                </p>
              </div>
              <h3 class="mt-1 text-sm text-gray-800 leading-snug line-clamp-2">{{ item.nombre }}</h3>
              <p class="mt-1.5 text-xs text-gray-400">Guardado el {{ formatDate(item.fecha_agregado) }}</p>
            </div>
          </RouterLink>

          <!-- Add to cart -->
          <button
            type="button"
            class="absolute bottom-2 right-2 rounded-full p-2 shadow transition-colors"
            :class="isAgotado(item)
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : agregando === item.producto_id
                ? 'bg-yellow-300 text-gray-700'
                : 'bg-yellow-400 hover:bg-yellow-500 text-gray-900'"
            :disabled="isAgotado(item)"
            :aria-label="isAgotado(item) ? 'Producto agotado' : 'Agregar al carrito'"
            @click.prevent="agregarAlCarrito(item)"
          >
            <!-- X when out of stock -->
            <svg v-if="isAgotado(item)" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4">
              <path fill-rule="evenodd" d="M5.47 5.47a.75.75 0 0 1 1.06 0L12 10.94l5.47-5.47a.75.75 0 1 1 1.06 1.06L13.06 12l5.47 5.47a.75.75 0 1 1-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 0 1-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
            </svg>
            <!-- Plus when available -->
            <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4">
              <path fill-rule="evenodd" d="M12 3.75a.75.75 0 0 1 .75.75v6.75H19.5a.75.75 0 0 1 0 1.5h-6.75V19.5a.75.75 0 0 1-1.5 0v-6.75H4.5a.75.75 0 0 1 0-1.5h6.75V4.5a.75.75 0 0 1 .75-.75Z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useWishlistStore } from '@/stores/wishlist'
import { useCarritoStore } from '@/stores/carrito'

const wishlist = useWishlistStore()
const carrito = useCarritoStore()
const loading = ref(false)
const agregando = ref(null) // producto_id que se está agregando

const placeholder = 'data:image/svg+xml;utf8,' + encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"><rect width="100%" height="100%" fill="#f3f4f6"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#9ca3af" font-family="Arial" font-size="18">Sin imagen</text></svg>`
)

onMounted(async () => {
  if (!wishlist._loaded) {
    loading.value = true
    await wishlist.cargar()
    loading.value = false
  }
})

const isAgotado = (item) => {
  if (item.estado_inventario === 'agotado') return true
  if (item.stock === null || item.stock === undefined) return false
  return Number(item.stock) <= 0
}

const quitar = async (item) => {
  await wishlist.toggle(item.producto_id)
}

const agregarAlCarrito = async (item) => {
  if (isAgotado(item)) return
  agregando.value = item.producto_id
  try {
    // carrito.agregar espera un objeto producto con {id, stock}
    await carrito.agregar({ id: item.producto_id, stock: item.stock ?? 1 }, 1)
  } finally {
    agregando.value = null
  }
}

const fmt = (n) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 2 }).format(n ?? 0)

const formatDate = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>
