<template>
  <main class="min-h-screen bg-slate-50 dark:bg-slate-900 px-4 py-8">
    <div class="mx-auto max-w-5xl space-y-6">

      <!-- Breadcrumb -->
      <nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
        <RouterLink to="/mi-cuenta" class="hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors">Mi cuenta</RouterLink>
        <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
        </svg>
        <span class="text-slate-700 dark:text-slate-300 font-medium">Mis direcciones</span>
      </nav>

      <h1 class="text-3xl font-bold text-slate-900 dark:text-slate-100">Mis direcciones</h1>

      <!-- Cargando -->
      <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="n in 3" :key="n" class="h-52 rounded-2xl bg-slate-200 dark:bg-slate-700 animate-pulse" />
      </div>

      <!-- Grid de tarjetas -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 items-start">

        <!-- Tarjeta: Agregar dirección -->
        <button
          @click="nueva"
          class="flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 p-10 text-slate-500 dark:text-slate-400 hover:border-emerald-400 hover:text-emerald-600 dark:hover:border-emerald-500 dark:hover:text-emerald-400 transition-colors group min-h-[180px] w-full"
        >
          <span class="text-4xl font-light leading-none group-hover:scale-110 transition-transform">+</span>
          <span class="text-base font-medium">Agregar dirección</span>
        </button>

        <!-- Tarjetas de direcciones -->
        <div
          v-for="dir in direcciones"
          :key="dir.id"
          class="relative rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm flex flex-col gap-3 min-h-[180px]"
        >
          <!-- Badge predeterminada -->
          <div v-if="dir.predeterminada" class="text-xs text-slate-500 dark:text-slate-400">
            <span class="font-semibold">Predeterminado:</span>
            <span class="ml-1 text-slate-700 dark:text-slate-300">{{ dir.nombre }} {{ dir.apellidos }}</span>
          </div>

          <!-- Contenido dirección -->
          <div class="flex-1 text-sm text-slate-700 dark:text-slate-300 leading-relaxed space-y-0.5">
            <p class="font-bold text-slate-900 dark:text-slate-100">{{ dir.nombre }} {{ dir.apellidos }}</p>
            <p>{{ dir.calle }} {{ dir.numero_exterior }}<template v-if="dir.numero_interior"> Int. {{ dir.numero_interior }}</template></p>
            <p v-if="dir.colonia" class="uppercase text-xs font-medium tracking-wide text-slate-500 dark:text-slate-400">{{ dir.colonia }}</p>
            <p>{{ dir.ciudad }}, {{ dir.estado }}</p>
            <p>{{ dir.codigo_postal }}</p>
            <p>{{ dir.pais }}</p>
            <p v-if="dir.telefono" class="pt-1 text-slate-600 dark:text-slate-400">
              Número de teléfono: {{ dir.telefono }}
            </p>
            <p v-if="dir.referencias" class="text-xs text-slate-500 dark:text-slate-500 pt-1 italic">
              {{ dir.referencias }}
            </p>
          </div>

          <!-- Acciones -->
          <div class="pt-2 border-t border-slate-100 dark:border-slate-700 text-sm flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <button
                class="text-emerald-600 dark:text-emerald-400 hover:underline font-medium"
                @click="editar(dir)"
              >Editar</button>
              <span class="text-slate-300 dark:text-slate-600">|</span>
              <button
                class="text-emerald-600 dark:text-emerald-400 hover:underline font-medium"
                @click="confirmarBorrar(dir)"
              >Descartar</button>
            </div>
            <button
              v-if="!dir.predeterminada"
              class="text-left text-emerald-600 dark:text-emerald-400 hover:underline font-medium flex items-center gap-1"
              @click="establecerPredeterminada(dir)"
            >
              <svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              Establecer como predeterminado
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Modal formulario ─── -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="show = false" />
          <div class="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-white dark:bg-slate-800 shadow-xl">

            <div class="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 px-6 py-4">
              <h2 class="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {{ editingId ? 'Editar dirección' : 'Nueva dirección' }}
              </h2>
              <button @click="show = false" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form @submit.prevent="guardar" class="p-6 space-y-5" :key="formKey">

              <fieldset class="space-y-3">
                <legend class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Datos de contacto</legend>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label :class="labelClass">Nombre *</label>
                    <input v-model="form.nombre" type="text" placeholder="Nombre" required :class="inputClass" />
                  </div>
                  <div>
                    <label :class="labelClass">Apellidos *</label>
                    <input v-model="form.apellidos" type="text" placeholder="Apellidos" required :class="inputClass" />
                  </div>
                  <div class="sm:col-span-2">
                    <label :class="labelClass">Correo electrónico</label>
                    <input v-model="form.email" type="email" placeholder="correo@ejemplo.com" :class="inputClass" />
                  </div>
                  <div>
                    <label :class="labelClass">Teléfono</label>
                    <input v-model="form.telefono" type="tel" placeholder="55 1234 5678" :class="inputClass" />
                  </div>
                  <div>
                    <label :class="labelClass">Empresa</label>
                    <input v-model="form.nombre_empresa" type="text" placeholder="Opcional" :class="inputClass" />
                  </div>
                </div>
              </fieldset>

              <fieldset class="space-y-3">
                <legend class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Dirección</legend>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">

                  <!-- Código postal -->
                  <div>
                    <label :class="labelClass">Código postal *</label>
                    <div class="relative">
                      <input
                        v-model="form.codigo_postal"
                        type="text"
                        inputmode="numeric"
                        maxlength="5"
                        placeholder="Ej. 06600"
                        required
                        :class="[inputClass, 'pr-9']"
                        @input="onCpInput"
                      />
                      <div v-if="cpCargando" class="absolute right-3 top-1/2 -translate-y-1/2">
                        <svg class="h-4 w-4 animate-spin text-slate-400" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                        </svg>
                      </div>
                      <svg v-else-if="cpOk" class="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <p v-if="cpError" class="mt-1 text-xs text-red-500">{{ cpError }}</p>
                    <p v-else-if="cpOk" class="mt-1 text-xs text-emerald-600 dark:text-emerald-400">Datos autocompletados ✓</p>
                  </div>

                  <!-- Colonia -->
                  <div>
                    <label :class="labelClass">Colonia *</label>
                    <select v-if="colonias.length > 0" v-model="form.colonia" required :class="inputClass">
                      <option value="" disabled>Selecciona una colonia</option>
                      <option v-for="c in colonias" :key="c" :value="c">{{ c }}</option>
                    </select>
                    <input v-else v-model="form.colonia" type="text" placeholder="Colonia" required :class="inputClass" />
                  </div>

                  <div>
                    <label :class="labelClass">Ciudad / Municipio *</label>
                    <input v-model="form.ciudad" type="text" placeholder="Ciudad" required :class="inputClass" />
                  </div>
                  <div>
                    <label :class="labelClass">Estado *</label>
                    <input v-model="form.estado" type="text" placeholder="Estado" required :class="inputClass" />
                  </div>
                  <div>
                    <label :class="labelClass">País</label>
                    <input v-model="form.pais" type="text" placeholder="México" :class="inputClass" />
                  </div>
                  <div>
                    <label :class="labelClass">Calle *</label>
                    <input v-model="form.calle" type="text" placeholder="Nombre de la calle" required :class="inputClass" />
                  </div>
                  <div>
                    <label :class="labelClass">No. exterior *</label>
                    <input v-model="form.numero_exterior" type="text" placeholder="123" required :class="inputClass" />
                  </div>
                  <div>
                    <label :class="labelClass">No. interior</label>
                    <input v-model="form.numero_interior" type="text" placeholder="Depto. 4B (opcional)" :class="inputClass" />
                  </div>
                  <div class="sm:col-span-2">
                    <label :class="labelClass">Referencias</label>
                    <textarea v-model="form.referencias" rows="2" placeholder="Entre calles, color de fachada…" :class="inputClass" />
                  </div>
                </div>
              </fieldset>

              <label class="flex items-center gap-2.5 cursor-pointer">
                <input type="checkbox" v-model="form.predeterminada" class="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" />
                <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Usar como dirección predeterminada</span>
              </label>

              <div v-if="guardadoError" class="rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-400">
                {{ guardadoError }}
              </div>

              <div class="flex gap-3 pt-2">
                <button
                  type="submit"
                  :disabled="guardando"
                  class="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors"
                >
                  <svg v-if="guardando" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                  </svg>
                  {{ guardando ? 'Guardando…' : (editingId ? 'Guardar cambios' : 'Agregar dirección') }}
                </button>
                <button
                  type="button"
                  class="rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-5 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors"
                  @click="show = false"
                >Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ─── Modal confirmación borrar ─── -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="confirmDir" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="confirmDir = null" />
          <div class="relative w-full max-w-sm rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-xl space-y-4">
            <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">¿Descartar esta dirección?</h3>
            <p class="text-sm text-slate-600 dark:text-slate-400">
              {{ confirmDir.calle }} {{ confirmDir.numero_exterior }}, {{ confirmDir.ciudad }}
            </p>
            <div class="flex gap-3">
              <button
                class="flex-1 rounded-xl bg-red-600 hover:bg-red-700 px-4 py-2.5 text-sm font-semibold text-white transition-colors"
                @click="borrar(confirmDir.id)"
              >Descartar</button>
              <button
                class="flex-1 rounded-xl border border-slate-200 dark:border-slate-600 px-4 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                @click="confirmDir = null"
              >Cancelar</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { obtenerDirecciones, crearDireccion, actualizarDireccion, eliminarDireccion } from '@/services/account'

const labelClass = 'block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1.5'
const inputClass = 'w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition'

const direcciones   = ref([])
const form          = ref({})
const editingId     = ref(null)
const show          = ref(false)
const formKey       = ref(0)
const cargando      = ref(false)
const guardando     = ref(false)
const guardadoError = ref('')
const confirmDir    = ref(null)

// Código postal
const colonias   = ref([])
const cpCargando = ref(false)
const cpOk       = ref(false)
const cpError    = ref('')
let   cpTimer    = null

const blank = () => ({
  nombre: '', apellidos: '', email: '', nombre_empresa: '',
  calle: '', numero_exterior: '', numero_interior: '',
  colonia: '', ciudad: '', pais: 'México', estado: '',
  codigo_postal: '', telefono: '', referencias: '',
  predeterminada: false,
})

const cargar = async () => {
  cargando.value = true
  try {
    const r = await obtenerDirecciones()
    direcciones.value = r.data.direcciones ?? r.data ?? []
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

const nueva = () => {
  editingId.value = null
  form.value = blank()
  colonias.value = []
  cpOk.value = false
  cpError.value = ''
  guardadoError.value = ''
  show.value = true
  formKey.value++
}

const editar = (d) => {
  editingId.value = d.id
  form.value = JSON.parse(JSON.stringify({ ...blank(), ...d }))
  colonias.value = []
  cpOk.value = false
  cpError.value = ''
  guardadoError.value = ''
  show.value = true
  formKey.value++
}

const guardar = async () => {
  guardadoError.value = ''
  guardando.value = true
  try {
    if (editingId.value) {
      await actualizarDireccion(editingId.value, form.value)
    } else {
      await crearDireccion(form.value)
    }
    show.value = false
    await cargar()
  } catch (e) {
    const data = e?.response?.data
    guardadoError.value = data && typeof data === 'object'
      ? Object.values(data).flat().join(' ')
      : 'Error al guardar la dirección.'
  } finally {
    guardando.value = false
  }
}

const establecerPredeterminada = async (dir) => {
  await actualizarDireccion(dir.id, { ...dir, predeterminada: true })
  await cargar()
}

const confirmarBorrar = (dir) => { confirmDir.value = dir }

const borrar = async (id) => {
  confirmDir.value = null
  await eliminarDireccion(id)
  await cargar()
}

// ─── Autocompletado por Código Postal ───
const onCpInput = () => {
  cpOk.value = false
  cpError.value = ''
  colonias.value = []
  clearTimeout(cpTimer)
  const cp = form.value.codigo_postal?.replace(/\D/g, '').slice(0, 5)
  form.value.codigo_postal = cp
  if (cp.length === 5) {
    cpTimer = setTimeout(() => buscarCp(cp), 500)
  }
}

const buscarCp = async (cp) => {
  cpCargando.value = true
  cpError.value = ''
  try {
    const res = await fetch(`https://api.copomex.com/query/info_cp/${cp}?type=simplified&token=pruebas`)
    const data = await res.json()
    const registros = Array.isArray(data) ? data : (data.error ? [] : [data])
    if (registros.length === 0 || registros[0]?.error) {
      cpError.value = 'Código postal no encontrado'
      return
    }
    form.value.estado = registros[0].estado ?? form.value.estado
    form.value.ciudad = registros[0].municipio ?? form.value.ciudad
    colonias.value = [...new Set(registros.map(r => r.asentamiento).filter(Boolean))]
    if (colonias.value.length === 1) form.value.colonia = colonias.value[0]
    cpOk.value = true
  } catch {
    cpError.value = 'No se pudo verificar el código postal'
  } finally {
    cpCargando.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
