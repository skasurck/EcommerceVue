// frontend/src/stores/categories.js
import { defineStore } from 'pinia';
import axios from '@/axios'; // Asume que tienes una instancia de axios configurada

export const useCategoryStore = defineStore('categories', {
  state: () => ({
    categoryTree: [],
    selectedCategoryIds: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchCategoryTree() {
      if (this.categoryTree.length > 0) {
        // No volver a cargar si ya las tenemos
        return;
      }
      this.loading = true;
      this.error = null;
      try {
        // Apuntamos a la vista que ya existía: AllCategoriesAPIView
        const response = await axios.get('/productos/api/all-categories/');
        this.categoryTree = response.data;
      } catch (error) {
        this.error = 'Error al cargar las categorías.';
        console.error('Error fetching category tree:', error);
      } finally {
        this.loading = false;
      }
    },
    
    // Inicializa las categorías seleccionadas al editar un producto existente
    setSelectedCategories(categoryIds) {
      if (Array.isArray(categoryIds)) {
        this.selectedCategoryIds = [...categoryIds];
      } else {
        this.selectedCategoryIds = [];
      }
    },

    // Lógica para marcar/desmarcar una categoría individualmente
    toggleCategory(categoryId) {
      const index = this.selectedCategoryIds.indexOf(categoryId);
      if (index > -1) {
        // Si ya está seleccionada, la quitamos
        this.selectedCategoryIds.splice(index, 1);
      } else {
        // Si no está, la añadimos
        this.selectedCategoryIds.push(categoryId);
      }
    },
    
    // Limpia la selección, útil al abrir el formulario para un nuevo producto
    clearSelection() {
      this.selectedCategoryIds = [];
    }
  },
});
