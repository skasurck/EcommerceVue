<template>
  <div class="category-tree-item">
    <div v-for="category in categories" :key="category.id" class="ml-4">
      <div v-if="level === 0">
        <p class="font-semibold my-2">{{ category.nombre }}</p>
        <category-tree-item
          v-if="category.subcategorias && category.subcategorias.length > 0"
          :categories="category.subcategorias"
          :selected-categories="selectedCategories"
          :level="level + 1"
          @update:selected-categories="emitSelection"
        />
      </div>
      <div v-else>
        <label class="flex items-center space-x-2">
          <input
            type="checkbox"
            :checked="isSelected(category.id)"
            @change="toggleCategory(category.id)"
            class="form-checkbox h-5 w-5 text-blue-600"
          />
          <span>{{ category.nombre }}</span>
        </label>
        <category-tree-item
          v-if="category.subcategorias && category.subcategorias.length > 0"
          :categories="category.subcategorias"
          :selected-categories="selectedCategories"
          :level="level + 1"
          @update:selected-categories="emitSelection"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CategoryTreeItem',
  props: {
    categories: {
      type: Array,
      required: true,
    },
    selectedCategories: {
      type: Array,
      required: true,
    },
    level: {
      type: Number,
      default: 0,
    },
  },
  emits: ['update:selected-categories'],
  setup(props, { emit }) {
    const isSelected = (categoryId) => {
      return props.selectedCategories.includes(categoryId);
    };

    const toggleCategory = (categoryId) => {
      const newSelection = [...props.selectedCategories];
      const index = newSelection.indexOf(categoryId);
      if (index > -1) {
        newSelection.splice(index, 1);
      } else {
        newSelection.push(categoryId);
      }
      emit('update:selected-categories', newSelection);
    };

    const emitSelection = (newSelection) => {
      emit('update:selected-categories', newSelection);
    };

    return {
      isSelected,
      toggleCategory,
      emitSelection,
    };
  },
};
</script>
