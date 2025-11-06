<template>
  <div class="container mx-auto p-4">
    <div class="flex flex-col md:flex-row">
      <!-- Filter Sidebar -->
      <aside class="w-full md:w-1/4 p-4">
        <h2 class="text-2xl font-bold mb-4">Filtros</h2>
        <!-- Search -->
        <div class="mb-4">
          <input type="text" v-model="searchQuery" placeholder="Buscar por nombre o SKU" class="w-full p-2 border rounded">
        </div>
        <!-- Price Range -->
        <div class="mb-4">
          <h3 class="font-bold mb-2">Rango de Precios</h3>
          <PriceSlider
            v-if="priceRange.min !== null && priceRange.max !== null"
            :min="priceRange.min"
            :max="priceRange.max"
            v-model="priceFilter"
          />
          <div class="flex justify-between mt-2">
            <span>{{ filters.precioMin }}</span>
            <span>{{ filters.precioMax }}</span>
          </div>
        </div>
        <!-- Brands -->
        <div class="mb-4">
          <h3 class="font-bold mb-2">Marcas</h3>
          <ul>
            <li v-for="marca in marcas" :key="marca.id">
              <input type="checkbox" :id="`marca-${marca.id}`" :value="marca.id" v-model="filters.marcas" class="mr-2">
              <label :for="`marca-${marca.id}`">{{ marca.nombre }}</label>
            </li>
          </ul>
        </div>
        <!-- Categories -->
        <div class="mb-4">
          <h3 class="font-bold mb-2">Categorías</h3>
          <CategoryTree :categorias="categoryTree" v-model:selectedCategorias="filters.categorias" />
        </div>
        <!-- Attributes -->
        <div class="mb-4">
          <h3 class="font-bold mb-2">Atributos</h3>
          <div v-for="atributo in atributos" :key="atributo.id">
            <h4 class="font-semibold">{{ atributo.nombre }}</h4>
            <ul>
              <li v-for="valor in valorAtributos.filter(v => v.atributo === atributo.id)" :key="valor.id">
                <input type="checkbox" :id="`valor-${valor.id}`" :value="valor.id" v-model="filters.atributos" class="mr-2">
                <label :for="`valor-${valor.id}`">{{ valor.valor }}</label>
              </li>
            </ul>
          </div>
        </div>
        <!-- Availability -->
        <div class="mb-4">
          <h3 class="font-bold mb-2">Disponibilidad</h3>
          <div class="flex items-center">
            <input type="checkbox" id="in-stock" v-model="filters.enStock" class="mr-2">
            <label for="in-stock">En Stock</label>
          </div>
        </div>
      </aside>

      <!-- Product List -->
      <main class="w-full md:w-3/4 p-4">
        <h1 class="text-3xl font-bold mb-4">Resultados de Búsqueda</h1>
        <div v-if="loading">Cargando...</div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <ProductCard v-for="producto in productos" :key="producto.id" :producto="producto" />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, computed } from 'vue';
import { getCategorias, getMarcas, getProductos, getAtributos, getValorAtributos, getPriceRange } from '../api/productos';
import { buildTree } from '../utils/tree';
import CategoryTree from '../components/CategoryTree.vue';
import PriceSlider from '../components/PriceSlider.vue';

const categorias = ref([]);
const marcas = ref([]);
const productos = ref([]);
const atributos = ref([]);
const valorAtributos = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const priceRange = ref({ min: null, max: null });

const categoryTree = computed(() => buildTree(categorias.value));

const filters = ref({
  marcas: [],
  categorias: [],
  enStock: false,
  precioMin: null,
  precioMax: null,
  atributos: [],
});

const priceFilter = computed({
  get: () => [filters.value.precioMin, filters.value.precioMax],
  set: (value) => {
    filters.value.precioMin = value[0];
    filters.value.precioMax = value[1];
  },
});

const fetchProductos = async () => {
  loading.value = true;
  try {
    const params = {
      search: searchQuery.value,
      marca: filters.value.marcas.join(','),
      categoria: filters.value.categorias.join(','),
      estado_inventario: filters.value.enStock ? 'en_stock' : '',
      precio_min: filters.value.precioMin,
      precio_max: filters.value.precioMax,
      atributos: filters.value.atributos.join(','),
    }
    const response = await getProductos(params);
    productos.value = response.data.results;
  } catch (error) {
    console.error('Error fetching products:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  try {
    const [catRes, marRes, atrRes, valAtrRes, priceRangeRes] = await Promise.all([
      getCategorias(),
      getMarcas(),
      getAtributos(),
      getValorAtributos(),
      getPriceRange(),
    ]);
    categorias.value = catRes.data;
    marcas.value = marRes.data;
    atributos.value = atrRes.data;
    valorAtributos.value = valAtrRes.data;
    priceRange.value = { min: priceRangeRes.data.min_precio, max: priceRangeRes.data.max_precio };
    filters.value.precioMin = priceRange.value.min;
    filters.value.precioMax = priceRange.value.max;
    fetchProductos();
  } catch (error) {
    console.error('Error fetching filters:', error);
  }
});

watch([searchQuery, filters], fetchProductos, { deep: true });
</script>
