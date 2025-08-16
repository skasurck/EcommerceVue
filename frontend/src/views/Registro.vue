<template>
  <div class="max-w-sm mx-auto px-4 py-10">
    <h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">Registro de usuario</h2>
    <form @submit.prevent="registrar" class="space-y-4">
      <input
        v-model="username"
        placeholder="Usuario"
        required
        class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <input
        v-model="email"
        type="email"
        placeholder="Correo (opcional)"
        class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <input
        v-model="password"
        type="password"
        placeholder="Contraseña"
        required
        class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded">
        Registrar
      </button>
    </form>
    <p v-if="mensaje" class="mt-4 text-center text-green-600">{{ mensaje }}</p>
    <p v-if="error" class="mt-2 text-center text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../axios'
defineOptions({ name: 'RegisterView' })

const username = ref('')
const email = ref('')
const password = ref('')
const mensaje = ref('')
const error = ref('')

const registrar = async () => {
  try {
    const res = await api.post('register/', {
      username: username.value,
      email: email.value,
      password: password.value
    })
    mensaje.value = res.data.mensaje
    error.value = ''
    username.value = ''
    email.value = ''
    password.value = ''
  } catch (err) {
    console.error(err)
    mensaje.value = ''
    error.value = 'Error al registrar usuario'
  }
}
</script>

