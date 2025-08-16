<template>
  <div class="max-w-sm mx-auto px-4 py-10">
    <h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">Iniciar sesión</h2>
    <form @submit.prevent="login" class="space-y-4">
      <input
        v-model="username"
        placeholder="Usuario"
        required
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
        Entrar
      </button>
    </form>
    <p v-if="error" class="mt-4 text-center text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../axios'
import { useAuthStore } from '../stores/auth'
defineOptions({ name: 'LoginView' })

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()
const auth = useAuthStore()

const login = async () => {
  try {
    const res = await api.post('auth/login/', {
      username: username.value,
      password: password.value
    })
    auth.login(res.data.token, res.data.user)
    error.value = ''
    router.push('/admin')
  } catch (err) {
    console.error(err)
    error.value = 'Credenciales inválidas'
  }
}
</script>

