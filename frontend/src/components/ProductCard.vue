<template>
  <div class="relative bg-white rounded-lg border shadow-sm group overflow-hidden">
    <!-- Wishlist heart button -->
    <button
      type="button"
      class="absolute top-2 right-2 z-20 rounded-full p-1.5 transition-colors"
      :class="isFavorito
        ? 'bg-rose-50 text-rose-500 hover:bg-rose-100'
        : 'bg-white/80 text-gray-300 hover:text-rose-400 hover:bg-rose-50 opacity-0 group-hover:opacity-100'"
      :aria-label="isFavorito ? 'Quitar de favoritos' : 'Agregar a favoritos'"
      @click.prevent.stop="toggleFav"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" :fill="isFavorito ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
    </button>

    <!-- Link & image -->
    <router-link :to="{ name: 'producto', params: { id: (p.id ?? producto.id) } }" class="block">
      <div class="relative">
        <!-- Discount badge -->
        <div v-if="hasDiscount && !isOutOfStock" class="absolute left-2 top-2 z-10 rounded-md bg-rose-600 px-2 py-0.5 text-white text-xs font-semibold">
          -{{ discountPct }}%
        </div>
        <!-- Promo label (shown when discounted) -->
        <div v-if="hasDiscount && !isOutOfStock" class="absolute left-2 top-8 z-10 rounded-md bg-rose-100 px-2 py-0.5 text-rose-700 text-xs font-medium">
          Promoción
        </div>
        <!-- Agotado badge -->
        <div v-if="isOutOfStock" class="absolute right-2 top-2 z-10 rounded-md bg-gray-700 px-2 py-0.5 text-white text-xs font-semibold tracking-wide">
          Agotado
        </div>

        <img
          :src="imgSrc"
          :alt="p.nombre || 'Producto'"
          loading="lazy"
          class="aspect-square w-full rounded-t-lg bg-gray-100 object-cover"
          :class="isOutOfStock ? 'opacity-50 grayscale' : 'group-hover:opacity-90'"
        />
      </div>

      <!-- Content -->
      <div class="p-3">
        <!-- Price -->
        <div class="flex items-baseline gap-2">
          <p class="text-gray-900 font-semibold">
            <span class="text-xl">{{ priceMajor }}</span><span class="align-top text-[10px]">{{ priceMinor }}</span>
          </p>
          <p v-if="hasDiscount" class="text-xs text-gray-500">
            Precio de lista:
            <span class="line-through">{{ listPriceFormatted }}</span>
          </p>
        </div>

        <!-- Title / name -->
        <h3 class="mt-1 text-sm text-gray-800 leading-snug line-clamp-3 break-words">
          {{ toProductTitle(p.nombre) }}
        </h3>

        <!-- Rating -->
        <div v-if="p.total_resenas > 0" class="mt-1 flex items-center gap-1">
          <StarRating :rating="Number(p.rating_promedio)" size="sm" :show-count="false" />
          <span class="text-xs text-slate-500">({{ p.total_resenas }})</span>
        </div>

        <!-- Short description (muted) -->
        <p v-if="p.descripcion_corta" class="mt-0.5 text-xs text-gray-500 line-clamp-2">
          {{ p.descripcion_corta }}
        </p>

        <!-- Color/variant dots or image count -->
        <div class="mt-2 flex items-center gap-2">
          <template v-if="colors.length">
            <span
              v-for="(c, idx) in colors.slice(0,4)"
              :key="idx"
              class="inline-block h-4 w-4 rounded-full border border-gray-300"
              :style="{ backgroundColor: c }"
            ></span>
            <span v-if="colors.length > 4" class="text-[11px] text-gray-500">+{{ colors.length - 4 }}</span>
          </template>
          <template v-else-if="imagenes.length">
            <span v-for="(img, idx) in imagenes.slice(0,4)" :key="idx" class="h-4 w-4 rounded-full bg-gray-200 overflow-hidden border">
              <img :src="img" alt="miniatura" class="h-full w-full object-cover" />
            </span>
            <span v-if="imagenes.length > 4" class="text-[11px] text-gray-500">+{{ imagenes.length - 4 }}</span>
          </template>
        </div>

        <!-- Stock warning -->
        <p v-if="stockLow && !isOutOfStock" class="mt-2 text-xs font-medium text-amber-700">
          Quedan {{ p.stock }} en inventario
        </p>

        <!-- Tier pricing hint -->
        <p v-if="tienePreciosEscalonados" class="mt-1 text-[11px] text-sky-700">
          Precio por volumen disponible
        </p>
      </div>
    </router-link>

    <!-- Add-to-cart floating button -->
    <button
      type="button"
      class="absolute bottom-2 right-2 rounded-full p-2 shadow transition-colors"
      :class="isOutOfStock
        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
        : 'bg-yellow-400 text-gray-900 hover:bg-yellow-500'"
      :disabled="isOutOfStock"
      @click.stop="!isOutOfStock && emit('add-to-cart', producto)"
      :aria-label="isOutOfStock ? 'Producto agotado' : 'Agregar al carrito'"
    >
      <!-- X icon when out of stock -->
      <svg v-if="isOutOfStock" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-5 w-5">
        <path fill-rule="evenodd" d="M5.47 5.47a.75.75 0 0 1 1.06 0L12 10.94l5.47-5.47a.75.75 0 1 1 1.06 1.06L13.06 12l5.47 5.47a.75.75 0 1 1-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 0 1-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
      </svg>
      <!-- Plus icon when available -->
      <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-5 w-5">
        <path fill-rule="evenodd" d="M12 3.75a.75.75 0 0 1 .75.75v6.75H19.5a.75.75 0 0 1 0 1.5h-6.75V19.5a.75.75 0 0 1-1.5 0v-6.75H4.5a.75.75 0 0 1 0-1.5h6.75V4.5a.75.75 0 0 1 .75-.75Z" clip-rule="evenodd" />
      </svg>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useWishlistStore } from '@/stores/wishlist'
import { useAuthStore } from '@/stores/auth'
import { toProductTitle } from '@/utils/text'
import StarRating from '@/components/StarRating.vue'

const emit = defineEmits(['add-to-cart'])
const wishlist = useWishlistStore()
const auth = useAuthStore()

const props = defineProps({
  producto: { type: Object, required: true },
})

// Normalize common fields so the template is simple and robust
const collapseAttributeValues = (buckets) => {
  const normalized = {}
  for (const [name, list] of Object.entries(buckets)) {
    const clean = list.map((v) => (v == null ? '' : String(v).trim())).filter(Boolean)
    if (!clean.length) continue
    normalized[name] = clean.length === 1 ? clean[0] : clean
  }
  return normalized
}

const normalizeAttributes = (detail, fallback = {}) => {
  if (Array.isArray(detail) && detail.length) {
    const buckets = {}
    for (const item of detail) {
      if (!item) continue
      const nombre = String(item?.atributo?.nombre ?? item?.nombre ?? '').trim()
      if (!nombre) continue
      const val = item?.valor ?? item?.value ?? ''
      if (Array.isArray(val)) {
        val.forEach((single) => {
          const normalized = single == null ? '' : String(single).trim()
          if (!normalized) return
          const bucket = buckets[nombre] || (buckets[nombre] = [])
          bucket.push(normalized)
        })
      } else {
        const normalized = val == null ? '' : String(val).trim()
        if (!normalized) continue
        const bucket = buckets[nombre] || (buckets[nombre] = [])
        bucket.push(normalized)
      }
    }
    return collapseAttributeValues(buckets)
  }

  if (typeof fallback === 'object' && fallback && !Array.isArray(fallback)) {
    return collapseAttributeValues(
      Object.entries(fallback).reduce((acc, [name, value]) => {
        if (!name) return acc
        const key = String(name).trim()
        if (!key) return acc
        if (Array.isArray(value)) acc[key] = value
        else if (value != null && value !== '') acc[key] = [value]
        return acc
      }, {})
    )
  }

  return {}
}

const p = computed(() => {
  const pr = props.producto || {}
  const attrDetail = Array.isArray(pr.atributos_detalle) ? pr.atributos_detalle : []
  const attrFallback = pr.atributos ?? pr.Atributos ?? {}
  return {
    id: pr.id,
    nombre: pr.nombre ?? pr.Nombre ?? '',
    descripcion_corta: pr.descripcion_corta ?? pr['Descripcion corta'] ?? pr.descripcionCorta ?? '',
    descripcion_larga: pr.descripcion_larga ?? pr['Descripcion larga'] ?? pr.descripcionLarga ?? '',
    precio_normal: pr.precio_normal ?? pr.precio ?? pr['Precio normal'] ?? pr.PrecioNormal ?? null,
    precio_rebajado: pr.precio_rebajado ?? pr['Precio rebajado'] ?? pr.PrecioRebajado ?? null,
    imagen_principal: pr.imagen_principal ?? pr['Imagen principal'] ?? pr.imagen ?? null,
    estado_inventario: pr.estado_inventario ?? pr['Estado inventario'] ?? pr.estadoInventario ?? '',
    categoria: pr.categoria ?? pr.Categoria ?? '',
    marca: pr.marca ?? pr.Marca ?? '',
    atributos: normalizeAttributes(attrDetail, attrFallback),
    atributos_detalle: attrDetail,
    stock: pr.stock ?? pr.Stock ?? null,
    precios_escalonados: pr.precios_escalonados ?? pr['Precio escalonados'] ?? pr.precios ?? null,
    imagenes: (pr.galeria ?? pr.imagenes ?? pr['Imagen productos'] ?? pr.imagenesProducto ?? []),
  }
})

const placeholder =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"><rect width="100%" height="100%" fill="#f3f4f6"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#9ca3af" font-family="Arial" font-size="18">Sin imagen</text></svg>`
  )

// Media URL resolver: soporta rutas relativas del backend
const MEDIA_BASE = (import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? 'http://localhost:8000' : (typeof window !== 'undefined' ? window.location.origin : ''))).replace(/\/+$/, '')
const toMedia = (u) => {
  if (!u) return null
  if (/^(data:|blob:|https?:)/i.test(u)) return u
  if (u.startsWith('/media/')) return `${MEDIA_BASE}${u}`
  return `${MEDIA_BASE}/media/${u.replace(/^\/+/, '')}`
}

const num = (v) => {
  if (v === undefined || v === null) return null
  if (typeof v === 'number') return Number.isFinite(v) ? v : null
  if (typeof v === 'string') {
    const cleaned = v.replace(/[^0-9.,-]/g, '').replace(',', '.').trim()
    if (cleaned === '') return null
    const n = Number(cleaned)
    return Number.isFinite(n) ? n : null
  }
  return null
}

const listPrice = computed(() => num(p.value.precio_normal))
// Solo considerar rebaja si viene un número válido distinto de vacío
const salePrice = computed(() => num(p.value.precio_rebajado))
// Precio mostrado: rebajado si existe, de lo contrario el normal
const displayPrice = computed(() => (salePrice.value ?? listPrice.value ?? 0))
const hasDiscount = computed(
  () => listPrice.value != null && salePrice.value != null && salePrice.value > 0 && salePrice.value < listPrice.value
)
const discountPct = computed(() => (hasDiscount.value ? Math.round((1 - salePrice.value / listPrice.value) * 100) : 0))

const fmt = (n) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 2 }).format(n ?? 0)

const saleFormatted = computed(() => fmt(displayPrice.value))
const listPriceFormatted = computed(() => (listPrice.value != null ? fmt(listPrice.value) : ''))

const priceMajor = computed(() => {
  const f = saleFormatted.value
  const m = f.match(/^(.*?)([.,](\d{2}))$/)
  return m ? m[1] : f
})
const priceMinor = computed(() => {
  const f = saleFormatted.value
  const m = f.match(/([.,](\d{2}))$/)
  return m ? m[2] : '00'
})

const stockLow = computed(() => Number.isFinite(Number(p.value.stock)) && Number(p.value.stock) > 0 && Number(p.value.stock) < 10)
const isOutOfStock = computed(() => {
  if (p.value.estado_inventario === 'agotado') return true
  const rawStock = p.value.stock
  if (rawStock === null || rawStock === undefined) return false
  const s = Number(rawStock)
  return Number.isFinite(s) && s <= 0
})

const colors = computed(() => {
  const at = p.value.atributos || {}
  const raw = at.color || at.Color || at.colores || at.Colores
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (typeof raw === 'string') return raw.split(',').map((s) => s.trim()).filter(Boolean)
  return []
})

const imagenes = computed(() => {
  const imgs = p.value.imagenes
  if (!Array.isArray(imgs)) return []
  const out = []
  for (const it of imgs) {
    const u = typeof it === 'string' ? it : it?.imagen || it?.url || it?.image || it?.src
    const full = toMedia(u)
    if (full) out.push(full)
  }
  return out
})

const imgSrc = computed(() => toMedia(p.value.imagen_principal) || imagenes.value[0] || placeholder)

const tienePreciosEscalonados = computed(() => {
  const pe = p.value.precios_escalonados
  return Array.isArray(pe) ? pe.length > 0 : !!pe
})

const productoId = computed(() => p.value.id ?? props.producto?.id)
const isFavorito = computed(() => auth.isAuthenticated && wishlist.esFavorito(productoId.value))

const toggleFav = async () => {
  if (!auth.isAuthenticated) {
    // Redirect to login could be handled here, for now just return
    return
  }
  await wishlist.toggle(productoId.value)
}
</script>
