<template>
  <Suspense>
    <template #default>
      <div class="max-w-3xl mx-auto p-4" v-if="producto">
        <h1 class="text-2xl font-bold mb-4">{{ producto.nombre }}</h1>

        <img
          v-if="producto.imagen_principal"
          :src="producto.imagen_principal"
          class="w-full max-h-96 object-cover rounded shadow"
          :alt="`Imagen de ${producto.nombre}`"
          loading="lazy"
        />

        <p class="text-blue-600 text-xl font-semibold my-4">
            <span v-if="producto.precio_rebajado">
            <span class="line-through mr-2 text-gray-500">
              ${{ (+producto.precio_normal).toFixed(2) }}
            </span>
              ${{ (+producto.precio_rebajado).toFixed(2) }}
            </span>
            <span v-else>
              ${{ (+producto.precio_normal).toFixed(2) }}
            </span>
        </p>
        <div class="mt-4 flex items-center space-x-2">
          <input
            type="number"
            v-model.number="cantidad"
            min="1"
            class="w-20 border p-1 rounded"
          />
          <button
            @click="agregar"
            class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded"
          >
            Agregar al carrito
          </button>
        </div>

        <table
          v-if="producto.precios_escalonados && producto.precios_escalonados.length"
          class="mt-4 w-full border-collapse text-sm"
        >
          <thead>
            <tr class="bg-gray-100">
              <th class="border p-2 text-left">Desde </th>
              <th class="border p-2 text-left">Precio unitario </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="tier in producto.precios_escalonados"
              :key="tier.id"
            >
              <td class="border p-2">{{ tier.cantidad_minima }}</td>
              <td class="border p-2">
                ${{ (+tier.precio_unitario).toFixed(2) }}
              </td>
            </tr>
          </tbody>
        </table>

        <p class="text-gray-700 whitespace-pre-line">{{ producto.descripcion_larga }}</p>
      </div>
    </template>

    <!-- skeleton -->
    <template #fallback>
      <div class="animate-pulse max-w-3xl mx-auto p-4 space-y-4">
        <div class="h-8 bg-gray-300 rounded w-2/3"></div>
        <div class="h-72 bg-gray-300 rounded"></div>
        <div class="h-6 bg-gray-300 rounded w-1/3"></div>
        <div class="h-24 bg-gray-300 rounded"></div>
      </div>
    </template>
  </Suspense>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { obtenerProducto } from '../services/api'
import { useHead } from '@vueuse/head'      // meta-tags (opcional)
import { useCarritoStore } from '../stores/carrito'

const route = useRoute()
const producto = ref(null)
const cantidad = ref(1)
const carrito = useCarritoStore()

const agregar = () => {
  if (producto.value) {
    carrito.agregar(producto.value.id, cantidad.value)
  }
}

// Cargar producto
onMounted(async () => {
  try {
    const { data } = await obtenerProducto(route.params.id)
    producto.value = data

    // Meta-tags dinámicos
    useHead({
      title: data.nombre,
      meta: [
        { name: 'description', content: (data.descripcion_larga || '').slice(0, 155) }
      ]
    })
  } catch (e) {
    console.error(e)
  }
})
</script>
