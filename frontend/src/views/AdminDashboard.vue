<template>
  <div class="max-w-3xl mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-4">Panel de administración</h1>
    <ul class="space-y-2">
      <li>
        <router-link to="/admin/productos" class="flex items-center gap-2 text-blue-600 hover:underline">
          <span aria-hidden="true">🛍️</span>
          <span>Gestión de productos</span>
        </router-link>
      </li>
      <li>
        <router-link to="/admin/pedidos" class="flex items-center gap-2 text-blue-600 hover:underline">
          <span aria-hidden="true">🧾</span>
          <span>Gestión de pedidos</span>
        </router-link>
      </li>
      <li>
        <router-link to="/admin/usuarios" class="flex items-center gap-2 text-blue-600 hover:underline">
          <span aria-hidden="true">👤</span>
          <span>Gestión de usuarios</span>
        </router-link>
      </li>
      <li>
        <router-link to="/admin/ai/clasificar-productos" class="flex items-center gap-2 text-blue-600 hover:underline">
          <span aria-hidden="true">🤖</span>
          <span>Clasificar productos con IA</span>
        </router-link>
      </li>
      <li>
        <router-link to="/admin/ai/revisar-clasificaciones" class="flex items-center gap-2 text-blue-600 hover:underline">
          <span aria-hidden="true">✅</span>
          <span>Revisar clasificaciones de IA</span>
        </router-link>
      </li>
      <li>
        <router-link to="/admin/suppliers/supermex" class="flex items-center gap-2 text-blue-600 hover:underline">
          <span aria-hidden="true">🚚</span>
          <span>Importar catálogo de Supermex</span>
        </router-link>
      </li>
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

