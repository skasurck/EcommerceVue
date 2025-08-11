<!-- App.vue (o el layout principal) -->
<template>
  <Navbar />
   <main style="padding-top: var(--nav-h)">
  <RouterView v-slot="{ Component, route }">
    <!-- si usas KeepAlive, EXCLUYE AdminUsuarios -->
    <!-- <KeepAlive exclude="AdminUsuarios"> -->
      <component :is="Component" :key="route.fullPath" />
    <!-- </KeepAlive> -->
  </RouterView>
   </main>
</template>



<script setup>
import Navbar from './components/Navbar.vue'
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()

onMounted(() => {
  auth.checkLogin()
// Calcular altura del navbar y guardarla en una variable CSS global
  const h = document.getElementById('nav').offsetHeight + 'px'
  document.documentElement.style.setProperty('--nav-h', h)
})
</script>

<style scoped>
body {
  margin: 0;
  font-family: sans-serif;
  background-color: #000000 !important;
}
</style>
