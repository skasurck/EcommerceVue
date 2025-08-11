<script setup>
import { useCarritoStore } from '@/stores/carrito'
const props = defineProps({ producto: { type: Object, required: true } })
const carrito = useCarritoStore()
const agregar = async () => {
  if (props.producto.stock > 0) {
    await carrito.agregar(props.producto)
    props.producto.stock = Math.max(props.producto.stock - 1, 0)
  }
}
const fmt = (n) => Number(n).toLocaleString('es-MX',{style:'currency',currency:'MXN'})
</script>

<template>
  <div class="relative bg-white border border-gray-200 rounded-lg shadow hover:shadow-lg transition duration-200 overflow-hidden">
    <div v-if="producto.stock <= 0" class="absolute top-0 left-0 bg-red-600 text-white text-xs px-2 py-1">Agotado</div>

    <RouterLink :to="`/producto/${producto.id}`" class="block">
      <img :src="producto.miniatura_url || producto.imagen_principal || 'https://via.placeholder.com/300x300?text=Producto'"
           alt="Producto" class="w-full aspect-square object-contain p-3 bg-white" />
    </RouterLink>

    <div class="p-3 space-y-1">
      <RouterLink :to="`/producto/${producto.id}`" class="line-clamp-2 text-[15px] leading-tight hover:underline text-gray-900">
        {{ producto.nombre }}
      </RouterLink>

      <div class="text-[14px] text-gray-500 line-clamp-2">{{ producto.descripcion_corta }}</div>

      <div class="mt-1 text-[18px] font-semibold text-gray-900">
        <template v-if="producto.precio_rebajado">
          <span class="text-red-600">{{ fmt(producto.precio_rebajado) }}</span>
          <span class="text-[13px] text-gray-500 line-through ml-2">{{ fmt(producto.precio_normal) }}</span>
        </template>
        <template v-else>
          {{ fmt(producto.precio_normal) }}
        </template>
      </div>

      <button
        :disabled="producto.stock<=0"
        @click="agregar"
        class="mt-2 w-full rounded-md px-3 py-2 text-sm font-medium
               disabled:bg-gray-300 disabled:cursor-not-allowed
               bg-yellow-400 hover:bg-yellow-300 border border-yellow-500">
        {{ producto.stock>0 ? 'Agregar al carrito' : 'Agotado' }}
      </button>
    </div>
  </div>
</template>
