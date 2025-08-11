<template>
  <nav id="nav" class="fixed inset-x-0 top-0 z-50 bg-slate-900/95 backdrop-blur supports-[backdrop-filter]:bg-slate-900/80 border-b border-slate-800">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="h-14 flex items-center justify-between">

        <!-- Brand + mobile toggle -->
        <div class="flex items-center gap-3">
          <RouterLink to="/" class="flex items-center gap-2 text-cyan-400 hover:text-white font-semibold">
            <span class="text-xl">🛒</span>
            <span class="text-lg hidden xs:inline">MiTienda</span>
          </RouterLink>

          <!-- Mobile toggle -->
          <button
            class="inline-flex lg:hidden items-center justify-center p-2 rounded text-slate-300 hover:bg-slate-800"
            @click="openMobile = !openMobile" aria-label="Abrir menú">
            <span v-if="!openMobile">☰</span>
            <span v-else>✕</span>
          </button>
        </div>

        <!-- Search (opcional) -->
        <div class="hidden md:flex flex-1 mx-6">
          <form class="w-full" @submit.prevent="goSearch">
            <input v-model="q" type="search" placeholder="Buscar productos…"
                   class="w-full h-9 rounded-md bg-slate-800/70 text-slate-100 placeholder-slate-400 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 px-3" />
          </form>
        </div>

        <!-- Right actions -->
        <div class="flex items-center gap-3">
          <!-- Links desktop -->
          <div class="hidden lg:flex items-center gap-4 text-sm">
            <RouterLink :to="{name:'productos'}"
              class="px-2 py-1 rounded hover:text-cyan-300"
              :class="isActive('/productos') ? 'text-cyan-300' : 'text-slate-200'">
              Productos
            </RouterLink>

            <RouterLink v-if="auth.isAuthenticated" to="/mi-cuenta"
              class="px-2 py-1 rounded hover:text-cyan-300"
              :class="isActive('/mi-cuenta') ? 'text-cyan-300' : 'text-slate-200'">
              Mi cuenta
            </RouterLink>

            <RouterLink v-if="auth.isAuthenticated && auth.hasAnyRole?.(['admin','super_admin'])"
              to="/admin"
              class="px-2 py-1 rounded hover:text-cyan-300"
              :class="sectionActive('/admin') ? 'text-cyan-300' : 'text-slate-200'">
              Admin
            </RouterLink>
          </div>

          <!-- Cart -->
          <RouterLink v-if="auth.isAuthenticated" to="/carrito"
            class="relative inline-flex items-center justify-center w-9 h-9 rounded-md hover:bg-slate-800 text-slate-200"
            aria-label="Carrito">
            <span>🛒</span>
            <span v-if="carrito.totalCantidad"
                  class="absolute -top-1 -right-1 min-w-[18px] h-[18px] text-[11px] leading-[18px] text-center rounded-full bg-fuchsia-600 text-white px-1">
              {{ carrito.totalCantidad }}
            </span>
          </RouterLink>

          <!-- Auth buttons / user menu -->
          <div v-if="!auth.isAuthenticated" class="hidden sm:flex items-center gap-2">
            <RouterLink to="/login" class="text-slate-200 hover:text-cyan-300 text-sm">Entrar</RouterLink>
            <RouterLink to="/registro" class="text-slate-200 hover:text-cyan-300 text-sm">Registrarse</RouterLink>
          </div>

          <div v-else class="relative">
            <button @click="openUser = !openUser"
                    class="flex items-center gap-2 px-2 py-1 rounded-md hover:bg-slate-800 text-slate-200">
              <span class="inline-block w-6 h-6 rounded-full bg-slate-700 grid place-items-center text-[12px]">
                {{ initials }}
              </span>
              <span class="hidden md:inline text-sm truncate max-w-[140px]">{{ userLabel }}</span>
            </button>

            <div v-if="openUser"
                 @click.outside="openUser=false"
                 class="absolute right-0 mt-2 w-56 rounded-md border border-slate-700 bg-slate-900 shadow-lg p-1">
              <RouterLink to="/mi-cuenta" class="block px-3 py-2 rounded hover:bg-slate-800 text-sm text-slate-200">Mi cuenta</RouterLink>
              <RouterLink v-if="auth.hasAnyRole?.(['admin','super_admin'])" to="/admin" class="block px-3 py-2 rounded hover:bg-slate-800 text-sm text-slate-200">Panel admin</RouterLink>
              <button @click="logout"
                      class="w-full text-left block px-3 py-2 rounded hover:bg-slate-800 text-sm text-rose-300">
                Cerrar sesión
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Mobile panel -->
      <div v-show="openMobile" class="lg:hidden pb-3">
        <form class="px-1 pt-2" @submit.prevent="goSearch">
          <input v-model="q" type="search" placeholder="Buscar productos…"
                 class="w-full h-10 rounded-md bg-slate-800/70 text-slate-100 placeholder-slate-400 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 px-3" />
        </form>
        <div class="mt-3 grid gap-1 text-sm">
          <RouterLink to="/productos" class="px-3 py-2 rounded hover:bg-slate-800 text-slate-200" @click="openMobile=false">Productos</RouterLink>
          <RouterLink v-if="auth.isAuthenticated" to="/mi-cuenta" class="px-3 py-2 rounded hover:bg-slate-800 text-slate-200" @click="openMobile=false">Mi cuenta</RouterLink>
          <RouterLink v-if="auth.isAuthenticated && auth.hasAnyRole?.(['admin','super_admin'])" to="/admin" class="px-3 py-2 rounded hover:bg-slate-800 text-slate-200" @click="openMobile=false">Admin</RouterLink>
          <div v-if="!auth.isAuthenticated" class="flex gap-2 px-3 pt-1">
            <RouterLink to="/login" class="px-3 py-2 rounded bg-slate-800 text-slate-200 flex-1 text-center" @click="openMobile=false">Entrar</RouterLink>
            <RouterLink to="/registro" class="px-3 py-2 rounded border border-slate-700 text-slate-200 flex-1 text-center" @click="openMobile=false">Registrarse</RouterLink>
          </div>
          <button v-else class="px-3 py-2 rounded bg-rose-600/90 hover:bg-rose-600 text-white text-left" @click="logout">Cerrar sesión</button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { onMounted, watch, ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCarritoStore } from '@/stores/carrito'

defineOptions({ name: 'AppNavbar' })
const auth = useAuthStore()
const carrito = useCarritoStore()
const router = useRouter()
const route = useRoute()

// UI state
const openMobile = ref(false)
const openUser = ref(false)
const q = ref(route.query.q ?? '')

// helpers
const isActive = (path) => route.path === path
const sectionActive = (prefix) => route.path.startsWith(prefix)
const userLabel = computed(() => auth.user?.nombre || auth.user?.email || '')
const initials = computed(() => {
  const n = userLabel.value?.trim() || ''
  const parts = n.split(' ')
  const first = (parts[0] || n).charAt(0)
  const second = parts[1]?.charAt(0) || ''
  return (first + second).toUpperCase()
})

const goSearch = () => {
  if (!q.value?.trim()) return
  router.push({ name: 'productos', query: { q: q.value.trim() } })
  openMobile.value = false
}

onMounted(() => {
  if (auth.isAuthenticated) carrito.cargar()
})
watch(() => auth.isAuthenticated, (v) => {
  if (v) carrito.cargar()
  else { carrito.items = []; carrito.reservaExpira = null }
})

// close dropdown on route change
watch(() => route.fullPath, () => { openUser.value = false; openMobile.value = false })

const logout = () => {
  auth.logout()
  router.push('/login')
}
</script>
