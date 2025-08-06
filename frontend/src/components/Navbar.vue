<template>
  <nav class="bg-gray-800 text-white px-6 py-3 flex justify-between items-center shadow w-full fixed top-0 left-0 z-50">
    <div class="flex items-center space-x-4">
      <RouterLink to="/" class="text-xl font-bold text-cyan-400 hover:text-white">🛒 MiTienda </RouterLink>
      <RouterLink to="/productos" class="hover:text-cyan-300">-Productos </RouterLink>
      <RouterLink v-if="auth.isAuthenticated" to="/carrito" class="relative hover:text-cyan-300">
        <span class="text-2xl">-Carrito  🛒</span>
        <span
          v-if="carrito.totalCantidad"
          class="absolute -top-1 -right-2 bg-fuchsia-600 text-white rounded-full text-xs px-1"
        >{{ carrito.totalCantidad }} </span>
      </RouterLink>
      <RouterLink v-if="auth.isAuthenticated" to="/mi-cuenta" class="hover:text-cyan-300">- Mi cuenta </RouterLink>
      <RouterLink v-if="auth.isAuthenticated" to="/nuevo-producto" class="hover:text-cyan-300">-Nuevo Producto </RouterLink>
    </div>

    <div class="flex items-center space-x-4">
      <p v-if="auth.user" class="text-sm text-gray-300">
  👤 {{ auth.user.nombre || auth.user.email }}
      </p>
      <RouterLink v-if="!auth.isAuthenticated" to="/login" class="hover:text-cyan-300">-Login </RouterLink>
      <RouterLink v-if="!auth.isAuthenticated" to="/registro" class="hover:text-cyan-300">-Registro </RouterLink>
      
      <button
        v-if="auth.isAuthenticated"
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
import { onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useCarritoStore } from '../stores/carrito'
defineOptions({ name: 'AppNavbar' })

const auth = useAuthStore()
const carrito = useCarritoStore()
const router = useRouter()

onMounted(() => {
  if (auth.isAuthenticated) carrito.cargar()
})
watch(
  () => auth.isAuthenticated,
  (val) => {
    if (val) carrito.cargar()
    else {
      carrito.items = []
      carrito.reservaExpira = null
    }
  }
)

const logout = () => {
  auth.logout()
  router.push('/login')
}
</script>

