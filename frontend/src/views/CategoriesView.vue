<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-4">Categorías</h1>
    <CategoryMenu />
  </div>
</template>

<script>
import CategoryMenu from '@/components/CategoryMenu.vue';

export default {
  name: 'CategoriesView',
  components: {
    CategoryMenu,
  },
};
</script>
