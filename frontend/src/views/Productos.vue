<template>
  <div class="p-4 max-w-7xl mx-auto">
    <h1 class="text-2xl font-bold mb-6 text-center text-gray-800">🛍️ Productos Disponibles</h1>

    <div v-if="productos.length === 0" class="text-center text-gray-500">Cargando productos...</div>

    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <div
        v-for="producto in productos"
        :key="producto.id"
        class="bg-white border border-gray-200 rounded-lg shadow hover:shadow-xl transition duration-200 overflow-hidden"
      >
        <RouterLink :to="`/producto/${producto.id}`">
          <img
            v-if="producto.imagen"
            :src="producto.imagen"
            alt="Imagen del producto"
            class="ImagenProducto w-full h-48 object-cover hover:brightness-90 transition"
          />
        </RouterLink>
        <div class="p-4">
          <h2 class="text-lg font-bold">
            <RouterLink :to="`/producto/${producto.id}`" class="text-blue-700 hover:underline">
              {{ producto.nombre }}
            </RouterLink>
          </h2>
          <p class="text-blue-600 font-semibold">
            ${{ Number(producto.precio).toFixed(2) }}
          </p>
          <p class="text-sm text-gray-500">{{ producto.descripcion }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { obtenerProductos } from '../services/api.js'
import { RouterLink } from 'vue-router'
defineOptions({ name: 'ProductosView' })

const productos = ref([])

onMounted(async () => {
  try {
    const response = await obtenerProductos()
    productos.value = response.data
  } catch (error) {
    console.error('Error cargando productos:', error)
  }
})
</script>

<style scoped>
h1 {
  color: #333;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  padding: 8px;
  border-bottom: 1px solid #ccc;
}
li:last-child {
  border-bottom: none;
}
.ImagenProducto {
  width: 250px;
  height: auto;
  object-fit: cover;
}
</style>