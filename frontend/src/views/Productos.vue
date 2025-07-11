<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Lista de Productos</h1>
    <div v-if="productos.length === 0" class="text-gray-500">Cargando productos...</div>
    <div v-for="producto in productos" :key="producto.id" class="mb-4 border p-4 rounded shadow">
      <img v-if="producto.imagen" :src="getImagenUrl(producto.imagen)" alt="Imagen del producto" class="w-32 h-32 object-cover mb-2">
      <p class="text-lg font-semibold">{{ producto.nombre }} - ${{ producto.precio }}</p>
      <p class="text-sm text-gray-500">{{ producto.descripcion }}</p>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { obtenerProductos } from '../services/api.js'

const productos = ref([])

const getImagenUrl = (path) => {
  return `http://127.0.0.1:8000${path}`  // Asegúrate que MEDIA_URL está expuesto correctamente
}

onMounted(async () => {
  try {
    const response  = await obtenerProductos()
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
</style>