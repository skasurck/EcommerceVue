<template>
  <div class="min-h-screen bg-slate-100">
    <!-- Sidebar -->
    <aside class="fixed inset-y-0 left-0 w-64 bg-slate-900 text-slate-200 z-50">
      <!-- Brand -->
      <div class="h-14 flex items-center px-4 border-b border-slate-800">
        <span class="font-semibold tracking-wide">Mi Tienda Admin</span>
      </div>

      <!-- Nav -->
      <nav class="p-3 space-y-6 text-sm">
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
    <div class="pl-64">
      <!-- Topbar -->
      <header class="h-14 bg-white border-b sticky top-0 z-40 flex items-center justify-between px-4 shadow-sm">
        <div class="text-sm text-slate-500">
          <span class="hidden sm:inline">Dashboard / </span>
          <span class="text-slate-700 font-medium">{{ title }}</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="hidden sm:inline text-sm text-slate-600">Hola, {{ auth.user?.nombre || auth.user?.email }}</span>
          <!-- espacio para notificaciones -->
        </div>
      </header>

      <main class="p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()
const title = computed(() => route.meta?.title || 'Panel')

// submenús
const open = ref({ products: true }) // abre productos por defecto
Object.defineProperty(open.value, 'products', {
  get() { return openState.products },
  set(v) { openState.products = v }
})
const openState = { products: true }

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
