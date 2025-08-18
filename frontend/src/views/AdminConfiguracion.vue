<template>
  <div class="max-w-3xl mx-auto px-4 py-6">
    <h2 class="text-2xl font-bold text-gray-900 mb-4">Configuración</h2>
    <ul class="space-y-2 mb-6">
      <li>
        <router-link to="/admin/configuracion/metodos-pago" class="text-blue-600 hover:underline">Métodos de pago</router-link>
      </li>
      <li>
        <router-link to="/admin/configuracion/metodos-envio" class="text-blue-600 hover:underline">Métodos de envío</router-link>
      </li>
    </ul>
    <router-view />
  </div>
</template>

<script setup>
defineOptions({ name: 'AdminConfiguracion' })
</script>

