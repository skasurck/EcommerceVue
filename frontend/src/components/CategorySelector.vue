<template>
  <div>
    <InputLabel :label="label" />
    <div class="mt-2 p-4 border rounded-md max-h-64 overflow-y-auto bg-white">
      <div v-for="category in categoryTree" :key="category.id">
        <CategoryNode :category="category" :selected-categories="modelValue" @update:selected-categories="emitUpdate" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getCategorias } from '@/api/productos.js';
import InputLabel from '@/inputs/InputLabel.vue';
import CategoryNode from '@/components/CategoryNode.vue'; // We will create this component

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  label: {
    type: String,
    default: 'Categorías',
  },
});

const emit = defineEmits(['update:modelValue']);

const allCategories = ref([]);
const categoryTree = computed(() => buildTree(allCategories.value));

function buildTree(nodes, parentId = null) {
  return nodes
    .filter((node) => node.parent === parentId)
    .map((node) => ({
      ...node,
      subcategorias: buildTree(nodes, node.id),
    }));
}

onMounted(async () => {
  try {
    const response = await getCategorias();
    allCategories.value = response.data;
  } catch (error) {
    console.error('Error al cargar las categorías:', error);
  }
});

function emitUpdate(newSelection) {
  emit('update:modelValue', newSelection);
}
</script>
