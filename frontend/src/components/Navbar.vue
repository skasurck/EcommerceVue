<template>
  <nav class="bg-gray-800 text-white px-6 py-3 flex justify-between items-center shadow w-full fixed top-0 left-0 z-50">
    <div class="flex items-center space-x-4">
      <RouterLink to="/" class="text-xl font-bold text-cyan-400 hover:text-white">🛒 MiTienda</RouterLink>
      <RouterLink to="/productos" class="hover:text-cyan-300">Productos</RouterLink>
      <RouterLink v-if="auth.isLoggedIn" to="/carrito" class="hover:text-cyan-300">Carrito</RouterLink>
      <RouterLink v-if="auth.isLoggedIn" to="/nuevo-producto" class="hover:text-cyan-300">Nuevo Producto</RouterLink>
    </div>

    <div class="flex items-center space-x-4">
      <p v-if="auth.profile" class="text-sm text-gray-300">
  👤 {{ auth.profile.username || auth.profile.email }}
      </p>
      <RouterLink v-if="!auth.isLoggedIn" to="/login" class="hover:text-cyan-300">Login</RouterLink>
      <RouterLink v-if="!auth.isLoggedIn" to="/registro" class="hover:text-cyan-300">Registro</RouterLink>
      <button
        v-if="auth.isLoggedIn"
        @click="logout"
        class="bg-red-600 hover:bg-red-700 px-4 py-1 rounded text-sm font-medium"
      >
        Cerrar sesión
      </button>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
defineOptions({ name: 'AppNavbar' })

const auth = useAuthStore()
const router = useRouter()

const logout = () => {
  auth.logout()
  router.push('/login')
}
</script>
