<template>
  <div class="product-form-container">
    <h1>{{ isEditing ? 'Editar Producto' : 'Crear Producto' }}</h1>
    <form @submit.prevent="saveProduct" v-if="!formLoading">
      
      <div class="form-section">
        <label for="product-name">Nombre del Producto</label>
        <input id="product-name" v-model="product.nombre" type="text" required />
      </div>

      <div class="form-section">
        <label for="product-image">Imagen Principal</label>
        <input id="product-image" type="file" @change="handleFileChange" accept="image/*" />
        <div v-if="!isEditing && imagePreview" class="image-preview">
          <p>Vista previa:</p>
          <img :src="imagePreview" alt="Vista previa de la imagen" />
        </div>
      </div>

      <div class="form-section">
        <h3>Categorías</h3>
        <div v-if="categoryStore.loading" class="loading-text">Cargando categorías...</div>
        <div v-else-if="categoryStore.error" class="error-text">{{ categoryStore.error }}</div>
        <div v-else class="category-box">
          <CategoryTreeCheckbox
            :nodes="categoryStore.categoryTree"
            :depth="0"
          />
        </div>
      </div>

      <button type="submit" :disabled="isSaving" class="save-button">
        {{ isSaving ? 'Guardando...' : 'Guardar Producto' }}
      </button>
      <div v-if="saveError" class="error-text">{{ saveError }}</div>
    </form>
    <div v-else class="loading-text">Cargando datos del formulario...</div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCategoryStore } from '@/stores/categories';
import axios from '@/axios';
import CategoryTreeCheckbox from '@/components/CategoryTreeCheckbox.vue';

const product = ref({
  nombre: '',
  descripcion_corta: '',
  descripcion_larga: '',
  precio_normal: 0,
  precio_rebajado: null,
  sku: '',
  stock: 0,
  disponible: true,
  visibilidad: true,
  estado: 'borrador',
  marca: null,
});
const isSaving = ref(false);
const formLoading = ref(true);
const saveError = ref(null);
const selectedFile = ref(null);
const imagePreview = ref(null);

const route = useRoute();
const router = useRouter();
const categoryStore = useCategoryStore();

const productId = computed(() => route.params.id);
const isEditing = computed(() => !!productId.value);

onMounted(async () => {
  formLoading.value = true;
  await categoryStore.fetchCategoryTree();

  if (isEditing.value) {
    try {
      const response = await axios.get(`/productos/productos/${productId.value}/`);
      product.value = response.data;
      const existingCategoryIds = response.data.categorias.map(cat => cat.id);
      categoryStore.setSelectedCategories(existingCategoryIds);
    } catch (error) {
      console.error("Error cargando el producto:", error);
      saveError.value = "No se pudo cargar el producto.";
    }
  } else {
    categoryStore.clearSelection();
  }
  formLoading.value = false;
});

function handleFileChange(event) {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    // Crear una URL para la vista previa
    imagePreview.value = URL.createObjectURL(file);
  } else {
    selectedFile.value = null;
    imagePreview.value = null;
  }
}

async function saveProduct() {
  isSaving.value = true;
  saveError.value = null;

  let payload;
  const isMultipart = !!selectedFile.value;

  if (isMultipart) {
    payload = new FormData();
    // Añadir todos los campos del producto al FormData
    for (const key in product.value) {
      const value = product.value[key];
      if (key !== 'categorias' && value !== null && value !== undefined) {
          payload.append(key, value);
      }
    }
    // Añadir la imagen
    payload.append('imagen_principal', selectedFile.value);

    // Adjuntar los IDs de categoría como claves separadas
    categoryStore.selectedCategoryIds.forEach(id => {
      payload.append('categorias_ids', id);
    });
  } else {
    payload = {
      ...product.value,
      categorias_ids: categoryStore.selectedCategoryIds,
    };
  }
  
  const headers = isMultipart ? { 'Content-Type': 'multipart/form-data' } : {};

  try {
    let response;
    const url = isEditing.value 
      ? `/productos/productos/${productId.value}/` 
      : '/productos/productos/';
    const method = isEditing.value ? 'put' : 'post';

    response = await axios({ method, url, data: payload, headers });

    console.log('Producto guardado:', response.data);
    router.push({ name: 'ProductList' }); // O la ruta que corresponda
  } catch (error) {
    console.error('Error al guardar el producto:', error.response?.data || error.message);
    saveError.value = 'Hubo un error al guardar. Revisa los campos marcados o la consola para más detalles.';
  } finally {
    isSaving.value = false;
  }
}
</script>

<style scoped>
.product-form-container {
  max-width: 700px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.form-section {
  margin-bottom: 1.5rem;
}
label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
input[type="text"], input[type="file"] {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.image-preview {
  margin-top: 1rem;
}
.image-preview img {
  max-width: 200px;
  max-height: 200px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.category-box {
  border: 1px solid #ddd;
  padding: 1rem;
  border-radius: 4px;
  max-height: 350px;
  overflow-y: auto;
  background-color: #f9f9f9;
}
.save-button {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background-color 0.2s;
}
.save-button:hover {
  background-color: #0056b3;
}
.save-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.loading-text, .error-text {
  padding: 1rem;
  text-align: center;
}
.error-text {
  color: #d9534f;
  margin-top: 1rem;
}
</style>
