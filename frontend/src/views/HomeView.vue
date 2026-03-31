<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useHead } from '@vueuse/head'
import ProductRow from '@/components/ProductRow.vue'
import ProductCard from '@/components/ProductCard.vue'
import { obtenerProductos, obtenerHomeSlider, obtenerPromoBanners, obtenerProductosDestacados } from '@/services/api.js'
import api from '@/axios'
import { useCarritoStore } from '@/stores/carrito'

const SITE_URL = typeof window !== 'undefined' ? window.location.origin : 'https://mktska.net'
const OG_IMAGE = `${SITE_URL}/logo-mktska.png`

const MEDIA_BASE = (import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? 'http://localhost:8000' : SITE_URL)).replace(/\/+$/, '')
const toMedia = (u) => {
  if (!u) return null
  if (/^(data:|blob:|https?:)/i.test(u)) return u
  if (u.startsWith('/media/')) return `${MEDIA_BASE}${u}`
  return `${MEDIA_BASE}/media/${u.replace(/^\/+/, '')}`
}

useHead({
  title: 'Mktska Digital — Tecnología y cómputo en México',
  meta: [
    { name: 'description', content: 'Tienda de tecnología en México. Encuentra computadoras, componentes, periféricos, impresoras y más. Envíos a todo el país.' },
    { property: 'og:type', content: 'website' },
    { property: 'og:url', content: SITE_URL },
    { property: 'og:title', content: 'Mktska Digital — Tecnología y cómputo en México' },
    { property: 'og:description', content: 'Tienda de tecnología en México. Encuentra computadoras, componentes, periféricos, impresoras y más. Envíos a todo el país.' },
    { property: 'og:image', content: OG_IMAGE },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: 'Mktska Digital — Tecnología y cómputo en México' },
    { name: 'twitter:description', content: 'Tienda de tecnología en México. Encuentra computadoras, componentes, periféricos, impresoras y más.' },
    { name: 'twitter:image', content: OG_IMAGE },
  ],
  link: [
    { rel: 'canonical', href: SITE_URL },
  ],
})

const nuevos = ref([])
const ofertas = ref([])
const destacados = ref([])
const sliderImages = ref([])
const promoBanners = ref([])
const currentSlide = ref(0)
let autoplayTimer = null

// ── Secciones por categoría ──────────────────────────────────────────────────
// Cada entrada define el label visible, el slug de la categoría en la DB,
// y el ref que recibirá los productos.
const CATEGORY_SECTIONS = [
  { label: 'CPU (Procesadores)',        slug: 'procesadores',       icon: '🖥️',  productos: ref([]), catId: ref(null) },
  { label: 'GPU (Tarjetas de Video)',   slug: 'tarjetas-de-video',  icon: '🎮',  productos: ref([]), catId: ref(null) },
  { label: 'Memoria RAM',               slug: 'memorias-ram-flash', icon: '💾',  productos: ref([]), catId: ref(null) },
  { label: 'SSD / NVMe',               slug: 'ssd',                icon: '⚡',  productos: ref([]), catId: ref(null) },
  { label: 'Tarjetas Madre',            slug: 'tarjetas-madre',     icon: '🔧',  productos: ref([]), catId: ref(null) },
  { label: 'Fuentes de Poder',          slug: 'fuentes-poder-pc',   icon: '🔌',  productos: ref([]), catId: ref(null) },
]

const cartStore = useCarritoStore()
const allProductsForCart = computed(() => [
  ...nuevos.value, ...ofertas.value, ...destacados.value,
  ...CATEGORY_SECTIONS.flatMap(s => s.productos.value),
])

const handleAddToCart = (product) => {
  const snapshot = { ...product }
  // Actualizar stock en cualquier lista que contenga el producto
  for (const list of [nuevos, ofertas, destacados, ...CATEGORY_SECTIONS.map(s => s.productos)]) {
    const idx = list.value.findIndex(p => p.id === product.id)
    if (idx !== -1) {
      const newStock = Math.max(0, Number(list.value[idx].stock) - 1)
      list.value[idx] = {
        ...list.value[idx],
        stock: newStock,
        estado_inventario: newStock === 0 ? 'agotado' : list.value[idx].estado_inventario,
      }
      break
    }
  }
  cartStore.agregar(snapshot)
}

const fetchCategorySections = async () => {
  try {
    // Traer categorías planas para mapear slug → id
    const { data } = await api.get('categorias/?page_size=500')
    const catList = Array.isArray(data) ? data : (data?.results ?? [])
    const slugToId = {}
    catList.forEach(c => { if (c.slug) slugToId[c.slug] = c.id })

    // Cargar las 6 secciones en paralelo
    await Promise.all(
      CATEGORY_SECTIONS.map(async (section) => {
        const catId = slugToId[section.slug]
        if (!catId) return
        section.catId.value = catId
        try {
          const res = await obtenerProductos({ categoria: catId, page_size: 12, ordering: '-id' })
          section.productos.value = res.data?.results ?? []
        } catch { /* silencioso */ }
      })
    )
  } catch { /* silencioso */ }
}

const defaultSlides = [
  {
    src: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1600&q=80',
    alt: 'Promoción de tecnología',
  },
  {
    src: 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1600&q=80',
    alt: 'Accesorios y cómputo',
  },
  {
    src: 'https://images.unsplash.com/photo-1468495244123-6c6f11b72bdb?auto=format&fit=crop&w=1600&q=80',
    alt: 'Novedades de la tienda',
  },
]

const canMoveSlide = computed(() => sliderImages.value.length > 1)
const activeDesktopSlide = computed(() => sliderImages.value[currentSlide.value] || null)

const goToSlide = (index) => {
  if (!sliderImages.value.length) return
  const total = sliderImages.value.length
  currentSlide.value = ((index % total) + total) % total
}

const nextSlide = () => {
  goToSlide(currentSlide.value + 1)
}

const prevSlide = () => {
  goToSlide(currentSlide.value - 1)
}

const startAutoplay = () => {
  stopAutoplay()
  autoplayTimer = window.setInterval(() => {
    if (!canMoveSlide.value) return
    nextSlide()
  }, 4500)
}

const stopAutoplay = () => {
  if (!autoplayTimer) return
  clearInterval(autoplayTimer)
  autoplayTimer = null
}

const fetchHomeSlider = async () => {
  try {
    const { data } = await obtenerHomeSlider({ ordering: 'orden' })
    const raw = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
    const mapped = raw
      .filter((item) => item?.imagen_url)
      .map((item) => ({
        src: item.imagen_url,
        mobileSrc: item.imagen_mobile_url || item.imagen_url,
        title: item.titulo || '',
        description: item.descripcion || '',
        titleColor: /^#[0-9A-Fa-f]{6}$/.test(item.titulo_color || '') ? item.titulo_color : '#ea580c',
        mobileTitle: item.titulo_mobile || item.titulo || '',
        mobileDescription: item.descripcion_mobile || item.descripcion || '',
        alt: item.titulo || item.descripcion || 'Slide principal',
      }))
    sliderImages.value = mapped.length ? mapped : [...defaultSlides]
  } catch (err) {
    sliderImages.value = [...defaultSlides]
    console.error('No se pudo cargar el slider del home:', err)
  }
}

const fetchBloque = async (params) => {
  const res = await obtenerProductos({ page: 1, page_size: 12, ...params })
  return res.data?.results || []
}

onMounted(async () => {
  await fetchHomeSlider()
  startAutoplay()

  const [ofertasResponse, allProductsResponse, bannersResponse, destacadosResponse] = await Promise.all([
    fetchBloque({ en_oferta: 'true', page_size: 12 }).catch(() => []),
    fetchBloque().catch(() => []),
    obtenerPromoBanners({ ordering: 'orden' }).then(r => {
      const raw = Array.isArray(r.data?.results) ? r.data.results : Array.isArray(r.data) ? r.data : []
      return raw.filter(b => b.imagen_url)
    }).catch(() => []),
    obtenerProductosDestacados({ limite: 12 }).then(r => {
      return Array.isArray(r.data) ? r.data : []
    }).catch(() => []),
  ])

  ofertas.value = ofertasResponse
  promoBanners.value = bannersResponse
  const all = allProductsResponse

  nuevos.value = [...all].sort((a, b) => b.id - a.id).slice(0, 12)
  destacados.value = destacadosResponse.length > 0 ? destacadosResponse : all.slice(0, 12)

  // Cargar secciones de componentes (no bloquea el render inicial)
  fetchCategorySections()
})

onBeforeUnmount(() => {
  stopAutoplay()
})
</script>

<template>
  <main class="bg-slate-50 dark:bg-slate-950 min-h-screen">
    <h1 class="sr-only">Mktska Digital — Tienda de tecnología y cómputo en México</h1>

    <!-- ── Slider mobile ─────────────────────────────────────────────────────── -->
    <section class="lg:hidden bg-slate-900 min-h-[300px] sm:min-h-[390px]">
      <div class="px-2 py-3 overflow-x-auto mobile-no-scrollbar">
        <div class="flex gap-3 snap-x snap-mandatory">
          <article
            v-for="(slide, index) in sliderImages"
            :key="`mobile-slide-${index}`"
            class="relative snap-start shrink-0 w-[80%] xs:w-[75%] h-[280px] sm:h-[360px] rounded-2xl overflow-hidden border border-white/10"
          >
            <img
              :src="slide.mobileSrc || slide.src"
              :alt="slide.mobileDescription || slide.description || slide.alt"
              class="absolute inset-0 h-full w-full object-cover"
              :fetchpriority="index === 0 ? 'high' : 'low'"
              :loading="index === 0 ? 'eager' : 'lazy'"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-black/55 via-black/15 to-transparent" />
            <div class="relative z-10 p-4">
              <h3
                class="text-4xl leading-8 font-extrabold drop-shadow-md"
                :style="{ color: slide.titleColor }"
              >
                {{ slide.mobileTitle || 'Oferta especial' }}
              </h3>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- ── Slider desktop ────────────────────────────────────────────────────── -->
    <section class="hidden lg:block bg-slate-900">
      <div class="max-w-7xl mx-auto px-4 py-5">
        <div
          class="relative h-52 sm:h-72 md:h-80 lg:h-[420px] rounded-2xl overflow-hidden ring-1 ring-white/10"
          @mouseenter="stopAutoplay"
          @mouseleave="startAutoplay"
        >
          <img
            v-for="(slide, index) in sliderImages"
            :key="`${slide.src}-${index}`"
            :src="slide.src"
            :alt="slide.alt"
            class="absolute inset-0 h-full w-full object-cover transition-opacity duration-500"
            :class="index === currentSlide ? 'opacity-100' : 'opacity-0'"
          />

          <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/15 to-transparent" />

          <div
            v-if="activeDesktopSlide"
            class="absolute left-16 top-16 w-[42%] max-w-2xl"
          >
            <h3
              class="text-5xl xl:text-6xl leading-tight font-extrabold drop-shadow-lg"
              :style="{ color: activeDesktopSlide.titleColor }"
            >
              {{ activeDesktopSlide.title || activeDesktopSlide.mobileTitle || 'Oferta especial' }}
            </h3>
            <p v-if="activeDesktopSlide.description || activeDesktopSlide.mobileDescription" class="mt-3 text-base text-white/90 drop-shadow">
              {{ activeDesktopSlide.description || activeDesktopSlide.mobileDescription }}
            </p>
          </div>

          <button
            class="absolute left-3 top-1/2 -translate-y-1/2 rounded-full w-10 h-10 bg-white/15 hover:bg-white/30 backdrop-blur-sm text-white font-bold text-xl transition-colors"
            type="button"
            aria-label="Imagen anterior"
            @click="prevSlide"
          >‹</button>
          <button
            class="absolute right-3 top-1/2 -translate-y-1/2 rounded-full w-10 h-10 bg-white/15 hover:bg-white/30 backdrop-blur-sm text-white font-bold text-xl transition-colors"
            type="button"
            aria-label="Imagen siguiente"
            @click="nextSlide"
          >›</button>

          <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2">
            <button
              v-for="(_, index) in sliderImages"
              :key="`dot-${index}`"
              type="button"
              class="h-2 rounded-full transition-all duration-300"
              :class="index === currentSlide ? 'bg-white w-6' : 'bg-white/40 hover:bg-white/70 w-2'"
              @click="goToSlide(index)"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- ── Trust bar ─────────────────────────────────────────────────────────── -->
    <section class="bg-slate-900 border-t border-white/5">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <div class="grid grid-cols-2 lg:grid-cols-4 divide-x divide-white/10">
          <div class="flex items-center gap-3 px-4 py-1">
            <div class="shrink-0 text-cyan-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 0 1-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 0 0-3.213-9.193 2.056 2.056 0 0 0-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 0 0-10.026 0 1.106 1.106 0 0 0-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12" />
              </svg>
            </div>
            <div>
              <p class="text-sm font-bold text-white uppercase tracking-wide">Envío Rápido</p>
              <p class="text-xs text-slate-400">Entregas de 1 a 5 días</p>
            </div>
          </div>
          <div class="flex items-center gap-3 px-4 py-1">
            <div class="shrink-0 text-cyan-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Z" />
              </svg>
            </div>
            <div>
              <p class="text-sm font-bold text-white uppercase tracking-wide">Pago Seguro</p>
              <p class="text-xs text-slate-400">100% transacciones protegidas</p>
            </div>
          </div>
          <div class="flex items-center gap-3 px-4 py-1">
            <div class="shrink-0 text-cyan-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z" />
              </svg>
            </div>
            <div>
              <p class="text-sm font-bold text-white uppercase tracking-wide">Soporte 24/7</p>
              <p class="text-xs text-slate-400">Atención dedicada siempre</p>
            </div>
          </div>
          <div class="flex items-center gap-3 px-4 py-1">
            <div class="shrink-0 text-cyan-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043A3.745 3.745 0 0 1 12 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 0 1-3.296-1.043 3.745 3.745 0 0 1-1.043-3.296A3.745 3.745 0 0 1 3 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 0 1 1.043-3.296 3.746 3.746 0 0 1 3.296-1.043A3.746 3.746 0 0 1 12 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.296A3.745 3.745 0 0 1 21 12Z" />
              </svg>
            </div>
            <div>
              <p class="text-sm font-bold text-white uppercase tracking-wide">Garantía 30 días</p>
              <p class="text-xs text-slate-400">Satisfacción o reembolso</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Promo banners ──────────────────────────────────────────────────────── -->
    <div v-if="promoBanners.length" class="max-w-7xl mx-auto px-4 pt-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <component
          :is="banner.enlace ? 'a' : 'div'"
          v-for="banner in promoBanners"
          :key="banner.id"
          :href="banner.enlace || undefined"
          class="relative h-48 rounded-xl overflow-hidden shadow-md block group cursor-pointer"
          :class="{ 'cursor-default': !banner.enlace }"
        >
          <img
            :src="banner.imagen_url"
            :alt="banner.titulo || 'Banner'"
            class="absolute inset-0 h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
          <div class="absolute bottom-0 left-0 p-4">
            <h3
              v-if="banner.titulo"
              class="text-xl font-extrabold leading-tight"
              :style="{ color: /^#[0-9A-Fa-f]{6}$/.test(banner.titulo_color) ? banner.titulo_color : '#ffffff' }"
            >
              {{ banner.titulo }}
            </h3>
            <p v-if="banner.descripcion" class="mt-1 text-sm text-white/90">
              {{ banner.descripcion }}
            </p>
          </div>
        </component>
      </div>
    </div>

    <!-- ── Categorías rápidas ─────────────────────────────────────────────────── -->
    <div class="max-w-7xl mx-auto px-4 pt-8 pb-2">
      <h2 class="text-lg font-bold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
        <span class="block w-1 h-5 rounded-full bg-cyan-500 shrink-0"></span>
        Componentes para PC
      </h2>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <RouterLink
          v-for="section in CATEGORY_SECTIONS"
          :key="section.slug"
          :to="section.catId.value ? `/productos?categoria=${section.catId.value}` : '/productos'"
          class="flex flex-col overflow-hidden rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-cyan-400 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 group"
        >
          <!-- Imagen del primer producto de la categoría -->
          <div class="flex items-center justify-center h-28 sm:h-32 bg-white dark:bg-slate-900 p-3">
            <img
              v-if="section.productos.value[0]?.imagen_principal"
              :src="toMedia(section.productos.value[0].imagen_principal)"
              :alt="section.label"
              loading="lazy"
              class="h-full w-full object-contain transition-transform duration-300 group-hover:scale-105"
            />
            <span v-else class="text-4xl">{{ section.icon }}</span>
          </div>
          <!-- Nombre de la categoría -->
          <div class="px-3 py-2 bg-slate-50 dark:bg-slate-800 border-t border-slate-100 dark:border-slate-700 text-center">
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 group-hover:text-cyan-600 leading-snug">{{ section.label }}</span>
          </div>
        </RouterLink>
      </div>
    </div>

    <!-- ── Productos ─────────────────────────────────────────────────────────── -->
    <!-- min-h-[1200px] reserva espacio para que el footer empiece fuera del viewport
         mientras los productos cargan, evitando CLS de 0.7+ -->
    <div class="max-w-7xl mx-auto px-4 py-6 space-y-8 min-h-[1200px]">
      <ProductRow title="Ofertas del día" :productos="ofertas" to="/productos?ofertas=1" @add-to-cart="handleAddToCart" />
      <ProductRow title="Novedades" :productos="nuevos" to="/productos?orden=-id" @add-to-cart="handleAddToCart" />

      <section>
        <div class="flex items-baseline justify-between mb-3 px-2">
          <h2 class="text-xl font-semibold text-slate-800 dark:text-white flex items-center gap-2">
            <span class="block w-1 h-5 rounded-full bg-cyan-500 shrink-0"></span>
            Destacados
          </h2>
          <RouterLink to="/productos" class="text-sm text-blue-700 hover:underline">Ver más</RouterLink>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <ProductCard v-for="p in destacados" :key="p.id" :producto="p" @add-to-cart="handleAddToCart" />
        </div>
      </section>

      <!-- ── Secciones por categoría de componentes ── -->
      <template v-for="section in CATEGORY_SECTIONS" :key="section.slug">
        <ProductRow
          v-if="section.productos.value.length"
          :title="`${section.icon} ${section.label}`"
          :productos="section.productos.value"
          :to="section.catId.value ? `/productos?categoria=${section.catId.value}` : '/productos'"
          @add-to-cart="handleAddToCart"
        />
      </template>
    </div>

  </main>
</template>

<style scoped>
.mobile-no-scrollbar::-webkit-scrollbar {
  display: none;
}

.mobile-no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
