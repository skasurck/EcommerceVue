<template>
  <div class="max-w-sm mx-auto px-4 py-10">
    <h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">Iniciar sesión</h2>
    <form @submit.prevent="onSubmit" class="space-y-4">
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
      <button type="submit" :disabled="isSubmitting" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded disabled:opacity-50">
        {{ isSubmitting ? 'Entrando…' : 'Entrar' }}
      </button>
    </form>
    <p v-if="error" class="mt-4 text-center text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineOptions({ name: 'LoginView' })

const username = ref('')
const password = ref('')
const error = ref('')
const isSubmitting = ref(false)
const router = useRouter()
const auth = useAuthStore()

let inFlightController = null
let debounceTimer

const onSubmit = () => {
  if (import.meta.env.DEV) console.debug('submit login')
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    inFlightController?.abort()
    if (inFlightController && import.meta.env.DEV) console.debug('previous login aborted')
    inFlightController = new AbortController()
    isSubmitting.value = true
    try {
      await auth.login({ username: username.value, password: password.value }, inFlightController.signal)
      error.value = ''
      if (import.meta.env.DEV) console.debug('redirecting to /products')
      router.push('/products')
    } catch (err) {
      if (err.name === 'CanceledError') return
      if (err.response?.status === 401) {
        error.value = 'Credenciales inválidas'
      } else {
        console.error(err)
        error.value = 'Error al iniciar sesión'
      }
    } finally {
      isSubmitting.value = false
    }
  }, 300)
}
</script>

