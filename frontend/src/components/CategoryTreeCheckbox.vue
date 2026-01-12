<template>
  <div class="category-tree-container">
    <div 
      v-for="category in nodes" 
      :key="category.id" 
      class="category-node"
    >
      <div 
        class="category-item" 
        :style="{ 'padding-left': `${depth * 25}px` }"
      >
        <input
          type="checkbox"
          :id="`cat-${category.id}`"
          :checked="categoryStore.selectedCategoryIds.includes(category.id)"
          @change="categoryStore.toggleCategory(category.id)"
        />
        <label :for="`cat-${category.id}`">{{ category.nombre }}</label>
      </div>

      <!-- ========= LLAMADA RECURSIVA ========= -->
      <!-- Si la categoría actual tiene subcategorías, el componente se llama a sí mismo -->
      <!-- para renderizarlas, aumentando el nivel de profundidad (indentación). -->
      <CategoryTreeCheckbox
        v-if="category.subcategorias && category.subcategorias.length > 0"
        :nodes="category.subcategorias"
        :depth="depth + 1"
      />
    </div>
  </div>
</template>

<script setup>
import { useCategoryStore } from '@/stores/categories';

// Se le da un nombre al componente para que la recursividad funcione correctamente
defineOptions({
  name: 'CategoryTreeCheckbox'
});

// Props que el componente acepta desde fuera
defineProps({
  // La lista de categorías (o subcategorías) a renderizar en este nivel
  nodes: {
    type: Array,
    required: true,
  },
  // El nivel de profundidad para calcular la indentación
  depth: {
    type: Number,
    default: 0,
  },
});

// Instancia del store de Pinia para manejar el estado
const categoryStore = useCategoryStore();
</script>

<style scoped>
.category-node {
  margin-bottom: 2px;
}
.category-item {
  display: flex;
  align-items: center;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}
.category-item:hover {
  background-color: #f0f0f0;
}
.category-item label {
  margin-left: 8px;
  cursor: pointer;
  user-select: none;
}
.category-item input {
  cursor: pointer;
}
</style>
