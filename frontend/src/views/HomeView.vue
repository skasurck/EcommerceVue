<template>
  <main>
    <h1 class="text-3xl font-bold text-center my-8">Bienvenido a MiTienda</h1>
    <p class="text-center text-gray-600">Aquí encontrarás los mejores productos a los mejores precios.</p>
    <div class="flex justify-center mt-8">
      <router-link to="/productos" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        Ver Productos
      </router-link>
      <router-link to="/nuevo-producto" class="ml-4 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600" >
        Agregar Nuevo Producto
      </router-link>
    </div>
    <div class="mt-8 text-center">
      <p class="text-gray-500">Para comenzar, inicia sesión o regístrate.</p>
      <div class="mt-4">
        <router-link to="/login" class="text-blue-500 hover:underline">Iniciar Sesión</router-link>
        <span class="mx-2">|</span>
        <router-link to="/registro" class="text-blue-500 hover:underline">Registrarse</router-link>
      </div>
    </div>
    <div class="mt-8 text-center">
      <p class="text-gray-500">¡Gracias por visitar MiTienda!</p>
    </div>
  </main>
</template>
<script setup>
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
</script>
