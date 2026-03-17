<template>
  <nav id="nav" class="fixed inset-x-0 top-0 z-50 bg-slate-900/95 backdrop-blur supports-[backdrop-filter]:bg-slate-900/80 border-b border-slate-800">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="h-14 flex items-center justify-between">

        <!-- Brand + mobile toggle -->
        <div class="flex items-center gap-3">
          <RouterLink to="/" class="flex items-center">
            <img src="/logo-mktska.png" alt="Mktska Digital" class="h-9 w-auto object-contain" />
          </RouterLink>

          <!-- Mobile toggle -->
          <button
            class="inline-flex lg:hidden items-center justify-center p-2 rounded text-slate-300 hover:bg-slate-800"
            @click="openMobile = !openMobile" aria-label="Abrir menú">
            <span v-if="!openMobile">☰</span>
            <span v-else>✕</span>
          </button>
        </div>

        <!-- Search -->
        <div class="hidden md:flex flex-1 mx-6 relative" @click.outside="showDropdown=false">
          <form class="w-full flex gap-1" @submit.prevent="goSearch">
            <input
              v-model="q"
              type="search"
              placeholder="Buscar productos…"
              class="flex-1 h-9 rounded-l-md bg-slate-800/70 text-slate-100 placeholder-slate-400 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 px-3"
              role="combobox"
              :aria-expanded="showDropdown"
              aria-controls="search-suggestions"
              @keydown="onKeydown"
              @focus="onFocus"
            />
            <button
              type="submit"
              class="h-9 px-3 bg-cyan-500 hover:bg-cyan-400 text-white rounded-r-md transition flex items-center"
              aria-label="Buscar"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-4.35-4.35m0 0A7.5 7.5 0 1 0 6.15 6.15a7.5 7.5 0 0 0 10.5 10.5Z"/>
              </svg>
            </button>
          </form>
          <div
            v-if="showDropdown"
            id="search-suggestions"
            role="listbox"
            class="absolute top-full left-0 right-0 translate-y-1 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-50 max-h-96 overflow-auto pointer-events-auto text-slate-100"
          >
            <div v-if="loading" class="p-3 space-y-2">
              <div v-for="n in 5" :key="n" class="flex items-center gap-3 px-1">
                <div class="w-10 h-10 bg-slate-700 rounded-lg animate-pulse shrink-0"></div>
                <div class="flex-1 h-4 bg-slate-700 rounded animate-pulse"></div>
                <div class="w-16 h-4 bg-slate-700 rounded animate-pulse shrink-0"></div>
              </div>
            </div>
            <div v-else-if="error" class="p-3 text-sm text-rose-300">Error al cargar</div>
            <div v-else-if="!suggestions.length" class="p-3 text-sm text-slate-400">Sin resultados</div>
            <ul v-else>
              <li
                v-for="(item, i) in suggestions"
                :key="item.id"
                role="option"
                :aria-selected="i === activeIndex"
                @mouseenter="activeIndex = i"
                @mouseleave="activeIndex = -1"
                @click="selectSuggestion(item)"
                class="flex items-center gap-3 px-3 py-2.5 cursor-pointer transition-colors hover:bg-slate-800"
                :class="{ 'bg-slate-800': i === activeIndex }"
              >
                <img
                  :src="imgSrc(item)"
                  @error="onImgError"
                  class="w-10 h-10 object-cover rounded-lg shrink-0 bg-slate-800"
                  alt=""
                />
                <div class="flex-1 truncate text-sm text-slate-100">{{ item.name }}</div>
                <div class="text-sm font-semibold text-cyan-300 whitespace-nowrap shrink-0">
                  {{ fmt(item.price_sale ?? item.price) }}
                </div>
              </li>
              <li class="border-t border-slate-700">
                <button
                  class="w-full text-center px-3 py-2.5 text-sm text-cyan-400 hover:bg-slate-800 hover:text-cyan-300 transition-colors"
                  @click.prevent="moreResults"
                >
                  Ver todos los resultados →
                </button>
              </li>
            </ul>
          </div>
        </div>

        <!-- Right actions -->
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="inline-flex items-center justify-center w-9 h-9 rounded-md border border-slate-700 text-slate-200 hover:bg-slate-800"
            :aria-label="isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'"
            :title="isDark ? 'Modo claro' : 'Modo oscuro'"
            @click="toggleTheme"
          >
            <span v-if="isDark">☀</span>
            <span v-else>☾</span>
          </button>

          <!-- Links desktop -->
          <div class="hidden lg:flex items-center gap-4 text-sm">
            <RouterLink :to="{name:'productos'}"
              class="px-2 py-1 rounded hover:text-cyan-300"
              :class="isActive('/productos') ? 'text-cyan-300' : 'text-slate-200'">
              Tienda
            </RouterLink>

            <div class="relative" v-click-outside="() => openCategories = false">
              <RouterLink :to="{name:'categorias'}"
                class="px-2 py-1 rounded hover:text-cyan-300"
                :class="isActive('/categorias') ? 'text-cyan-300' : 'text-slate-200'"
                @click.prevent="openCategories = !openCategories">
                Categorías
              </RouterLink>
              <div v-if="openCategories" class="absolute left-0 mt-2 w-64 bg-slate-900 border border-slate-700 rounded-md shadow-lg">
                <CategoryMenu />
              </div>
            </div>

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
           <!-- <RouterLink v-if="auth.isAuthenticated" to="/carrito" -->
          <RouterLink  to="/carrito"
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
        <div class="px-1 pt-2 relative" @click.outside="showDropdown=false">
          <form @submit.prevent="goSearch" class="flex gap-1">
            <input
              v-model="q"
              type="search"
              placeholder="Buscar productos…"
              class="flex-1 h-10 rounded-l-md bg-slate-800/70 text-slate-100 placeholder-slate-400 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 px-3"
              role="combobox"
              :aria-expanded="showDropdown"
              aria-controls="search-suggestions"
              @keydown="onKeydown"
              @focus="onFocus"
            />
            <button
              type="submit"
              class="h-10 px-3 bg-cyan-500 hover:bg-cyan-400 text-white rounded-r-md transition flex items-center"
              aria-label="Buscar"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-4.35-4.35m0 0A7.5 7.5 0 1 0 6.15 6.15a7.5 7.5 0 0 0 10.5 10.5Z"/>
              </svg>
            </button>
          </form>
          <div
            v-if="showDropdown"
            id="search-suggestions"
            role="listbox"
            class="absolute top-full left-0 right-0 translate-y-1 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-50 max-h-96 overflow-auto pointer-events-auto text-slate-100"
          >
            <div v-if="loading" class="p-3 space-y-2">
              <div v-for="n in 5" :key="n" class="flex items-center gap-3 px-1">
                <div class="w-10 h-10 bg-slate-700 rounded-lg animate-pulse shrink-0"></div>
                <div class="flex-1 h-4 bg-slate-700 rounded animate-pulse"></div>
                <div class="w-16 h-4 bg-slate-700 rounded animate-pulse shrink-0"></div>
              </div>
            </div>
            <div v-else-if="error" class="p-3 text-sm text-rose-300">Error al cargar</div>
            <div v-else-if="!suggestions.length" class="p-3 text-sm text-slate-400">Sin resultados</div>
            <ul v-else>
              <li
                v-for="(item, i) in suggestions"
                :key="item.id"
                role="option"
                :aria-selected="i === activeIndex"
                @mouseenter="activeIndex = i"
                @mouseleave="activeIndex = -1"
                @click="selectSuggestion(item)"
                class="flex items-center gap-3 px-3 py-2.5 cursor-pointer transition-colors hover:bg-slate-800"
                :class="{ 'bg-slate-800': i === activeIndex }"
              >
                <img
                  :src="imgSrc(item)"
                  @error="onImgError"
                  class="w-10 h-10 object-cover rounded-lg shrink-0 bg-slate-800"
                  alt=""
                />
                <div class="flex-1 truncate text-sm text-slate-100">{{ item.name }}</div>
                <div class="text-sm font-semibold text-cyan-300 whitespace-nowrap shrink-0">
                  {{ fmt(item.price_sale ?? item.price) }}
                </div>
              </li>
              <li class="border-t border-slate-700">
                <button
                  class="w-full text-center px-3 py-2.5 text-sm text-cyan-400 hover:bg-slate-800 hover:text-cyan-300 transition-colors"
                  @click.prevent="moreResults"
                >
                  Ver todos los resultados →
                </button>
              </li>
            </ul>
          </div>
        </div>
        <div class="mt-3 grid gap-1 text-sm">
          <button
            type="button"
            class="px-3 py-2 rounded border border-slate-700 text-slate-200 hover:bg-slate-800 text-left"
            @click="toggleTheme"
          >
            {{ isDark ? 'Usar modo claro' : 'Usar modo oscuro' }}
          </button>
          <RouterLink to="/productos" class="px-3 py-2 rounded hover:bg-slate-800 text-slate-200" @click="openMobile=false">Tienda</RouterLink>
          <RouterLink to="/categorias" class="px-3 py-2 rounded hover:bg-slate-800 text-slate-200" @click="openMobile=false">Categorías</RouterLink>
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
import { onMounted, watch, ref, computed, onBeforeUnmount } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCarritoStore } from '@/stores/carrito'
import CategoryMenu from './CategoryMenu.vue'
import { useTheme } from '@/composables/useTheme'
import api from '@/axios'

const DEFAULT_THUMB = '/placeholder-product.png'

const imgSrc = (item) => item.thumbnail || DEFAULT_THUMB
const onImgError = (e) => { e.target.src = DEFAULT_THUMB }

defineOptions({ name: 'AppNavbar' })
const auth = useAuthStore()
const carrito = useCarritoStore()
const router = useRouter()
const route = useRoute()
const { isDark, toggleTheme } = useTheme()

// UI state
const openMobile = ref(false)
const openUser = ref(false)
const openCategories = ref(false)
const q = ref(route.query.q ?? '')
const suggestions = ref([])
const loading = ref(false)
const error = ref(false)
const showDropdown = ref(false)
const activeIndex = ref(-1)
let debounceId = null

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
  const term = q.value?.trim()
  if (!term) return
  showDropdown.value = false
  openMobile.value = false
  router.push({ name: 'busqueda', query: { q: term } })
  q.value = ''
}

const fetchSuggestions = async (term) => {
  const res = await api.get('productos/', { params: { search: term, page_size: 10 } })
  const data = res.data
  const list = Array.isArray(data) ? data : (data?.results ?? [])
  return list.slice(0, 10).map(p => ({
    id: p.id,
    name: p.nombre,
    price: p.precio_normal,
    price_sale: p.precio_rebajado,
    thumbnail: p.miniatura || p.imagen_principal || null,
  }))
}

watch(q, (val) => {
  if (debounceId) clearTimeout(debounceId)
  const term = val.trim()
  if (term.length < 2) {
    suggestions.value = []
    showDropdown.value = false
    loading.value = false
    error.value = false
    return
  }
  loading.value = true
  showDropdown.value = true
  debounceId = setTimeout(async () => {
    error.value = false
    activeIndex.value = -1
    try {
      suggestions.value = await fetchSuggestions(term)
    } catch {
      error.value = true
    } finally {
      loading.value = false
    }
  }, 300)
})

const onKeydown = (e) => {
  if (!showDropdown.value && e.key !== 'Escape') return
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIndex.value =
      activeIndex.value < suggestions.value.length - 1 ? activeIndex.value + 1 : -1
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value =
      activeIndex.value > -1 ? activeIndex.value - 1 : suggestions.value.length - 1
  } else if (e.key === 'Enter') {
    if (activeIndex.value > -1 && suggestions.value[activeIndex.value]) {
      selectSuggestion(suggestions.value[activeIndex.value])
    } else {
      goSearch()
    }
  } else if (e.key === 'Escape') {
    showDropdown.value = false
  }
}

const onFocus = () => {
  if (suggestions.value.length) showDropdown.value = true
}

const selectSuggestion = (item) => {
  showDropdown.value = false
  if (item?.id != null) {
    router.push({ name: 'producto', params: { id: String(item.id) } })
  } else if (item?.slug) {
    // fallback por si no hay id disponible
    router.push(`/producto/${item.slug}`)
  } else {
    goSearch()
  }
  q.value = ''
}

const moreResults = () => {
  showDropdown.value = false
  goSearch()
}

const fmt = (n) => Number(n).toLocaleString('es-MX', { style: 'currency', currency: 'MXN' })

onMounted(() => {
  carrito.cargar()
})
watch(() => auth.isAuthenticated, () => {
  carrito.cargar()
})

// close dropdown on route change
watch(() => route.fullPath, () => {
  openUser.value = false
  openMobile.value = false
  showDropdown.value = false
})

onBeforeUnmount(() => {
  if (debounceId) clearTimeout(debounceId)
})

const logout = () => {
  auth.logout()
  router.push('/login')
}
</script>
