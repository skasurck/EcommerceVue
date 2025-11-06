<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-4">Categoría: {{ $route.params.categoriaId }}</h1>
    <div v-if="loading">Cargando...</div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <ProductCard v-for="producto in productos" :key="producto.id" :producto="producto" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { getProductos } from '../api/productos';

import ProductCard from '../components/ProductCard.vue';

const route = useRoute();
const productos = ref([]);
const loading = ref(false);

const fetchProductosPorCategoria = async () => {
  loading.value = true;
  try {
    const params = {
      categoria: route.params.categoriaId,
    };
    const response = await getProductos(params);
    productos.value = response.data.results;
  } catch (error) {
    console.error('Error fetching products by category:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchProductosPorCategoria);
</script>
