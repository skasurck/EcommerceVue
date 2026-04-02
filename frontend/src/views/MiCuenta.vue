<template>
  <main class="min-h-screen bg-slate-50 dark:bg-slate-900 px-4 py-8">
    <div class="mx-auto max-w-4xl space-y-6">

      <!-- Header -->
      <header class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6 shadow-sm">
        <div class="flex flex-col sm:flex-row items-center sm:items-start gap-5">
          <!-- Avatar -->
          <div class="relative shrink-0 cursor-pointer group" @click="fileInput.click()">
            <img
              :src="fotoUrl"
              alt="Foto de perfil"
              class="w-24 h-24 rounded-full object-cover ring-4 ring-white dark:ring-slate-700 shadow"
            />
            <div class="absolute inset-0 flex items-center justify-center rounded-full bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity">
              <span class="text-white text-xs font-semibold">Cambiar</span>
            </div>
            <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFotoChange" />
          </div>

          <!-- Nombre + form -->
          <div class="flex-1 w-full">
            <h1 class="text-2xl font-bold text-slate-900 dark:text-slate-100 text-center sm:text-left">
              {{ perfil.first_name || 'Mi cuenta' }}
              {{ perfil.last_name }}
            </h1>
            <p class="text-sm text-slate-500 dark:text-slate-400 text-center sm:text-left mb-4">{{ perfil.email }}</p>

            <form @submit.prevent="guardarPerfil" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1">Nombre</label>
                <input v-model="perfil.first_name" type="text" placeholder="Tu nombre" :class="inputClass" />
              </div>
              <div>
                <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1">Apellidos</label>
                <input v-model="perfil.last_name" type="text" placeholder="Tus apellidos" :class="inputClass" />
              </div>
              <div class="sm:col-span-2">
                <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1">Correo electrónico</label>
                <input v-model="perfil.email" type="email" placeholder="correo@ejemplo.com" :class="inputClass" />
              </div>
              <div>
                <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1">Teléfono</label>
                <input v-model="perfil.perfil.telefono" type="tel" placeholder="55 1234 5678" :class="inputClass" />
              </div>
              <div>
                <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1">Empresa</label>
                <input v-model="perfil.perfil.empresa" type="text" placeholder="Nombre de empresa" :class="inputClass" />
              </div>

              <div class="sm:col-span-2 flex items-center gap-3 pt-1">
                <button type="submit" :disabled="guardando" class="inline-flex items-center gap-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors">
                  <svg v-if="guardando" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                  </svg>
                  {{ guardando ? 'Guardando…' : 'Guardar cambios' }}
                </button>
                <span v-if="guardadoOk" class="text-sm text-emerald-600 dark:text-emerald-400 font-medium">✓ Guardado</span>
              </div>
            </form>
          </div>
        </div>
      </header>

      <!-- Accesos rápidos -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <AccountTile
          title="Mis pedidos"
          desc="Rastrea o consulta pedidos anteriores"
          icon="mdi:package-variant-closed"
          to="/mis-pedidos"
        />
        <AccountTile
          title="Seguridad"
          desc="Cambia tu contraseña"
          icon="mdi:shield-lock-outline"
          to="/seguridad"
        />
        <AccountTile
          title="Direcciones"
          desc="Gestiona tus direcciones de envío"
          icon="mdi:home-map-marker"
          to="/direcciones"
        />
      </div>

      <!-- ── Califica tus compras (solo si hay productos pendientes) ── -->
      <RouterLink
        v-if="pedidosParaCalificar.length"
        to="/mis-pedidos"
        class="block rounded-2xl border-2 border-amber-400 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/20 dark:border-amber-600 p-6 shadow-sm hover:shadow-md transition-shadow group"
      >
        <div class="flex items-center gap-5">
          <!-- Icono animado -->
          <div class="shrink-0 flex h-16 w-16 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-900/40 border-2 border-amber-300 dark:border-amber-700 group-hover:scale-105 transition-transform">
            <span class="text-3xl">⭐</span>
          </div>

          <div class="flex-1 min-w-0">
            <h2 class="text-lg font-bold text-amber-900 dark:text-amber-200">¡Califica tu compra!</h2>
            <p class="text-sm text-amber-700 dark:text-amber-400 mt-0.5">
              Tienes
              <span class="font-semibold">{{ totalProductosPorCalificar }} producto{{ totalProductosPorCalificar !== 1 ? 's' : '' }}</span>
              sin calificar. Tu opinión ayuda a otros compradores.
            </p>
            <!-- Mini vista previa de productos -->
            <div class="mt-3 flex items-center gap-2 flex-wrap">
              <img
                v-for="(img, i) in previewImagenes"
                :key="i"
                :src="img"
                class="h-10 w-10 rounded-lg object-cover border-2 border-white dark:border-slate-700 shadow-sm"
              />
              <span v-if="totalProductosPorCalificar > previewImagenes.length"
                class="text-xs text-amber-600 dark:text-amber-400 font-medium">
                +{{ totalProductosPorCalificar - previewImagenes.length }} más
              </span>
            </div>
          </div>

          <!-- Flecha -->
          <svg class="h-6 w-6 text-amber-500 shrink-0 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
          </svg>
        </div>
      </RouterLink>

      <!-- Cerrar sesión -->
      <div class="pt-2">
        <button
          type="button"
          @click="cerrarSesion"
          class="inline-flex items-center gap-2 rounded-xl border border-red-200 dark:border-red-900 bg-white dark:bg-slate-800 px-5 py-2.5 text-sm font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 hover:border-red-300 transition-colors"
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9"/>
          </svg>
          Cerrar sesión
        </button>
      </div>

    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import AccountTile from '@/components/AccountTile.vue'
import placeholderImg from '@/assets/profile-placeholder.svg'
import { obtenerPerfil, actualizarPerfil, subirFotoPerfil, obtenerPedidos } from '@/services/account'
import { useAuthStore } from '@/stores/auth'
import axios from '@/axios'

const auth = useAuthStore()
const router = useRouter()

const perfil = ref({ perfil: { telefono: '', empresa: '' } })
const fotoUrl = ref(placeholderImg)
const fileInput = ref(null)
const guardando = ref(false)
const guardadoOk = ref(false)

// ── Productos sin calificar ──
const pedidosParaCalificar = ref([])   // pedidos que tienen items sin reseña
const productosParaCalificar = ref([]) // lista plana de items sin reseña

const totalProductosPorCalificar = computed(() => productosParaCalificar.value.length)

const previewImagenes = computed(() =>
  productosParaCalificar.value
    .map(it => it.producto_imagen)
    .filter(Boolean)
    .slice(0, 5)
)

const ESTADOS_CALIFICABLES = ['pagado', 'confirmado', 'enviado', 'entregado']

async function detectarProductosSinCalificar() {
  try {
    // 1. Traer pedidos elegibles (máx 20 para no sobrecargar)
    const { data } = await obtenerPedidos({ page: 1, page_size: 20 })
    const lista = Array.isArray(data) ? data : (data.results ?? [])
    const elegibles = lista.filter(p => ESTADOS_CALIFICABLES.includes(p.estado))
    if (!elegibles.length) return

    // 2. Recopilar IDs únicos de productos
    const allItems = elegibles.flatMap(p => p.detalles ?? [])
    const productoIds = [...new Set(allItems.map(it => it.producto).filter(Boolean))]
    if (!productoIds.length) return

    // 3. Traer reseñas propias del usuario para esos productos
    const res = await axios.get(`resenas/?productos=${productoIds.join(',')}&mias=1`)
    const misResenas = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
    const resenadoIds = new Set(misResenas.map(r => r.producto))

    // 4. Filtrar items sin reseña (únicos por productoId)
    const vistos = new Set()
    const sinCalificar = []
    for (const it of allItems) {
      if (it.producto && !resenadoIds.has(it.producto) && !vistos.has(it.producto)) {
        vistos.add(it.producto)
        sinCalificar.push(it)
      }
    }

    productosParaCalificar.value = sinCalificar
    pedidosParaCalificar.value = elegibles.filter(p =>
      (p.detalles ?? []).some(it => it.producto && !resenadoIds.has(it.producto))
    )
  } catch { /* silencioso */ }
}

const inputClass = 'w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition'

const cerrarSesion = () => {
  auth.logout()
  router.push('/')
}

const cargarDatos = async () => {
  const { data } = await obtenerPerfil()
  perfil.value = data
  perfil.value.perfil = perfil.value.perfil || { telefono: '', empresa: '' }
  fotoUrl.value = data.foto_url || placeholderImg
}

const guardarPerfil = async () => {
  guardando.value = true
  guardadoOk.value = false
  try {
    await actualizarPerfil(perfil.value)
    guardadoOk.value = true
    setTimeout(() => { guardadoOk.value = false }, 3000)
  } finally {
    guardando.value = false
  }
}

const onFotoChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const { data } = await subirFotoPerfil(file)
  fotoUrl.value = data.foto_url
}

onMounted(() => {
  cargarDatos()
  detectarProductosSinCalificar()
})
</script>
