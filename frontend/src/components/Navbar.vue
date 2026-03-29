<template>
  <nav id="nav" class="fixed inset-x-0 top-0 z-50 bg-white/95 dark:bg-slate-900/95 backdrop-blur supports-[backdrop-filter]:bg-white/85 dark:supports-[backdrop-filter]:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 transition-colors">
    <div class="mx-auto max-w-7xl">

      <!-- ═══════════════════════════════════════════════
           DESKTOP: dos filas estilo Amazon
      ═══════════════════════════════════════════════ -->
      <div class="hidden lg:block">

        <!-- Fila 1: Logo | Ubicación | Búsqueda | Cuenta | Carrito -->
        <div class="flex h-14 items-center gap-4 px-4 lg:px-8">

          <!-- Logo -->
          <RouterLink to="/" class="flex items-center shrink-0">
            <img src="/logo-mktska.png" alt="Mktska Digital" width="120" height="36" class="h-9 w-auto object-contain [filter:brightness(0)] dark:[filter:brightness(0)_invert(1)] transition-[filter]" />
          </RouterLink>

          <!-- Ubicación -->
          <button type="button" @click="changeLocation"
            class="shrink-0 flex flex-col items-start leading-tight hover:ring-1 hover:ring-cyan-400 rounded px-1 py-0.5 transition-shadow">
            <span class="text-[10px] text-slate-500 dark:text-slate-400">Enviar a</span>
            <span class="text-xs font-bold text-slate-800 dark:text-slate-100 flex items-center gap-0.5 max-w-[110px] truncate">
              {{ locationLabel }}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 shrink-0" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
            </span>
          </button>

          <!-- Búsqueda -->
          <div class="flex flex-1 relative" @click.outside="showDropdown=false">
            <form class="w-full flex" @submit.prevent="goSearch">
              <input
                v-model="q"
                type="search"
                placeholder="Buscar productos…"
                class="flex-1 h-10 rounded-l-md bg-slate-100 dark:bg-slate-800/70 text-slate-900 dark:text-slate-100 placeholder-slate-400 border border-slate-300 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 px-3 text-sm"
                role="combobox"
                :aria-expanded="showDropdown"
                aria-controls="search-desktop"
                @keydown="onKeydown"
                @focus="onFocus"
              />
              <button type="submit" class="h-10 px-4 bg-cyan-500 hover:bg-cyan-400 text-white rounded-r-md transition flex items-center" aria-label="Buscar">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-4.35-4.35m0 0A7.5 7.5 0 1 0 6.15 6.15a7.5 7.5 0 0 0 10.5 10.5Z"/>
                </svg>
              </button>
            </form>
            <SearchDropdown id="search-desktop" :show="showDropdown" :loading="loading" :error="error" :suggestions="suggestions" :active-index="activeIndex" @select="selectSuggestion" @more="moreResults" @hover="activeIndex = $event" />
          </div>

          <!-- Cuenta -->
          <div class="shrink-0">
            <!-- No autenticado -->
            <div v-if="!auth.isAuthenticated" class="flex flex-col items-start leading-tight">
              <span class="text-[10px] text-slate-500 dark:text-slate-400">
                Hola, <RouterLink to="/login" class="text-cyan-600 dark:text-cyan-400 hover:underline">identifícate</RouterLink>
              </span>
              <RouterLink to="/login" class="text-xs font-bold text-slate-800 dark:text-slate-100 hover:text-cyan-600 dark:hover:text-cyan-300 flex items-center gap-0.5">
                Cuenta y listas
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
              </RouterLink>
            </div>

            <!-- Autenticado -->
            <div v-else class="relative">
              <button @click="openUser = !openUser"
                class="flex flex-col items-start leading-tight hover:ring-1 hover:ring-cyan-400 rounded px-1 py-0.5 transition-shadow">
                <span class="text-[10px] text-slate-500 dark:text-slate-400">Hola, {{ userFirstName }}</span>
                <span class="text-xs font-bold text-slate-800 dark:text-slate-100 flex items-center gap-0.5">
                  Mi cuenta
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
                </span>
              </button>

              <div v-if="openUser" @click.outside="openUser=false"
                class="absolute right-0 mt-2 w-60 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-xl p-1 z-50">
                <p class="px-3 py-2 text-xs text-slate-500 dark:text-slate-400 border-b border-slate-100 dark:border-slate-800 truncate">{{ userLabel }}</p>
                <!-- Modo oscuro dentro del dropdown -->
                <button @click="toggleTheme" class="w-full flex items-center gap-2 px-3 py-2 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-sm text-slate-700 dark:text-slate-200">
                  <span>{{ isDark ? '☀' : '☾' }}</span>
                  {{ isDark ? 'Modo claro' : 'Modo oscuro' }}
                </button>
                <div class="my-1 border-t border-slate-100 dark:border-slate-800"></div>
                <RouterLink to="/mi-cuenta" class="block px-3 py-2 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-sm text-slate-700 dark:text-slate-200">Mi cuenta</RouterLink>
                <RouterLink to="/lista-deseos" class="flex items-center gap-2 px-3 py-2 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-sm text-slate-700 dark:text-slate-200">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  Lista de deseos
                  <span v-if="wishlist.total" class="ml-auto text-xs bg-rose-500 text-white rounded-full px-1.5">{{ wishlist.total }}</span>
                </RouterLink>
                <RouterLink v-if="auth.hasAnyRole?.(['admin','super_admin'])" to="/admin" class="block px-3 py-2 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-sm text-slate-700 dark:text-slate-200">Panel admin</RouterLink>
                <div class="my-1 border-t border-slate-100 dark:border-slate-800"></div>
                <button @click="logout" class="w-full text-left block px-3 py-2 rounded hover:bg-rose-50 dark:hover:bg-rose-900/20 text-sm text-rose-500 dark:text-rose-400">Cerrar sesión</button>
              </div>
            </div>
          </div>

          <!-- Carrito -->
          <RouterLink to="/carrito" class="shrink-0 flex flex-col items-center leading-tight hover:ring-1 hover:ring-cyan-400 rounded px-1 py-0.5 transition-shadow" aria-label="Carrito">
            <div class="relative">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-slate-700 dark:text-slate-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 00-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 00-16.536-1.84M7.5 14.25L5.106 5.272M6 20.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm12.75 0a.75.75 0 11-1.5 0 .75.75 0 011.5 0z" />
              </svg>
              <span v-if="carrito.totalCantidad" class="absolute -top-1.5 -right-1.5 min-w-[20px] h-[20px] text-[11px] leading-[20px] text-center rounded-full bg-cyan-500 text-white font-bold px-1">{{ carrito.totalCantidad }}</span>
            </div>
            <span class="text-[10px] font-bold text-slate-800 dark:text-slate-100">Carrito</span>
          </RouterLink>
        </div>

        <!-- Fila 2: Links de navegación -->
        <div class="flex items-center gap-1 px-4 lg:px-8 py-1 border-t border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900/60 overflow-x-auto mobile-no-scrollbar">
          <RouterLink to="/"
            class="px-3 py-1.5 rounded text-sm font-medium whitespace-nowrap hover:bg-slate-200 dark:hover:bg-slate-800"
            :class="isActive('/') ? 'text-cyan-600 dark:text-cyan-300' : 'text-slate-700 dark:text-slate-300'">
            Inicio
          </RouterLink>

          <RouterLink to="/productos"
            class="px-3 py-1.5 rounded text-sm font-medium whitespace-nowrap hover:bg-slate-200 dark:hover:bg-slate-800"
            :class="isActive('/productos') ? 'text-cyan-600 dark:text-cyan-300' : 'text-slate-700 dark:text-slate-300'">
            Tienda
          </RouterLink>

          <RouterLink to="/categorias"
            class="px-3 py-1.5 rounded text-sm font-medium whitespace-nowrap hover:bg-slate-200 dark:hover:bg-slate-800"
            :class="sectionActive('/categori') ? 'text-cyan-600 dark:text-cyan-300' : 'text-slate-700 dark:text-slate-300'">
            Categorías
          </RouterLink>

          <RouterLink v-if="auth.isAuthenticated" to="/lista-deseos"
            class="px-3 py-1.5 rounded text-sm font-medium whitespace-nowrap hover:bg-slate-200 dark:hover:bg-slate-800 flex items-center gap-1"
            :class="isActive('/lista-deseos') ? 'text-cyan-600 dark:text-cyan-300' : 'text-slate-700 dark:text-slate-300'">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            Favoritos
            <span v-if="wishlist.total" class="text-xs bg-rose-500 text-white rounded-full px-1.5 leading-4">{{ wishlist.total }}</span>
          </RouterLink>

          <RouterLink v-if="auth.isAuthenticated && auth.hasAnyRole?.(['admin','super_admin'])" to="/admin"
            class="px-3 py-1.5 rounded text-sm font-medium whitespace-nowrap hover:bg-slate-200 dark:hover:bg-slate-800"
            :class="sectionActive('/admin') ? 'text-cyan-600 dark:text-cyan-300' : 'text-slate-700 dark:text-slate-300'">
            Panel admin
          </RouterLink>

          <RouterLink v-if="!auth.isAuthenticated" to="/login"
            class="px-3 py-1.5 rounded text-sm font-medium whitespace-nowrap text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800">
            Entrar
          </RouterLink>
          <RouterLink v-if="!auth.isAuthenticated" to="/registro"
            class="px-3 py-1.5 rounded text-sm font-medium whitespace-nowrap text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800">
            Registrarse
          </RouterLink>

          <!-- Modo oscuro: siempre visible, al final de la barra -->
          <button type="button" @click="toggleTheme"
            class="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium whitespace-nowrap text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 shrink-0">
            <span>{{ isDark ? '☀' : '☾' }}</span>
            {{ isDark ? 'Modo claro' : 'Modo oscuro' }}
          </button>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════
           MOBILE: multi-fila estilo Amazon
      ═══════════════════════════════════════════════ -->
      <div class="lg:hidden">

        <!-- Fila 1: ☰ | Logo | Usuario | Wishlist | Carrito -->
        <div class="h-12 flex items-center px-3 gap-2">
          <button
            class="inline-flex items-center justify-center w-9 h-9 rounded text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 shrink-0"
            @click="openMobile = !openMobile" aria-label="Abrir menú">
            <span v-if="!openMobile" class="text-lg leading-none">☰</span>
            <span v-else class="text-lg leading-none">✕</span>
          </button>

          <RouterLink to="/" class="flex items-center shrink-0">
            <img src="/logo-mktska.png" alt="Mktska Digital" width="120" height="32" class="h-8 w-auto object-contain [filter:brightness(0)] dark:[filter:brightness(0)_invert(1)] transition-[filter]" />
          </RouterLink>

          <!-- User greeting -->
          <RouterLink v-if="auth.isAuthenticated" to="/mi-cuenta"
            class="flex items-center gap-1 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:text-cyan-600 dark:hover:text-cyan-300 ml-1 truncate max-w-[100px]">
            <span class="inline-flex w-6 h-6 rounded-full bg-cyan-100 dark:bg-slate-700 items-center justify-center text-[11px] font-bold text-cyan-700 dark:text-slate-100 shrink-0">{{ initials }}</span>
            <span class="truncate">{{ userFirstName }}</span>
            <span class="text-slate-400 shrink-0">›</span>
          </RouterLink>
          <RouterLink v-else to="/login"
            class="flex items-center gap-1 text-xs text-slate-600 dark:text-slate-300 hover:text-cyan-600 dark:hover:text-cyan-300 ml-1">
            <span class="inline-flex w-6 h-6 rounded-full border border-slate-300 dark:border-slate-600 items-center justify-center text-slate-500 dark:text-slate-400 shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>
            </span>
            <span>Entrar</span>
            <span class="text-slate-400">›</span>
          </RouterLink>

          <div class="flex-1" />

          <!-- Wishlist mobile -->
          <RouterLink v-if="auth.isAuthenticated" to="/lista-deseos"
            class="relative inline-flex items-center justify-center w-9 h-9 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-200 shrink-0"
            aria-label="Lista de deseos">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <span v-if="wishlist.total" class="absolute -top-1 -right-1 min-w-[16px] h-[16px] text-[10px] leading-[16px] text-center rounded-full bg-rose-500 text-white px-0.5">{{ wishlist.total }}</span>
          </RouterLink>

          <!-- Cart mobile -->
          <RouterLink to="/carrito"
            class="relative inline-flex items-center justify-center w-9 h-9 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-200 shrink-0"
            aria-label="Carrito">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 00-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 00-16.536-1.84M7.5 14.25L5.106 5.272M6 20.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm12.75 0a.75.75 0 11-1.5 0 .75.75 0 011.5 0z" />
            </svg>
            <span v-if="carrito.totalCantidad" class="absolute -top-1 -right-1 min-w-[16px] h-[16px] text-[10px] leading-[16px] text-center rounded-full bg-cyan-500 text-white px-0.5">{{ carrito.totalCantidad }}</span>
          </RouterLink>
        </div>

        <!-- Fila 2: Barra de búsqueda (siempre visible) -->
        <div class="px-3 pb-2 relative" @click.outside="showDropdown=false">
          <form @submit.prevent="goSearch" class="flex gap-1">
            <input
              v-model="q"
              type="search"
              placeholder="Buscar productos…"
              class="flex-1 h-10 rounded-l-md bg-slate-100 dark:bg-slate-800/70 text-slate-900 dark:text-slate-100 placeholder-slate-400 border border-slate-300 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 px-3"
              role="combobox"
              :aria-expanded="showDropdown"
              aria-controls="search-mobile"
              @keydown="onKeydown"
              @focus="onFocus"
            />
            <button type="submit" class="h-10 px-3 bg-cyan-500 hover:bg-cyan-400 text-white rounded-r-md transition flex items-center" aria-label="Buscar">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-4.35-4.35m0 0A7.5 7.5 0 1 0 6.15 6.15a7.5 7.5 0 0 0 10.5 10.5Z"/>
              </svg>
            </button>
          </form>
          <!-- Dropdown suggestions mobile -->
          <div v-if="showDropdown" id="search-mobile" role="listbox"
            class="absolute top-full left-3 right-3 translate-y-0.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl shadow-2xl z-50 max-h-96 overflow-auto text-slate-900 dark:text-slate-100">
            <div v-if="loading" class="p-3 space-y-2">
              <div v-for="n in 5" :key="n" class="flex items-center gap-3 px-1">
                <div class="w-9 h-9 bg-slate-200 dark:bg-slate-700 rounded-lg animate-pulse shrink-0"></div>
                <div class="flex-1 h-3.5 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
                <div class="w-14 h-3.5 bg-slate-200 dark:bg-slate-700 rounded animate-pulse shrink-0"></div>
              </div>
            </div>
            <div v-else-if="error" class="p-3 text-sm text-rose-500 dark:text-rose-300">Error al cargar</div>
            <div v-else-if="!suggestions.length" class="p-3 text-sm text-slate-500 dark:text-slate-400">Sin resultados</div>
            <ul v-else>
              <li v-for="(item, i) in suggestions" :key="item.id"
                role="option" :aria-selected="i === activeIndex"
                @mouseenter="activeIndex = i" @mouseleave="activeIndex = -1"
                @click="selectSuggestion(item)"
                class="flex items-center gap-3 px-3 py-2.5 cursor-pointer transition-colors hover:bg-slate-100 dark:hover:bg-slate-800"
                :class="{ 'bg-slate-100 dark:bg-slate-800': i === activeIndex }">
                <img :src="imgSrc(item)" @error="onImgError" class="w-9 h-9 object-cover rounded-lg shrink-0 bg-slate-200 dark:bg-slate-800" alt="" />
                <div class="flex-1 truncate text-sm text-slate-800 dark:text-slate-100">{{ item.name }}</div>
                <div class="text-sm font-semibold text-cyan-600 dark:text-cyan-300 whitespace-nowrap shrink-0">{{ fmt(item.price_sale ?? item.price) }}</div>
              </li>
              <li class="border-t border-slate-200 dark:border-slate-700">
                <button class="w-full text-center px-3 py-2.5 text-sm text-cyan-600 dark:text-cyan-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" @click.prevent="moreResults">
                  Ver todos los resultados →
                </button>
              </li>
            </ul>
          </div>
        </div>

        <!-- Fila 3: Links rápidos -->
        <div class="overflow-x-auto mobile-no-scrollbar border-t border-slate-200 dark:border-slate-700/50">
          <div class="flex items-center gap-1 px-3 py-1.5 whitespace-nowrap text-xs font-semibold">
            <RouterLink to="/productos" class="px-2.5 py-1 rounded-full text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800" @click="openMobile=false">Tienda</RouterLink>
            <RouterLink to="/categorias" class="px-2.5 py-1 rounded-full text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800" @click="openMobile=false">Categorías</RouterLink>
            <RouterLink v-if="auth.isAuthenticated" to="/lista-deseos" class="px-2.5 py-1 rounded-full text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800" @click="openMobile=false">Favoritos</RouterLink>
            <RouterLink v-if="auth.isAuthenticated" to="/mi-cuenta" class="px-2.5 py-1 rounded-full text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800" @click="openMobile=false">Mi cuenta</RouterLink>
            <RouterLink v-if="auth.isAuthenticated && auth.hasAnyRole?.(['admin','super_admin'])" to="/admin" class="px-2.5 py-1 rounded-full text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800" @click="openMobile=false">Admin</RouterLink>
            <RouterLink v-if="!auth.isAuthenticated" to="/login" class="px-2.5 py-1 rounded-full text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800" @click="openMobile=false">Entrar</RouterLink>
            <RouterLink v-if="!auth.isAuthenticated" to="/registro" class="px-2.5 py-1 rounded-full text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800" @click="openMobile=false">Registrarse</RouterLink>
          </div>
        </div>

        <!-- Fila 4: Ubicación de entrega -->
        <div class="px-3 py-1.5 bg-slate-100 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-700/50 flex items-center gap-2 text-xs overflow-hidden">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-slate-500 dark:text-slate-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
          </svg>
          <span class="text-slate-500 dark:text-slate-400 shrink-0">Enviar a</span>
          <button type="button" @click="changeLocation" class="font-semibold text-slate-700 dark:text-slate-200 truncate min-w-0 hover:text-cyan-600 dark:hover:text-cyan-300 text-left">{{ locationLabel }}</button>
          <button type="button" @click="detectLocationByIP" class="shrink-0 rounded bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 px-2 py-0.5 text-[10px] font-semibold text-slate-600 dark:text-slate-300">Auto</button>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════
           MOBILE: menú desplegable (☰)
      ═══════════════════════════════════════════════ -->
      <div v-show="openMobile" class="lg:hidden border-t border-slate-200 dark:border-slate-800">
        <div class="px-3 py-3 grid gap-1 text-sm">

          <!-- Modo oscuro (solo en menú mobile) -->
          <button type="button"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 text-left font-medium"
            @click="toggleTheme">
            <span class="text-base">{{ isDark ? '☀' : '☾' }}</span>
            {{ isDark ? 'Usar modo claro' : 'Usar modo oscuro' }}
          </button>

          <div class="my-1 border-t border-slate-100 dark:border-slate-800"></div>

          <!-- Navegación -->
          <RouterLink to="/" class="px-3 py-2.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 font-medium" @click="openMobile=false">Inicio</RouterLink>
          <RouterLink to="/productos" class="px-3 py-2.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 font-medium" @click="openMobile=false">Tienda</RouterLink>
          <RouterLink to="/categorias" class="px-3 py-2.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 font-medium" @click="openMobile=false">Categorías</RouterLink>
          <RouterLink v-if="auth.isAuthenticated" to="/mi-cuenta" class="px-3 py-2.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 font-medium" @click="openMobile=false">Mi cuenta</RouterLink>
          <RouterLink v-if="auth.isAuthenticated" to="/lista-deseos" class="px-3 py-2.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 font-medium" @click="openMobile=false">Lista de deseos</RouterLink>
          <RouterLink v-if="auth.isAuthenticated && auth.hasAnyRole?.(['admin','super_admin'])" to="/admin" class="px-3 py-2.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 font-medium" @click="openMobile=false">Panel admin</RouterLink>

          <div class="my-1 border-t border-slate-100 dark:border-slate-800"></div>

          <!-- Auth -->
          <div v-if="!auth.isAuthenticated" class="flex gap-2 pt-1">
            <RouterLink to="/login" class="flex-1 text-center px-3 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-white font-semibold" @click="openMobile=false">Entrar</RouterLink>
            <RouterLink to="/registro" class="flex-1 text-center px-3 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 font-medium hover:bg-slate-100 dark:hover:bg-slate-800" @click="openMobile=false">Registrarse</RouterLink>
          </div>
          <button v-else class="px-3 py-2.5 rounded-lg bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400 hover:bg-rose-100 dark:hover:bg-rose-900/30 text-left font-medium" @click="logout">Cerrar sesión</button>
        </div>
      </div>

    </div>
  </nav>
</template>

<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { onMounted, watch, ref, computed, onBeforeUnmount, defineComponent, h } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCarritoStore } from '@/stores/carrito'
import { useWishlistStore } from '@/stores/wishlist'
import CategoryMenu from './CategoryMenu.vue'
import { useTheme } from '@/composables/useTheme'
import api from '@/axios'

const DEFAULT_THUMB = '/placeholder-product.png'
const imgSrc = (item) => item.thumbnail || DEFAULT_THUMB
const onImgError = (e) => { e.target.src = DEFAULT_THUMB }

// Componente inline del dropdown de sugerencias (evita duplicar el template)
const SearchDropdown = defineComponent({
  props: {
    id: String,
    show: Boolean,
    loading: Boolean,
    error: Boolean,
    suggestions: Array,
    activeIndex: Number,
  },
  emits: ['select', 'more', 'hover'],
  setup(props, { emit }) {
    const fmt = (n) => Number(n).toLocaleString('es-MX', { style: 'currency', currency: 'MXN' })
    return () => {
      if (!props.show) return null
      return h('div', {
        id: props.id,
        role: 'listbox',
        class: 'absolute top-full left-0 right-0 translate-y-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl shadow-2xl z-50 max-h-96 overflow-auto text-slate-900 dark:text-slate-100',
      }, props.loading
        ? [h('div', { class: 'p-3 space-y-2' }, Array.from({ length: 5 }, (_, n) =>
            h('div', { key: n, class: 'flex items-center gap-3 px-1' }, [
              h('div', { class: 'w-10 h-10 bg-slate-200 dark:bg-slate-700 rounded-lg animate-pulse shrink-0' }),
              h('div', { class: 'flex-1 h-4 bg-slate-200 dark:bg-slate-700 rounded animate-pulse' }),
              h('div', { class: 'w-16 h-4 bg-slate-200 dark:bg-slate-700 rounded animate-pulse shrink-0' }),
            ])
          ))]
        : props.error
          ? [h('div', { class: 'p-3 text-sm text-rose-500 dark:text-rose-300' }, 'Error al cargar')]
          : !props.suggestions.length
            ? [h('div', { class: 'p-3 text-sm text-slate-500 dark:text-slate-400' }, 'Sin resultados')]
            : [
                h('ul', {}, [
                  ...props.suggestions.map((item, i) =>
                    h('li', {
                      key: item.id,
                      role: 'option',
                      'aria-selected': i === props.activeIndex,
                      class: ['flex items-center gap-3 px-3 py-2.5 cursor-pointer transition-colors hover:bg-slate-100 dark:hover:bg-slate-800', i === props.activeIndex ? 'bg-slate-100 dark:bg-slate-800' : ''].join(' '),
                      onMouseenter: () => emit('hover', i),
                      onMouseleave: () => emit('hover', -1),
                      onClick: () => emit('select', item),
                    }, [
                      h('img', { src: item.thumbnail || DEFAULT_THUMB, class: 'w-10 h-10 object-cover rounded-lg shrink-0 bg-slate-200 dark:bg-slate-800', alt: '' }),
                      h('div', { class: 'flex-1 truncate text-sm text-slate-800 dark:text-slate-100' }, item.name),
                      h('div', { class: 'text-sm font-semibold text-cyan-600 dark:text-cyan-300 whitespace-nowrap shrink-0' }, fmt(item.price_sale ?? item.price)),
                    ])
                  ),
                  h('li', { class: 'border-t border-slate-200 dark:border-slate-700' },
                    h('button', {
                      class: 'w-full text-center px-3 py-2.5 text-sm text-cyan-600 dark:text-cyan-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-cyan-500 dark:hover:text-cyan-300 transition-colors',
                      onClick: (e) => { e.preventDefault(); emit('more') },
                    }, 'Ver todos los resultados →')
                  ),
                ]),
              ]
      )
    }
  },
})

defineOptions({ name: 'AppNavbar' })
const auth = useAuthStore()
const carrito = useCarritoStore()
const wishlist = useWishlistStore()
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

// Ubicación
const LOCATION_KEY = 'home_delivery_location'
const locationLabel = ref(localStorage.getItem(LOCATION_KEY) || 'Tu ubicación')

const saveLocation = (label) => {
  locationLabel.value = label
  localStorage.setItem(LOCATION_KEY, label)
}

const changeLocation = () => {
  const next = window.prompt('Ingresa tu ciudad y código postal', locationLabel.value)
  if (next?.trim()) saveLocation(next.trim())
}

const detectLocationByIP = async () => {
  try {
    const ctrl = new AbortController()
    const t = setTimeout(() => ctrl.abort(), 4000)
    const res = await fetch('https://ipapi.co/json/', { signal: ctrl.signal })
    clearTimeout(t)
    if (!res.ok) return
    const d = await res.json()
    const city = d?.city?.trim() || 'Tu zona'
    const postal = d?.postal?.trim()
    saveLocation(postal ? `${city} ${postal}` : city)
  } catch { /* silencioso */ }
}

// Helpers
const isActive = (path) => route.path === path
const sectionActive = (prefix) => route.path.startsWith(prefix)
const userLabel = computed(() => auth.user?.nombre || auth.user?.email || '')
const userFirstName = computed(() => {
  const n = userLabel.value?.trim()
  if (!n) return ''
  return n.split(/[\s@]/)[0]
})
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
    activeIndex.value = activeIndex.value < suggestions.value.length - 1 ? activeIndex.value + 1 : -1
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = activeIndex.value > -1 ? activeIndex.value - 1 : suggestions.value.length - 1
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
  if (auth.isAuthenticated) wishlist.cargar()
  detectLocationByIP()
})

watch(() => auth.isAuthenticated, (val) => {
  carrito.cargar()
  if (val) {
    wishlist.cargar()
  } else {
    wishlist.clear()
  }
})

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
