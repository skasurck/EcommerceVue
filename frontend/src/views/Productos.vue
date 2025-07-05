<template>
  <div>
    <h1>Productossss</h1>
    <ul>
      <li v-for="producto in productos" :key="producto.id">
        {{ producto.nombre }} - ${{ producto.precio }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../axios'

const productos = ref([])

onMounted(async () => {
  try {
    const res = await api.get('productos/')
    productos.value = res.data
  } catch (error) {
    console.error('Error cargando productos:', error)
  }
})
</script>
<style scoped>
h1 {
  color: #333;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  padding: 8px;
  border-bottom: 1px solid #ccc;
}
li:last-child {
  border-bottom: none;
}
</style>