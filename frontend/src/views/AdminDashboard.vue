<template>
  <div>
    <h1>Panel de administración</h1>
    <ul>
      <li><router-link to="/admin/productos">Gestión de productos</router-link></li>
      <li><router-link to="/admin/pedidos">Gestión de pedidos</router-link></li>
      <li><router-link to="/admin/usuarios">Gestión de usuarios</router-link></li>
      <li v-if="auth.hasRole('super_admin')"><router-link to="/admin/configuracion">Configuración</router-link></li>
    </ul>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
defineOptions({ name: 'AdminDashboard' })
</script>
