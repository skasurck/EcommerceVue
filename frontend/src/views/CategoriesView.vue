<template>
  <div class="min-h-screen bg-[#060c18] text-white">

    <!-- Hero -->
    <div class="relative overflow-hidden bg-gradient-to-b from-slate-900 to-[#060c18] py-16 px-4">
      <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-10%,rgba(6,182,212,0.12),transparent)]"></div>
      <!-- grid lines decoration -->
      <div class="pointer-events-none absolute inset-0 opacity-[0.04]"
           style="background-image: linear-gradient(rgba(255,255,255,0.5) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.5) 1px,transparent 1px);background-size:60px 60px"></div>
      <div class="relative mx-auto max-w-5xl text-center">
        <p class="mb-3 inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1 text-xs font-medium tracking-widest text-cyan-400 uppercase">
          <span class="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
          Catálogo completo
        </p>
        <h1 class="text-4xl font-extrabold tracking-tight sm:text-5xl">
          Explora por
          <span class="bg-gradient-to-r from-cyan-400 via-blue-400 to-violet-500 bg-clip-text text-transparent"> Categoría</span>
        </h1>
        <p class="mt-4 text-base text-slate-400 max-w-xl mx-auto">
          Encuentra componentes, periféricos y accesorios organizados por tipo de producto.
        </p>
      </div>
    </div>

    <!-- Grid -->
    <div class="mx-auto max-w-7xl px-4 pb-16 pt-4">

      <!-- Skeleton -->
      <div v-if="loading" class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        <div v-for="i in 8" :key="i" class="h-44 rounded-2xl bg-slate-800/60 animate-pulse"></div>
      </div>

      <!-- Cards -->
      <div v-else-if="categories.length" class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        <RouterLink
          v-for="cat in categories"
          :key="cat.id"
          :to="{ name: 'categoria', params: { categoriaId: cat.id } }"
          class="group relative flex flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80 p-5 transition-all duration-300
                 hover:-translate-y-1 hover:border-opacity-70 hover:shadow-[0_0_35px_-8px]"
          :style="{ '--tw-shadow-color': getConfig(cat.nombre).color + '66',
                    '--hover-border': getConfig(cat.nombre).color + '60' }"
          :class="`hover:border-[${getConfig(cat.nombre).color}]`"
        >
          <!-- background glow on hover -->
          <div class="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
               :style="{ background: `radial-gradient(ellipse at 30% 30%, ${getConfig(cat.nombre).color}18, transparent 70%)` }"></div>

          <!-- Top row: icon + arrow -->
          <div class="relative mb-5 flex items-start justify-between">
            <div class="flex h-14 w-14 items-center justify-center rounded-xl transition-transform duration-300 group-hover:scale-110"
                 :style="{ background: `linear-gradient(135deg, ${getConfig(cat.nombre).color}28, ${getConfig(cat.nombre).color}0a)`,
                           border: `1px solid ${getConfig(cat.nombre).color}35` }">
              <svg v-html="getConfig(cat.nombre).iconPath" class="h-7 w-7" :style="{ color: getConfig(cat.nombre).color }"
                   fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true"></svg>
            </div>
            <div class="rounded-lg border border-slate-700 bg-slate-800/60 p-1.5 text-slate-600 transition-all duration-300 group-hover:border-opacity-80 group-hover:text-white"
                 :style="{ '--group-color': getConfig(cat.nombre).color }">
              <svg class="h-3.5 w-3.5 transition-transform duration-300 group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/>
              </svg>
            </div>
          </div>

          <!-- Name + meta -->
          <div class="relative mt-auto">
            <h2 class="font-semibold leading-snug text-slate-100 transition-colors duration-200 group-hover:text-white" style="font-size:0.92rem">
              {{ cat.nombre }}
            </h2>
            <p v-if="cat.subcategorias?.length" class="mt-1 text-xs text-slate-600">
              {{ cat.subcategorias.length }} subcategoría{{ cat.subcategorias.length !== 1 ? 's' : '' }}
            </p>
          </div>

          <!-- Bottom accent line -->
          <div class="absolute bottom-0 left-0 right-0 h-0.5 scale-x-0 rounded-b-2xl transition-transform duration-300 group-hover:scale-x-100"
               :style="{ background: `linear-gradient(90deg, transparent, ${getConfig(cat.nombre).color}, transparent)` }"></div>
        </RouterLink>
      </div>

      <!-- Empty -->
      <div v-else class="py-24 text-center text-slate-500">
        No se encontraron categorías.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCategoriasTree } from '@/api/productos'
import { useHead } from '@vueuse/head'

useHead({ title: 'Categorías — Explorar' })

const categories = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await getCategoriasTree()
    categories.value = data
  } catch (e) {
    console.error('Error cargando categorías', e)
  } finally {
    loading.value = false
  }
})

// Icon SVG path snippets (stroke-based, no fill, single path/group)
const CONFIGS = [
  {
    keys: ['audio', 'video', 'sonido', 'multimedia'],
    color: '#a855f7',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 11-.99-3.467l2.31-.66a2.25 2.25 0 001.632-2.163zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 01-.99-3.467l2.31-.66A2.25 2.25 0 009 15.553z"/>',
  },
  {
    keys: ['computadora', 'laptop', 'notebook'],
    color: '#3b82f6',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25A2.25 2.25 0 015.25 3h13.5A2.25 2.25 0 0121 5.25z"/>',
  },
  {
    keys: ['cómputo', 'computo', 'hardware', 'componente'],
    color: '#06b6d4',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25zm.75-12h9v9h-9v-9z"/>',
  },
  {
    keys: ['energía', 'energia', 'fuente', 'ups', 'batería', 'bateria', 'electr'],
    color: '#f59e0b',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>',
  },
  {
    keys: ['impresión', 'impresion', 'copiado', 'toner', 'tinta', 'escaner'],
    color: '#10b981',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M6.72 13.829c-.24.03-.48.062-.72.096m.72-.096a42.415 42.415 0 0110.56 0m-10.56 0L6.34 18m10.94-4.171c.24.03.48.062.72.096m-.72-.096L17.66 18m0 0l.229 2.523a1.125 1.125 0 01-1.12 1.227H7.231c-.662 0-1.18-.568-1.12-1.227L6.34 18m11.318 0h1.091A2.25 2.25 0 0021 15.75V9.456c0-1.081-.768-2.015-1.837-2.175a48.055 48.055 0 00-1.913-.247M6.34 18H5.25A2.25 2.25 0 013 15.75V9.456c0-1.081.768-2.015 1.837-2.175a48.056 48.056 0 011.913-.247m10.5 0a48.536 48.536 0 00-10.5 0m10.5 0V3.375c0-.621-.504-1.125-1.125-1.125h-8.25c-.621 0-1.125.504-1.125 1.125v3.659M18 10.5h.008v.008H18V10.5zm-3 0h.008v.008H15V10.5z"/>',
  },
  {
    keys: ['punto de venta', 'pos', 'caja', 'cobro', 'codigo de barras', 'barcode'],
    color: '#f97316',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 013.75 9.375v-4.5zM3.75 14.625c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5a1.125 1.125 0 01-1.125-1.125v-4.5zM13.5 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0113.5 9.375v-4.5z"/><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 6.75h.75v.75h-.75v-.75zM6.75 16.5h.75v.75h-.75v-.75zM16.5 6.75h.75v.75h-.75v-.75zM13.5 13.5h.75v.75h-.75v-.75zM13.5 19.5h.75v.75h-.75v-.75zM19.5 13.5h.75v.75h-.75v-.75zM19.5 19.5h.75v.75h-.75v-.75zM16.5 16.5h.75v.75h-.75v-.75z"/>',
  },
  {
    keys: ['seguridad', 'vigilancia', 'camara', 'cámara', 'cctv', 'alarma'],
    color: '#ef4444',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m0-10.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.75c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.57-.598-3.75h-.152c-3.196 0-6.1-1.249-8.25-3.286zm0 13.036h.008v.008H12v-.008z"/>',
  },
  {
    keys: ['software', 'servicio', 'licencia', 'aplicacion', 'aplicación'],
    color: '#8b5cf6',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M6.75 7.5l3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0021 18V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v12a2.25 2.25 0 002.25 2.25z"/>',
  },
  {
    keys: ['red', 'networking', 'switch', 'router', 'wifi', 'cable'],
    color: '#06d6a0',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M8.288 15.038a5.25 5.25 0 017.424 0M5.106 11.856c3.807-3.808 9.98-3.808 13.788 0M1.924 8.674c5.565-5.565 14.587-5.565 20.152 0M12.53 18.22l-.53.53-.53-.53a.75.75 0 011.06 0z"/>',
  },
  {
    keys: ['almacenamiento', 'disco', 'ssd', 'hdd', 'storage'],
    color: '#14b8a6',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125"/>',
  },
]

const DEFAULT_CONFIG = {
  color: '#64748b',
  iconPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"/>',
}

const getConfig = (nombre) => {
  const lower = nombre.toLowerCase()
  for (const cfg of CONFIGS) {
    if (cfg.keys.some((k) => lower.includes(k))) return cfg
  }
  return DEFAULT_CONFIG
}
</script>
