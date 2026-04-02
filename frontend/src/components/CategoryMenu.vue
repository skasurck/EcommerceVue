<template>
  <div class="category-menu">
    <ul class="category-list">
      <li v-for="category in categories" :key="category.id" class="category-item">
        <div class="category-item-content">
          <RouterLink :to="{ name: 'categoria', params: { categoriaSlug: category.slug || category.id } }">{{ category.nombre }}</RouterLink>
          <button v-if="category.subcategorias.length > 0" @click="toggleCategory(category)" class="submenu-toggle">
            <span class="submenu-arrow" :class="{ 'open': category.open }"></span>
          </button>
        </div>
        <ul v-if="category.open && category.subcategorias.length > 0" class="submenu">
          <li v-for="subcategory in category.subcategorias" :key="subcategory.id">
            <RouterLink :to="{ name: 'categoria', params: { categoriaSlug: subcategory.slug || subcategory.id } }">{{ subcategory.nombre }}</RouterLink>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script>
import { getCategoriasTree } from '@/api/productos.js';

export default {
  name: 'CategoryMenu',
  data() {
    return {
      categories: [],
    };
  },
  async created() {
    try {
      const response = await getCategoriasTree();
      this.categories = response.data.map(category => ({ ...category, open: false }));
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  },
  methods: {
    toggleCategory(category) {
      category.open = !category.open;
    }
  }
};
</script>

<style scoped>
.category-menu {
  width: 100%;
  font-family: sans-serif;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  text-decoration: none;
  color: #333;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
}

.category-item-content:hover {
  background-color: #f5f5f5;
}

.category-item-content a {
  text-decoration: none;
  color: #333;
  flex-grow: 1;
}

.submenu {
  list-style: none;
  padding-left: 20px;
  background-color: #fafafa;
}

.submenu li a {
  padding: 10px 15px;
  font-size: 0.9em;
  border-bottom: none;
  display: block;
  text-decoration: none;
  color: #333;
}

.submenu li a:hover {
  background-color: #f0f0f0;
}

.submenu-toggle {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
}

.submenu-arrow {
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 5px solid #333;
  transition: transform 0.3s;
}

.submenu-arrow.open {
  transform: rotate(180deg);
}
</style>
