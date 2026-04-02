<template>
  <div class="min-h-screen bg-slate-100">

    <!-- Overlay oscuro (mobile) -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/50 z-40 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 w-64 bg-slate-900 text-slate-200 z-50 transition-transform duration-300 lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Brand -->
      <div class="h-14 flex items-center px-4 border-b border-slate-800">
        <span class="font-semibold tracking-wide">Mi Tienda Admin</span>
      </div>

      <!-- Nav -->
      <nav class="p-3 space-y-6 text-sm overflow-y-auto h-[calc(100vh-3.5rem)]">
        <!-- Sección: navegación -->
        <div>
          <div class="px-3 mb-2 text-[11px] uppercase tracking-wide text-slate-400">Navegación</div>
          <ul class="space-y-1">
            <li>
              <RouterLink :to="{name:'admin'}"
                class="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="isActive('/admin') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span>📊</span><span>Dashboard</span>
              </RouterLink>
            </li>

            <!-- Productos con submenú -->
            <li>
              <button @click="open.products = !open.products"
                class="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/productos') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span class="flex items-center gap-3"><span>🛍️</span> <span>Productos</span></span>
                <span class="text-xs" :class="open.products ? 'rotate-90' : ''">›</span>
              </button>
              <transition name="fade">
                <ul v-if="open.products" class="mt-1 ml-9 space-y-1">
                  <li>
                    <RouterLink to="/admin/productos"
                      class="block px-2 py-1.5 rounded hover:bg-slate-800"
                      :class="isActive('/admin/productos') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                      Listado
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink to="/admin/productos/nuevo"
                      class="flex items-center justify-between px-2 py-1.5 rounded hover:bg-slate-800"
                      :class="isActive('/admin/productos/nuevo') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                      <span>Nuevo producto</span>
                      <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">nuevo</span>
                    </RouterLink>
                  </li>
                </ul>
              </transition>
            </li>

            <li>
              <RouterLink to="/admin/pedidos"
                class="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/pedidos') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span>🧾</span><span>Pedidos</span>
              </RouterLink>
            </li>

            <li>
              <RouterLink to="/admin/usuarios"
                class="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/usuarios') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span>👤</span><span>Usuarios</span>
              </RouterLink>
            </li>

            <li>
              <RouterLink to="/admin/resenas"
                class="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/resenas') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span>⭐</span><span>Reseñas</span>
              </RouterLink>
            </li>

            <li>
              <RouterLink to="/admin/promotions"
                class="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/promotions') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span>🎉</span><span>Promociones</span>
              </RouterLink>
            </li>

            <li>
              <RouterLink to="/admin/cupones"
                class="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/cupones') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span>🏷️</span><span>Cupones</span>
              </RouterLink>
            </li>

            <!-- Editar página principal con submenú -->
            <li>
              <button @click="open.home = !open.home"
                class="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/home-editor') || sectionActive('/admin/promo-banners') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span class="flex items-center gap-3"><span>🖼️</span> <span>Editar página principal</span></span>
                <span class="text-xs" :class="open.home ? 'rotate-90' : ''">›</span>
              </button>
              <transition name="fade">
                <ul v-if="open.home" class="mt-1 ml-9 space-y-1">
                  <li>
                    <RouterLink to="/admin/home-editor"
                      class="block px-2 py-1.5 rounded hover:bg-slate-800"
                      :class="isActive('/admin/home-editor') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                      Slider principal
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink to="/admin/promo-banners"
                      class="block px-2 py-1.5 rounded hover:bg-slate-800"
                      :class="isActive('/admin/promo-banners') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                      Banners promocionales
                    </RouterLink>
                  </li>
                </ul>
              </transition>
            </li>

            <li>
              <RouterLink to="/admin/ai/clasificar-productos"
                class="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/ai/clasificar-productos') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span>🤖</span><span>Clasificar con IA</span>
              </RouterLink>
            </li>

            <li>
              <RouterLink to="/admin/ai/revisar-clasificaciones"
                class="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/ai/revisar-clasificaciones') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span>✅</span><span>Revisar clasificaciones</span>
              </RouterLink>
            </li>
            <li v-if="auth.hasRole('super_admin')">
              <RouterLink to="/admin/ai/learning-stats"
                class="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/ai/learning-stats') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span>📈</span><span>Estadisticas IA</span>
              </RouterLink>
            </li>

            <li>
              <RouterLink to="/admin/suppliers/supermex"
                class="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/suppliers/supermex') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span>🚚</span><span>Importar Supermex</span>
              </RouterLink>
            </li>

            <li v-if="auth.hasRole('super_admin')">
              <RouterLink to="/admin/configuracion"
                class="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800"
                :class="sectionActive('/admin/configuracion') ? 'bg-slate-800 text-white' : 'text-slate-300'">
                <span>⚙️</span><span>Configuración</span>
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Sección: utilidades -->
        <div>
          <div class="px-3 mb-2 text-[11px] uppercase tracking-wide text-slate-400">Utilidades</div>
          <ul class="space-y-1">
            <li>
              <a href="/" class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 text-slate-300">
                <span>↩️</span><span>Ir al sitio</span>
              </a>
            </li>
            <li>
              <button @click="logout"
                class="w-full text-left flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 text-slate-300">
                <span>🚪</span><span>Cerrar sesión</span>
              </button>
            </li>
          </ul>
        </div>
      </nav>
    </aside>

    <!-- Contenido -->
    <div class="lg:pl-64">
      <!-- Topbar -->
      <header class="h-14 bg-white border-b sticky top-0 z-40 flex items-center justify-between px-4 shadow-sm">
        <!-- Hamburger (solo mobile) -->
        <button
          class="lg:hidden flex items-center justify-center w-9 h-9 rounded-lg hover:bg-slate-100 text-slate-600 mr-2"
          @click="sidebarOpen = true"
          aria-label="Abrir menú"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <div class="text-sm text-slate-500">
          <span class="hidden sm:inline">Dashboard / </span>
          <span class="text-slate-700 font-medium">{{ title }}</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="hidden sm:inline text-sm text-slate-600">Hola, {{ auth.user?.nombre || auth.user?.email }}</span>
          <!-- espacio para notificaciones -->
        </div>
      </header>

      <main class="p-4 lg:p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { computed, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()
const title = computed(() => route.meta?.title || 'Panel')

// sidebar mobile
const sidebarOpen = ref(false)

// cerrar sidebar al navegar
watch(() => route.path, () => {
  sidebarOpen.value = false
})

// submenús
const homeSection = ['/admin/home-editor', '/admin/promo-banners']
const openState = {
  products: true,
  home: homeSection.some(p => route.path.startsWith(p)),
}
const open = ref({ products: true, home: openState.home })
Object.defineProperty(open.value, 'products', {
  get() { return openState.products },
  set(v) { openState.products = v }
})
Object.defineProperty(open.value, 'home', {
  get() { return openState.home },
  set(v) { openState.home = v }
})

// helpers de activo
const isActive = (path) => route.path === path
const sectionActive = (prefix) => route.path.startsWith(prefix)

const logout = () => {
  auth.logout()
  window.location.href = '/login'
}
</script>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity .15s ease }
.fade-enter-from, .fade-leave-to { opacity: 0 }
</style>
