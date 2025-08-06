<template>
  <div>
    <h2>Configuración</h2>
    <ul>
      <li><router-link to="/admin/configuracion/metodos-pago">Métodos de pago</router-link></li>
      <li><router-link to="/admin/configuracion/metodos-envio">Métodos de envío</router-link></li>
    </ul>
    <router-view />
  </div>
</template>

<script setup>
defineOptions({ name: 'AdminConfiguracion' })
</script>
