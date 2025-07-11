<template>
  <Suspense>
    <template #default>
      <div class="max-w-3xl mx-auto p-4" v-if="producto">
        <h1 class="text-2xl font-bold mb-4">{{ producto.nombre }}</h1>

        <img
          v-if="producto.imagen"
          :src="producto.imagen"
          class="w-full max-h-96 object-cover rounded shadow"
          :alt="`Imagen de ${producto.nombre}`"
          loading="lazy"
        />

        <p class="text-blue-600 text-xl font-semibold my-4">
          ${{ (+producto.precio).toFixed(2) }}
        </p>

        <p class="text-gray-700 whitespace-pre-line">{{ producto.descripcion }}</p>
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

const route = useRoute()
const producto = ref(null)

// Cargar producto
onMounted(async () => {
  try {
    const { data } = await obtenerProducto(route.params.id)
    producto.value = data

    // Meta-tags dinámicos
    useHead({
      title: data.nombre,
      meta: [
        { name: 'description', content: data.descripcion.slice(0, 155) }
      ]
    })
  } catch (e) {
    console.error(e)
  }
})
</script>
