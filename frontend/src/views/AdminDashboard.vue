<template>
  <div class="max-w-3xl mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-4">Panel de administración</h1>
    <ul class="space-y-2">
      <li><router-link to="/admin/productos" class="text-blue-600 hover:underline">Gestión de productos</router-link></li>
      <li><router-link to="/admin/pedidos" class="text-blue-600 hover:underline">Gestión de pedidos</router-link></li>
      <li><router-link to="/admin/usuarios" class="text-blue-600 hover:underline">Gestión de usuarios</router-link></li>
      <li v-if="auth.hasRole('super_admin')">
        <router-link to="/admin/configuracion" class="text-blue-600 hover:underline">Configuración</router-link>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
defineOptions({ name: 'AdminDashboard' })
</script>

