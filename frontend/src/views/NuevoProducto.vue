<template>
  <div class="max-w-md mx-auto p-6 bg-white rounded-lg shadow">
    <h2 class="text-xl font-bold mb-4">Crear nuevo producto</h2>

    <form @submit.prevent="crearProducto" class="space-y-4">
      <!-- Nombre -->
      <div>
        <label class="block text-sm font-medium mb-1">Nombre *</label>
        <input
          v-model.trim="producto.nombre"
          class="w-full p-2 border rounded"
          :class="{'border-red-500': errores.nombre}"
          autocomplete="off"
          required
        />
        <p v-if="errores.nombre" class="text-xs text-red-600">{{ errores.nombre }}</p>
      </div>

      <!-- Descripción -->
      <div>
        <label class="block text-sm font-medium mb-1">Descripción</label>
        <textarea
          v-model.trim="producto.descripcion"
          class="w-full p-2 border rounded resize-none"
          rows="3"
        />
      </div>

      <!-- Precio -->
      <div>
        <label class="block text-sm font-medium mb-1">Precio (MXN) *</label>
        <input
          v-model.number="producto.precio"
          type="number"
          step="0.01"
          min="0"
          class="w-full p-2 border rounded"
          :class="{'border-red-500': errores.precio}"
          required
        />
        <p v-if="errores.precio" class="text-xs text-red-600">{{ errores.precio }}</p>
      </div>

      <!-- Disponible -->
      <div class="flex items-center space-x-2">
        <input v-model="producto.disponible" type="checkbox" id="disp" />
        <label for="disp">Disponible</label>
      </div>

      <!-- Imagen -->
      <div>
        <label class="block text-sm font-medium mb-1">Imagen (máx 10 MB)</label>
        <input type="file" accept="image/*" @change="manejarImagen" />
        <p v-if="errores.imagen" class="text-xs text-red-600">{{ errores.imagen }}</p>

        <!-- Vista previa -->
        <div v-if="previewUrl" class="mt-2">
          <img :src="previewUrl" alt="Preview" class="imagePrevi w-40 h-40 object-cover rounded border" />
        </div>
      </div>

      <!-- Botón -->
      <button
        type="submit"
        class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded disabled:opacity-50"
        :disabled="subiendo"
      >
        {{ subiendo ? 'Subiendo…' : 'Guardar' }}
      </button>
    </form>

    <!-- Mensaje -->
    <p v-if="mensaje" class="mt-4 text-green-600">{{ mensaje }}</p>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

// Estado del formulario
const producto = reactive({
  nombre: '',
  descripcion: '',
  precio: 0,
  disponible: true
})
const imagenFile = ref(null)
const previewUrl = ref(null)

// Manejo de errores y estado
const errores = reactive({})
const mensaje = ref('')
const subiendo = ref(false)
// ────────── VALIDACIONES ──────────

// ────────── MANEJADORES ──────────
const manejarImagen = (e) => {
  const file = e.target.files[0]
  errores.imagen = ''

  if (!file) {
    imagenFile.value = null
    previewUrl.value = null
    return
  }
  const extension = file.name.split('.').pop().toLowerCase()
  if (!['jpg', 'jpeg', 'png', 'webp'].includes(extension)) {
    errores.imagen = 'Extensión de archivo no permitida.'
    imagenFile.value = null
    previewUrl.value = null
    return
  }
  
  const extensionesPermitidas = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  
  if (!extensionesPermitidas.includes(file.type)) {
    errores.imagen = 'Formato no permitido. Usa JPG, PNG o WEBP.'
    imagenFile.value = null
    previewUrl.value = null
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    errores.imagen = 'La imagen supera los 10 MB.'
    imagenFile.value = null
    previewUrl.value = null
    return
  }

  imagenFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

const validar = () => {
  errores.nombre = producto.nombre ? '' : 'El nombre es obligatorio.'
  errores.precio = producto.precio > 0 ? '' : 'El precio debe ser mayor a 0.'
  // imagen opcional: ya se validó tamaño arriba
  return !errores.nombre && !errores.precio && !errores.imagen
}

const limpiarFormulario = () => {
  producto.nombre = ''
  producto.descripcion = ''
  producto.precio = 0
  producto.disponible = true
  imagenFile.value = null
  previewUrl.value = null
}

const crearProducto = async () => {
  mensaje.value = ''

  // 1. Verifica sesión
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }

  // 2. Valida campos
  if (!validar()) return

  // 3. Construye FormData
  const formData = new FormData()
  formData.append('nombre', producto.nombre)
  formData.append('descripcion', producto.descripcion)
  formData.append('precio', Number(producto.precio)) // 👈 Esto en lugar de producto.precio directo
  formData.append('disponible', producto.disponible)
  if (imagenFile.value) formData.append('imagen', imagenFile.value)

  // 4. POST
  try {
    subiendo.value = true
    await api.post('productos/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    mensaje.value = 'Producto creado con éxito'
    limpiarFormulario()
    // Opcional: actualizar lista o redirigir
    router.push('/productos')
  } catch (err) {
    console.error(err)
    mensaje.value = 'Hubo un error al guardar'
  } finally {
    subiendo.value = false
  }
}
</script>
<style scoped>
h2 {
  color: #333;
}
input, textarea {
  transition: border-color 0.2s;
}
input:focus, textarea:focus {
  border-color: #3b82f6; /* Azul claro */
  outline: none;
}
.border-red-500 {
  border-color: #f87171; /* Rojo claro */
}
.border {
  border: 1px solid #e5e7eb; /* Gris claro */
}
.imagePrevi {
  max-width: 290px;
  height: auto;
}
</style>
<!-- This is a simple form to create a new product. It uses Vue's reactivity system to bind the form inputs to a `producto` object. When the form is submitted, it sends a POST request to the API to create the product. If successful, it displays a success message and resets the form. If there's an error, it logs the error and displays an error message. The form includes fields for name, description, price, and availability. -->