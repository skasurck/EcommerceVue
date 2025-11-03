<template>
  <!-- Navbar solo fuera de /admin -->
  <Navbar v-if="!isAdmin" />

  <!-- Si hay navbar, damos padding-top. Si no, 0 -->
  <main :style="{ paddingTop: isAdmin ? '0px' : navHeight }">
    <RouterView v-slot="{ Component, route }">
      <component :is="Component" :key="route.fullPath" />
    </RouterView>
  </main>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import { onMounted, onUnmounted, ref, computed, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()

// ¿estamos en el layout admin?
const isAdmin = computed(() => route.path.startsWith('/admin'))

// altura dinámica del navbar público
const navHeight = ref('0px')
const setNavHeight = () => {
  const el = document.getElementById('nav')
  navHeight.value = el ? `${el.offsetHeight}px` : '0px'
}

const activityHandler = () => {
  if (auth.isAuthenticated) {
    auth.resetInactivityTimer()
  }
}

onMounted(async () => {
  auth.checkLogin()
  await nextTick()
  setNavHeight()
  window.addEventListener('mousemove', activityHandler)
  window.addEventListener('keydown', activityHandler)
  window.addEventListener('scroll', activityHandler)
  window.addEventListener('click', activityHandler)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', activityHandler)
  window.removeEventListener('keydown', activityHandler)
  window.removeEventListener('scroll', activityHandler)
  window.removeEventListener('click', activityHandler)
  auth.clearInactivityTimer()
})

// Recalcular al cambiar de ruta (p. ej. entras/sales de admin)
watch(() => route.fullPath, async () => {
  await nextTick()
  setNavHeight()
})
</script>

<style scoped>
body {
  margin: 0;
  font-family: sans-serif;
  background-color: #000000 !important;
}
</style>
