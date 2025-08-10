<!-- App.vue (o el layout principal) -->
<template>
  <Navbar />
  <RouterView v-slot="{ Component, route }">
    <!-- si usas KeepAlive, EXCLUYE AdminUsuarios -->
    <!-- <KeepAlive exclude="AdminUsuarios"> -->
      <component :is="Component" :key="route.fullPath" />
    <!-- </KeepAlive> -->
  </RouterView>
</template>



<script setup>
import Navbar from './components/Navbar.vue'
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()

onMounted(() => {
  auth.checkLogin()
})
</script>

<style scoped>
body {
  margin: 0;
  font-family: sans-serif;
  background-color: #000000 !important;
}
</style>
