<script setup>
import ProductCard from './ProductCard.vue'
defineProps({
  title: String,
  productos: { type: Array, default: () => [] },
  to: { type: String, default: '/productos' }
})
</script>

<template>
  <section class="mb-8">
    <div class="flex items-baseline justify-between mb-2 px-2">
      <h2 class="text-xl font-semibold">{{ title }}</h2>
      <RouterLink :to="to" class="text-sm text-blue-700 hover:underline">Ver más</RouterLink>
    </div>
    <div class="overflow-x-auto scrollbar-thin">
      <div class="flex gap-4 pr-4 pl-2 snap-x snap-mandatory">
        <div v-for="p in productos" :key="p.id" class="w-56 shrink-0 snap-start">
          <ProductCard :producto="p" />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* scrollbars discretos */
.scrollbar-thin::-webkit-scrollbar{height:8px}
.scrollbar-thin::-webkit-scrollbar-thumb{background:#d1d5db;border-radius:9999px}
</style>
