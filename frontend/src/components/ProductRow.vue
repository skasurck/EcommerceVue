<script setup>
import ProductCard from './ProductCard.vue'
defineProps({
  title: String,
  productos: { type: Array, default: () => [] },
  to: { type: String, default: '/productos' }
})
defineEmits(['add-to-cart'])
</script>

<template>
  <section class="mb-8">
    <div class="flex items-center justify-between mb-3 px-2">
      <h2 class="text-xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
        <span class="block w-1 h-5 rounded-full bg-cyan-500 shrink-0"></span>
        {{ title }}
      </h2>
      <RouterLink
        :to="to"
        class="flex items-center gap-1 text-sm font-medium text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 dark:hover:text-cyan-300 transition-colors"
      >
        Ver más
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
      </RouterLink>
    </div>
    <div class="overflow-x-auto scrollbar-thin">
      <div class="flex gap-4 pr-4 pl-2 snap-x snap-mandatory">
        <div v-for="p in productos" :key="p.id" class="w-56 shrink-0 snap-start">
          <ProductCard :producto="p" @add-to-cart="$emit('add-to-cart', $event)" />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.scrollbar-thin::-webkit-scrollbar {
  height: 6px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 9999px;
}
:global(.dark) .scrollbar-thin::-webkit-scrollbar-thumb {
  background: #475569;
}
</style>
