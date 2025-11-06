<template>
  <ul>
    <li v-for="categoria in categorias" :key="categoria.id">
      <input type="checkbox" :id="`categoria-${categoria.id}`" :value="categoria.id" v-model="selectedCategorias" class="mr-2">
      <label :for="`categoria-${categoria.id}`">{{ categoria.nombre }}</label>
      <CategoryTree v-if="categoria.children" :categorias="categoria.children" v-model:selectedCategorias="selectedCategorias" />
    </li>
  </ul>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue';
import CategoryTree from './CategoryTree.vue';

const props = defineProps({
  categorias: {
    type: Array,
    required: true,
  },
  selectedCategorias: {
    type: Array,
    required: true,
  },
});

const emits = defineEmits(['update:selectedCategorias']);

const selectedCategorias = computed({
  get: () => props.selectedCategorias,
  set: (value) => emits('update:selectedCategorias', value),
});
</script>
