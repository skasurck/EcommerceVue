<template>
  <div class="formulario">
    <h2>Crear nuevo producto</h2>
    <form @submit.prevent="crearProducto">
      <div>
        <label>Nombre:</label>
        <input v-model="producto.nombre" required />
      </div>
      <div>
        <label>Descripción:</label>
        <textarea v-model="producto.descripcion" />
      </div>
      <div>
        <label>Precio:</label>
        <input v-model.number="producto.precio" type="number" step="0.01" required />
      </div>
      <div>
        <label>Disponible:</label>
        <input v-model="producto.disponible" type="checkbox" />
      </div>
      
      <button type="submit">Guardar</button>
    </form>

    <p v-if="mensaje" style="color: green">{{ mensaje }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../axios'

const producto = ref({
  nombre: '',
  descripcion: '',
  precio: 0,
  disponible: true
})

const mensaje = ref('')

const crearProducto = async () => {
// Verificar si el usuario ha iniciado sesión
  if (!localStorage.getItem('access')) {
  alert('Debes iniciar sesión')
  return
}
  // Validar campos requeridos
  if (!producto.value.nombre || producto.value.precio <= 0) {
    mensaje.value = 'Por favor, completa todos los campos requeridos.'
    return
  }
// Enviar solicitud POST para crear el producto
  try {
    await api.post('productos/', producto.value)
    mensaje.value = 'Producto creado con éxito'
    // Limpia el formulario
    producto.value = {
      nombre: '',
      descripcion: '',
      precio: 0,
      disponible: true
    }
  } catch (error) {
    console.error('Error al crear producto:', error)
    mensaje.value = 'Hubo un error'
  }
}
</script>
<style scoped>
.formulario {
  max-width: 400px;
  margin: auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.formulario h2 {
  text-align: center;
}
.formulario div {
  margin-bottom: 15px;
}
.formulario label {
  display: block;
  margin-bottom: 5px;
}
.formulario input,
.formulario textarea {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
.formulario button {
  width: 100%;
  padding: 10px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.formulario button:hover {
  background-color: #218838;
}
.formulario p {
  text-align: center;
  margin-top: 10px;
}
.formulario p.error {
  color: red;
}
.formulario p.success {
  color: green;
}
</style>
<!-- This is a simple form to create a new product. It uses Vue's reactivity system to bind the form inputs to a `producto` object. When the form is submitted, it sends a POST request to the API to create the product. If successful, it displays a success message and resets the form. If there's an error, it logs the error and displays an error message. The form includes fields for name, description, price, and availability. -->