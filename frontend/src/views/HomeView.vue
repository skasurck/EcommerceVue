<script setup>
import { ref, onMounted } from 'vue'
import ProductRow from '@/components/ProductRow.vue'
import ProductCard from '@/components/ProductCard.vue'
import { obtenerProductos } from '@/services/api.js'

const nuevos = ref([])
const ofertas = ref([])
const destacados = ref([])

const fetchBloque = async (params) => {
  const res = await obtenerProductos({ page: 1, page_size: 12, ...params })
  return res.data?.results || []
}

onMounted(async () => {
  // Fetch offers and all products in parallel
  const [ofertasResponse, allProductsResponse] = await Promise.all([
    fetchBloque({ en_oferta: 'true', page_size: 12 }),
    fetchBloque()
  ]);

  ofertas.value = ofertasResponse;
  
  const all = allProductsResponse;

  // Novedades → ordenados por id descendente
  nuevos.value = [...all].sort((a, b) => b.id - a.id).slice(0, 12)
  
  // Destacados (ejemplo: los primeros 12)
  destacados.value = all.slice(0, 12)
})
</script>

<template>
  <main class="bg-gray-100 grid grid-cols-12 min-h-screen">
    <!-- Hero sencillo -->
    <div class="bg-gradient-to-r from-yellow-300 to-yellow-100 col-span-12 mb-6">
      <div class="max-w-7xl mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold">Bienvenido a MiTienda</h1>
        <p class="text-gray-700">Ofertas del día, lo más vendido y más.</p>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 py-6 col-span-12 space-y-8">
      <ProductRow title="Ofertas del día" :productos="ofertas" to="/productos?ofertas=1" />
      <ProductRow title="Novedades" :productos="nuevos" to="/productos?orden=-id" />

      <!-- Grid denso al estilo “Más para ti” -->
      <section class="mt-8">
        <h2 class="text-xl font-semibold mb-2 px-2">Recomendado</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <ProductCard v-for="p in destacados" :key="p.id" :producto="p" />
        </div>
      </section>
    </div>
  </main>
</template>
