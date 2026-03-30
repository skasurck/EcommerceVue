<template>
  <footer class="bg-slate-900 text-slate-300 mt-16">
    <div class="max-w-7xl mx-auto px-4 py-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">

      <!-- Marca -->
      <div class="space-y-3">
        <img src="/logo-mktska.webp" alt="Mktska Digital" width="120" height="32" class="h-8 w-auto dark:hidden" />
        <img src="/logo-mktska-white.webp" alt="Mktska Digital" width="120" height="32" class="h-8 w-auto hidden dark:block" />
        <p class="text-sm text-slate-400 leading-relaxed">
          Tu tienda de tecnología y electrónica de confianza.
        </p>
        <!-- Redes sociales -->
        <div class="flex gap-3 pt-1">
          <a
            v-for="red in redes"
            :key="red.label"
            :href="red.href"
            :aria-label="red.label"
            target="_blank"
            rel="noopener noreferrer"
            class="flex h-8 w-8 items-center justify-center rounded-full bg-slate-700 hover:bg-slate-500 transition-colors"
          >
            <component :is="red.icon" class="h-4 w-4" />
          </a>
        </div>
      </div>

      <!-- Tienda -->
      <div>
        <h3 class="text-sm font-semibold uppercase tracking-wider text-slate-100 mb-3">Tienda</h3>
        <ul class="space-y-2 text-sm">
          <li><router-link to="/productos" class="hover:text-white transition-colors">Productos</router-link></li>
          <li><router-link to="/categorias" class="hover:text-white transition-colors">Categorías</router-link></li>
          <li><router-link to="/busqueda" class="hover:text-white transition-colors">Búsqueda</router-link></li>
          <li><router-link to="/carrito" class="hover:text-white transition-colors">Carrito</router-link></li>
        </ul>
      </div>

      <!-- Mi cuenta -->
      <div>
        <h3 class="text-sm font-semibold uppercase tracking-wider text-slate-100 mb-3">Mi cuenta</h3>
        <ul class="space-y-2 text-sm">
          <li><router-link to="/mi-cuenta" class="hover:text-white transition-colors">Perfil</router-link></li>
          <li><router-link to="/mis-pedidos" class="hover:text-white transition-colors">Mis pedidos</router-link></li>
          <li><router-link to="/direcciones" class="hover:text-white transition-colors">Mis direcciones</router-link></li>
          <li><router-link to="/seguridad" class="hover:text-white transition-colors">Seguridad</router-link></li>
        </ul>
      </div>

      <!-- Información -->
      <div>
        <h3 class="text-sm font-semibold uppercase tracking-wider text-slate-100 mb-3">Información</h3>
        <ul class="space-y-2 text-sm">
          <li><router-link to="/contacto" class="hover:text-white transition-colors">Contacto</router-link></li>
          <li><router-link to="/politica-de-privacidad" class="hover:text-white transition-colors">Política de privacidad</router-link></li>
          <li><router-link to="/terminos-y-condiciones" class="hover:text-white transition-colors">Términos y condiciones</router-link></li>
          <li><router-link to="/politica-de-devoluciones" class="hover:text-white transition-colors">Política de devoluciones</router-link></li>
        </ul>
      </div>
    </div>

    <div class="border-t border-slate-800 py-4 text-center text-xs text-slate-500">
      © {{ year }} Mktska Digital. Todos los derechos reservados.
    </div>
  </footer>
</template>

<script setup>
import { computed, h } from 'vue'

const year = computed(() => new Date().getFullYear())

// Iconos SVG inline como componentes para no depender de librerías externas
const IconFacebook = { render: () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [h('path', { d: 'M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z' })]) }
const IconInstagram = { render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('rect', { x: '2', y: '2', width: '20', height: '20', rx: '5', ry: '5' }),
  h('path', { d: 'M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z' }),
  h('line', { x1: '17.5', y1: '6.5', x2: '17.51', y2: '6.5' }),
]) }
const IconTwitterX = { render: () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [h('path', { d: 'M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z' })]) }
const IconWhatsApp = { render: () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [h('path', { d: 'M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z' })]) }

const redes = [
  { label: 'Facebook',  href: '#', icon: IconFacebook  },
  { label: 'Instagram', href: '#', icon: IconInstagram },
  { label: 'X',         href: '#', icon: IconTwitterX  },
  { label: 'WhatsApp',  href: '#', icon: IconWhatsApp  },
]
</script>
