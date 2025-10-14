<template>
  <div class="space-y-6">
    <div class="text-center space-y-2">
      <h1 class="text-2xl font-semibold text-gray-900">¿Cómo deseas continuar?</h1>
      <p class="text-gray-600">Elige una opción para finalizar tu compra.</p>
    </div>
    <div class="grid gap-6 md:grid-cols-3">
      <section class="p-4 border rounded-lg shadow-sm bg-white flex flex-col gap-3">
        <h2 class="text-lg font-semibold text-gray-900">Iniciar sesión</h2>
        <p class="text-sm text-gray-600">Accede con tu cuenta para recuperar tu carrito y direcciones guardadas.</p>
        <form class="flex flex-col gap-3" @submit.prevent="onLogin">
          <input
            v-model="loginUsername"
            type="text"
            autocomplete="username"
            required
            placeholder="Usuario"
            class="border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            v-model="loginPassword"
            type="password"
            autocomplete="current-password"
            required
            placeholder="Contraseña"
            class="border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            :disabled="loginLoading"
            class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded disabled:opacity-60"
          >
            {{ loginLoading ? 'Accediendo…' : 'Entrar' }}
          </button>
          <p v-if="loginError" class="text-sm text-red-600">{{ loginError }}</p>
        </form>
      </section>

      <section class="p-4 border rounded-lg shadow-sm bg-white flex flex-col gap-3">
        <h2 class="text-lg font-semibold text-gray-900">Registrarme</h2>
        <p class="text-sm text-gray-600">Crea una cuenta para guardar tu historial de compras.</p>
        <form class="flex flex-col gap-3" @submit.prevent="onRegister">
          <input
            v-model="registerUsername"
            type="text"
            required
            placeholder="Usuario"
            class="border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
          <input
            v-model="registerEmail"
            type="email"
            placeholder="Correo (opcional)"
            class="border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
          <input
            v-model="registerPassword"
            type="password"
            required
            placeholder="Contraseña"
            class="border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
          <button
            type="submit"
            :disabled="registerLoading"
            class="bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 rounded disabled:opacity-60"
          >
            {{ registerLoading ? 'Registrando…' : 'Crear cuenta' }}
          </button>
          <p v-if="registerError" class="text-sm text-red-600">{{ registerError }}</p>
          <p v-if="registerMessage" class="text-sm text-emerald-600">{{ registerMessage }}</p>
        </form>
      </section>

      <section class="p-4 border rounded-lg shadow-sm bg-white flex flex-col gap-3">
        <h2 class="text-lg font-semibold text-gray-900">Continuar como invitado</h2>
        <p class="text-sm text-gray-600">
          Realiza tu compra ingresando tus datos solo para este pedido. Tus artículos se mantendrán reservados.
        </p>
        <button
          type="button"
          class="bg-gray-900 hover:bg-gray-800 text-white font-medium py-2 rounded"
          @click="emit('guest')"
        >
          Seguir como invitado
        </button>
        <p class="text-xs text-gray-500">
          Podrás crear una cuenta más adelante para guardar tu información.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

import api from '@/axios'
import { useAuthStore } from '@/stores/auth'
import { useCarritoStore } from '@/stores/carrito'

const emit = defineEmits(['guest', 'logged-in'])

const auth = useAuthStore()
const carrito = useCarritoStore()

const loginUsername = ref('')
const loginPassword = ref('')
const loginLoading = ref(false)
const loginError = ref('')

const registerUsername = ref('')
const registerEmail = ref('')
const registerPassword = ref('')
const registerLoading = ref(false)
const registerError = ref('')
const registerMessage = ref('')

const onLogin = async () => {
  if (loginLoading.value) return
  loginLoading.value = true
  loginError.value = ''
  try {
    await auth.login({ username: loginUsername.value, password: loginPassword.value })
    await carrito.cargar()
    emit('logged-in')
  } catch (err) {
    if (err.response?.status === 401) {
      loginError.value = 'Credenciales inválidas'
    } else {
      loginError.value = 'No se pudo iniciar sesión'
    }
  } finally {
    loginLoading.value = false
  }
}

const onRegister = async () => {
  if (registerLoading.value) return
  registerLoading.value = true
  registerError.value = ''
  registerMessage.value = ''
  try {
    const { data } = await api.post('register/', {
      username: registerUsername.value,
      email: registerEmail.value,
      password: registerPassword.value,
    })
    registerMessage.value = data?.mensaje || 'Cuenta creada, ahora puedes iniciar sesión.'
    registerUsername.value = ''
    registerEmail.value = ''
    registerPassword.value = ''
  } catch (err) {
    registerError.value = err.response?.data?.detail || 'No se pudo registrar la cuenta'
  } finally {
    registerLoading.value = false
  }
}
</script>
