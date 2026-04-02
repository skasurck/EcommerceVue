<template>
  <nav v-if="crumbs.length" aria-label="Breadcrumb" class="max-w-7xl mx-auto px-4 pt-3 pb-1">
    <ol class="flex flex-wrap items-center gap-1 text-sm text-slate-500">
      <li v-for="(crumb, i) in crumbs" :key="i" class="flex items-center gap-1">
        <span v-if="i > 0" class="text-slate-300">/</span>
        <router-link
          v-if="crumb.to && i < crumbs.length - 1"
          :to="crumb.to"
          class="hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
        >
          {{ crumb.label }}
        </router-link>
        <span v-else class="text-slate-700 dark:text-slate-300 font-medium truncate max-w-[240px]">
          {{ crumb.label }}
        </span>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useBreadcrumbStore } from '@/stores/breadcrumb'

const route = useRoute()
const breadcrumb = useBreadcrumbStore()

const home    = { label: 'Inicio', to: '/' }
const tienda  = { label: 'Tienda', to: '/productos' }
const cuenta  = { label: 'Mi cuenta', to: '/mi-cuenta' }
const pedidos = { label: 'Mis pedidos', to: '/mis-pedidos' }

const crumbs = computed(() => {
  const name = route.name
  const dyn = breadcrumb.dynamicLabel

  const map = {
    productos:        [home, tienda],
    busqueda:         [home, { label: route.query.q ? `Búsqueda: "${route.query.q}"` : 'Búsqueda' }],
    categoria:        [home, tienda, { label: dyn || String(route.params.categoriaSlug) }],
    marca:            [home, tienda, { label: dyn || String(route.params.marcaId) }],
    producto:         [home, tienda, { label: dyn || '…' }],
    carrito:          [home, { label: 'Carrito', to: '/carrito' }],
    checkout:         [home, { label: 'Carrito', to: '/carrito' }, { label: 'Checkout' }],
    'mi-cuenta':      [home, cuenta],
    MisPedidos:       [home, cuenta, pedidos],
    MiPedidoDetalle:  [home, cuenta, pedidos, { label: `Pedido #${route.params.id}` }],
    Seguridad:        [home, cuenta, { label: 'Seguridad' }],
    Direcciones:      [home, cuenta, { label: 'Direcciones' }],
    'lista-deseos':   [home, { label: 'Lista de deseos' }],
  }

  return map[name] ?? []
})

// Limpiar label dinámico al cambiar de ruta
watch(() => route.name, () => breadcrumb.clear())
</script>
