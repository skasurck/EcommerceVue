<template>
  <div class="border p-4 rounded">
    <router-link :to="{ name: 'producto', params: { id: producto.id } }">
      <img :src="producto.imagen_principal" :alt="producto.nombre" class="w-full h-48 object-cover mb-4">
      <h2 class="font-bold">{{ producto.nombre }}</h2>
      <p>{{ producto.precio }}</p>
    </router-link>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

defineProps({
  producto: {
    type: Object,
    required: true,
  },
});
</script>