<template>
  <div class="flex flex-col min-h-screen">
    <Navbar />
    <main class="pt-20 px-6 flex-1">
      <router-view />
    </main>
  </div>
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
