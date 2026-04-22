<template>
  <!-- Navbar solo fuera de /admin -->
  <Navbar v-if="!isAdmin" />
  <CartDrawer v-if="!isAdmin" />
  <ConsentBanner v-if="!isAdmin" />

  <!-- Si hay navbar, damos padding-top. Si no, 0 -->
  <main
    class="min-h-screen bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors"
    :style="{ paddingTop: isAdmin ? '0px' : navHeight }"
  >
    <Breadcrumb v-if="showBreadcrumb" />
    <RouterView v-slot="{ Component, route }">
      <component :is="Component" :key="route.fullPath" />
    </RouterView>
    <Footer v-if="!isAdmin" />
  </main>

  <!-- Botón flotante de WhatsApp (solo fuera del admin) -->
  <a
    v-if="!isAdmin"
    href="https://wa.me/525571666346"
    target="_blank"
    rel="noopener noreferrer"
    aria-label="Contactar por WhatsApp"
    class="fixed z-40 flex items-center justify-center rounded-full shadow-lg transition-transform hover:scale-110 active:scale-95"
    style="bottom: 80px; right: 18px; width: 52px; height: 52px; background-color: #25d366;"
  >
    <svg viewBox="0 0 32 32" fill="white" xmlns="http://www.w3.org/2000/svg" style="width:30px;height:30px;">
      <path d="M16.003 2.667C8.637 2.667 2.667 8.637 2.667 16c0 2.354.636 4.638 1.846 6.638L2.667 29.333l6.895-1.813A13.27 13.27 0 0 0 16.003 29.333C23.367 29.333 29.333 23.363 29.333 16S23.367 2.667 16.003 2.667Zm0 24.267a11.007 11.007 0 0 1-5.61-1.537l-.402-.24-4.09 1.075 1.09-3.98-.262-.41A10.965 10.965 0 0 1 5.001 16c0-6.065 4.937-11 11.002-11C22.07 5 27 9.935 27 16c0 6.063-4.93 10.934-10.997 10.934Zm6.03-8.198c-.33-.165-1.953-.964-2.256-1.073-.303-.11-.523-.165-.743.165-.22.33-.852 1.073-1.044 1.293-.192.22-.385.247-.715.082-.33-.165-1.394-.514-2.655-1.637-.981-.875-1.644-1.954-1.836-2.284-.192-.33-.02-.508.144-.672.149-.148.33-.385.495-.578.165-.192.22-.33.33-.55.11-.22.055-.412-.027-.578-.083-.165-.743-1.79-1.018-2.45-.268-.642-.54-.554-.743-.564l-.633-.012c-.22 0-.578.083-.88.413-.303.33-1.155 1.128-1.155 2.75s1.182 3.19 1.347 3.41c.165.22 2.327 3.553 5.638 4.984.788.34 1.403.543 1.882.695.79.252 1.51.217 2.078.131.634-.094 1.953-.799 2.228-1.57.275-.77.275-1.43.192-1.57-.083-.137-.303-.22-.633-.385Z"/>
    </svg>
  </a>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import Breadcrumb from './components/Breadcrumb.vue'
import Footer from './components/Footer.vue'
import CartDrawer from './components/CartDrawer.vue'
import ConsentBanner from './components/ConsentBanner.vue'
import { onMounted, onUnmounted, ref, computed, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCarritoStore } from '@/stores/carrito'
import { useTheme } from '@/composables/useTheme'
import { initTracking } from '@/composables/useTracking'

const auth = useAuthStore()
const cart = useCarritoStore()
const route = useRoute()
const { initTheme } = useTheme()

// ¿estamos en el layout admin?
const isAdmin = computed(() => route.path.startsWith('/admin'))

const hideBreadcrumbRoutes = new Set(['home', 'login', 'registro', 'gracias', 'not-found'])
const showBreadcrumb = computed(() =>
  !isAdmin.value && !hideBreadcrumbRoutes.has(route.name)
)

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

// Sincronizar sesión entre pestañas: cuando otra pestaña hace login/logout
// el navegador dispara 'storage' con los cambios de localStorage
const syncAuthAcrossTabs = (e) => {
  if (e.key === 'accessToken' || e.key === 'user') {
    auth.checkLogin()
  }
}

onMounted(async () => {
  initTheme()
  initTracking()
  auth.checkLogin()
  cart.cargar() // <- CARGAR EL CARRITO AL INICIAR
  await nextTick()
  setNavHeight()
  window.addEventListener('mousemove', activityHandler)
  window.addEventListener('keydown', activityHandler)
  window.addEventListener('scroll', activityHandler)
  window.addEventListener('click', activityHandler)
  window.addEventListener('storage', syncAuthAcrossTabs)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', activityHandler)
  window.removeEventListener('keydown', activityHandler)
  window.removeEventListener('scroll', activityHandler)
  window.removeEventListener('click', activityHandler)
  window.removeEventListener('storage', syncAuthAcrossTabs)
  auth.clearInactivityTimer()
})

// Recalcular al cambiar de ruta (p. ej. entras/sales de admin)
watch(() => route.fullPath, async () => {
  await nextTick()
  setNavHeight()
})
</script>
