<template>
  <div>
    <div class="flex items-center">
      <input
        type="checkbox"
        :id="`cat-${category.id}`"
        :checked="isSelected"
        @change="toggleSelection"
        class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
      />
      <label :for="`cat-${category.id}`" class="ml-2 text-sm text-gray-800">{{ category.nombre }}</label>
    </div>
    <div v-if="category.subcategorias && category.subcategorias.length > 0" class="pl-6 mt-1 space-y-1">
      <CategoryNode
        v-for="subCategory in category.subcategorias"
        :key="subCategory.id"
        :category="subCategory"
        :selected-categories="selectedCategories"
        @update:selected-categories="emitUpdate"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import CategoryNode from '@/components/CategoryNode.vue'; // Recursive import

const props = defineProps({
  category: {
    type: Object,
    required: true,
  },
  selectedCategories: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(['update:selected-categories']);

const isSelected = computed(() => {
  return props.selectedCategories.includes(props.category.id);
});

const toggleSelection = () => {
  const newSelection = [...props.selectedCategories];
  const index = newSelection.indexOf(props.category.id);

  if (index === -1) {
    newSelection.push(props.category.id);
  } else {
    newSelection.splice(index, 1);
  }
  emit('update:selected-categories', newSelection);
};

// Pass the event up from child nodes
const emitUpdate = (newSelection) => {
  emit('update:selected-categories', newSelection);
};
</script>
