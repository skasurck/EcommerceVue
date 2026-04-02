<template>
  <section class="mt-10">
    <h2 class="text-xl font-semibold text-slate-800 mb-1">Reseñas del producto</h2>

    <!-- Resumen de rating -->
    <div class="flex flex-col sm:flex-row gap-6 items-start sm:items-center mb-6">
      <div class="text-center">
        <div class="text-5xl font-bold text-slate-800">{{ ratingDisplay }}</div>
        <StarRating :rating="Number(props.ratingPromedio)" size="md" :show-count="false" class="justify-center mt-1" />
        <div class="text-sm text-slate-500 mt-1">{{ props.totalResenas }} reseña{{ props.totalResenas !== 1 ? 's' : '' }}</div>
      </div>
      <!-- Barras por estrella -->
      <div class="flex-1 space-y-1 w-full max-w-xs">
        <div v-for="n in [5,4,3,2,1]" :key="n" class="flex items-center gap-2 text-sm">
          <span class="w-3 text-slate-600">{{ n }}</span>
          <svg class="h-3.5 w-3.5 text-amber-400 shrink-0" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.958a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.448a1 1 0 00-.364 1.118l1.287 3.957c.3.922-.755 1.688-1.54 1.118l-3.37-2.447a1 1 0 00-1.175 0l-3.37 2.447c-.784.57-1.838-.196-1.54-1.118l1.287-3.957a1 1 0 00-.364-1.118L2.063 9.385c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69L9.049 2.927z"/>
          </svg>
          <div class="flex-1 bg-slate-200 rounded-full h-2 overflow-hidden">
            <div class="bg-amber-400 h-2 rounded-full transition-all duration-500" :style="{ width: porcentajePorEstrella(n) + '%' }"></div>
          </div>
          <span class="w-6 text-right text-slate-500">{{ conteoEstrella(n) }}</span>
        </div>
      </div>
    </div>

    <!-- Formulario nueva reseña -->
    <div v-if="auth.isAuthenticated && !miResena" class="bg-slate-50 border rounded-xl p-4 mb-6">
      <h3 class="font-semibold text-slate-700 mb-3">Escribe tu reseña</h3>
      <div class="mb-3">
        <label class="block text-sm text-slate-600 mb-1">Calificación</label>
        <StarRating interactive v-model="form.calificacion" size="lg" />
      </div>
      <div class="mb-3">
        <label class="block text-sm text-slate-600 mb-1">Comentario <span class="text-slate-400">(opcional)</span></label>
        <textarea
          v-model="form.comentario"
          rows="3"
          class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          placeholder="¿Qué te pareció el producto?"
        ></textarea>
      </div>
      <p v-if="formError" class="text-sm text-rose-600 mb-2">{{ formError }}</p>
      <button
        @click="enviarResena"
        :disabled="!form.calificacion || enviando"
        class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium"
      >
        {{ enviando ? 'Enviando…' : 'Publicar reseña' }}
      </button>
    </div>

    <!-- Mi reseña existente -->
    <div v-if="miResena" class="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
      <div class="flex items-center justify-between mb-1">
        <div class="flex items-center gap-2">
          <span class="text-sm font-semibold text-blue-800">Tu reseña</span>
          <span v-if="!miResena.aprobada" class="text-xs bg-amber-100 text-amber-700 border border-amber-200 px-1.5 py-0.5 rounded-full">
            Pendiente de aprobación
          </span>
        </div>
        <button @click="eliminarMiResena" class="text-xs text-rose-500 hover:text-rose-700">Eliminar</button>
      </div>
      <StarRating :rating="miResena.calificacion" size="sm" :show-count="false" />
      <p v-if="miResena.comentario" class="text-sm text-slate-700 mt-1">{{ miResena.comentario }}</p>
    </div>

    <!-- Sin sesión -->
    <div v-if="!auth.isAuthenticated" class="bg-slate-50 border rounded-xl p-4 mb-6 text-sm text-slate-600">
      <RouterLink to="/login" class="text-blue-600 hover:underline font-medium">Inicia sesión</RouterLink>
      para dejar tu reseña.
    </div>

    <!-- Lista de reseñas -->
    <div v-if="resenas.length" class="space-y-4">
      <div
        v-for="r in resenas"
        :key="r.id"
        class="border rounded-xl p-4 bg-white"
      >
        <div class="flex items-start justify-between gap-2 mb-1">
          <div>
            <span class="font-medium text-slate-800 text-sm">{{ r.usuario_nombre }}</span>
            <span v-if="r.verificado" class="ml-2 text-xs bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded">Compra verificada</span>
          </div>
          <span class="text-xs text-slate-400 whitespace-nowrap">{{ formatFecha(r.creado) }}</span>
        </div>
        <StarRating :rating="r.calificacion" size="sm" :show-count="false" />
        <p v-if="r.comentario" class="text-sm text-slate-700 mt-1">{{ r.comentario }}</p>
      </div>
    </div>

    <div v-else-if="!cargando" class="text-sm text-slate-500 text-center py-6">
      Aún no hay reseñas. ¡Sé el primero!
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import StarRating from './StarRating.vue'
import axios from '@/axios'
import { useAuthStore } from '@/stores/auth'
import { formatFecha } from '@/utils/formatters'

const props = defineProps({
  productoId: { type: Number, required: true },
  ratingPromedio: { type: [Number, String], default: 0 },
  totalResenas: { type: Number, default: 0 },
})

const emit = defineEmits(['rating-updated'])

const auth = useAuthStore()
const resenas = ref([])
const cargando = ref(false)
const enviando = ref(false)
const formError = ref('')
const form = ref({ calificacion: 0, comentario: '' })

const miResena = computed(() => resenas.value.find(r => r.mi_resena))

const ratingDisplay = computed(() => {
  const n = Number(props.ratingPromedio)
  return n ? n.toFixed(1) : '–'
})

function conteoEstrella(n) {
  return resenas.value.filter(r => r.calificacion === n).length
}

function porcentajePorEstrella(n) {
  if (!resenas.value.length) return 0
  return Math.round((conteoEstrella(n) / resenas.value.length) * 100)
}

async function cargarResenas() {
  cargando.value = true
  try {
    const res = await axios.get(`resenas/?producto=${props.productoId}`)
    resenas.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } finally {
    cargando.value = false
  }
}

async function enviarResena() {
  if (!form.value.calificacion) return
  enviando.value = true
  formError.value = ''
  try {
    await axios.post('resenas/', {
      producto: props.productoId,
      calificacion: form.value.calificacion,
      comentario: form.value.comentario,
    })
    form.value = { calificacion: 0, comentario: '' }
    await cargarResenas()
    emit('rating-updated')
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Error al publicar la reseña.'
  } finally {
    enviando.value = false
  }
}

async function eliminarMiResena() {
  if (!confirm('¿Eliminar tu reseña?')) return
  await axios.delete(`resenas/${miResena.value.id}/`)
  await cargarResenas()
  emit('rating-updated')
}

onMounted(cargarResenas)
</script>
