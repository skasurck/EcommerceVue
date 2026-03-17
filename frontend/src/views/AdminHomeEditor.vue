<template>
  <div class="max-w-6xl mx-auto space-y-6">
    <header class="flex flex-col gap-2">
      <h1 class="text-2xl font-bold text-slate-900">Editar página principal</h1>
      <p class="text-sm text-slate-600">
        Gestiona las imágenes del slider del Home. Solo administradores pueden realizar cambios.
      </p>
    </header>

    <section class="bg-white border border-slate-200 rounded-lg p-4 shadow-sm space-y-3">
      <h2 class="text-lg font-semibold text-slate-800">Agregar imágenes</h2>
      <div class="flex flex-col sm:flex-row gap-3 sm:items-center">
        <label class="inline-flex items-center justify-center rounded-md bg-slate-900 hover:bg-slate-800 px-4 py-2 text-sm font-medium text-white cursor-pointer w-fit">
          Seleccionar imágenes
          <input
            class="hidden"
            type="file"
            accept="image/*"
            multiple
            @change="handleUpload"
          />
        </label>
        <span class="text-sm text-slate-500">Puedes subir varias imágenes a la vez.</span>
      </div>
      <p v-if="uploading" class="text-sm text-blue-700">Subiendo imágenes...</p>
      <p v-if="feedback" class="text-sm text-emerald-700">{{ feedback }}</p>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
    </section>

    <section class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
      <div class="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-slate-800">Slides guardados</h2>
        <button
          class="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
          type="button"
          @click="fetchSlides"
        >
          Recargar
        </button>
      </div>

      <div v-if="loading" class="p-4 text-sm text-slate-500">Cargando slider...</div>
      <div v-else-if="slides.length === 0" class="p-4 text-sm text-slate-500">
        No hay imágenes guardadas todavía.
      </div>

      <div v-else class="divide-y divide-slate-200">
        <article
          v-for="slide in slides"
          :key="slide.id"
          class="p-4 grid grid-cols-1 lg:grid-cols-[13rem_1fr] gap-4"
        >
          <img
            :src="slide.imagen_url"
            :alt="slide.titulo || `Slide ${slide.id}`"
            class="w-full h-40 object-cover rounded border border-slate-200"
          />

          <div class="space-y-3">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <label class="text-sm text-slate-700">
                Título desktop
                <input
                  v-model="slide.titulo"
                  type="text"
                  class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5"
                  placeholder="Título del slide"
                />
              </label>
              <label class="text-sm text-slate-700">
                Orden
                <input
                  v-model.number="slide.orden"
                  type="number"
                  min="0"
                  class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5"
                />
              </label>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <label class="text-sm text-slate-700 block">
                Descripción desktop
                <input
                  v-model="slide.descripcion"
                  type="text"
                  class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5"
                  placeholder="Descripción desktop"
                />
              </label>
              <label class="text-sm text-slate-700 block">
                Título móvil
                <input
                  v-model="slide.titulo_mobile"
                  type="text"
                  class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5"
                  placeholder="Título para mobile"
                />
              </label>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="text-sm text-slate-700">
                <p class="mb-1">Color del título</p>
                <div class="flex flex-wrap items-center gap-2">
                  <button
                    v-for="color in titleColorPalette"
                    :key="`${slide.id}-${color}`"
                    type="button"
                    class="hex-color-btn"
                    :style="{ backgroundColor: color }"
                    :title="color"
                    @click="slide.titulo_color = color"
                  />
                </div>
              </div>
              <label class="text-sm text-slate-700 block">
                Código HEX
                <input
                  v-model="slide.titulo_color"
                  type="text"
                  maxlength="7"
                  placeholder="#ea580c"
                  class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5"
                />
              </label>
            </div>

            <label class="text-sm text-slate-700 block">
              Descripción móvil
              <input
                v-model="slide.descripcion_mobile"
                type="text"
                class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5"
                placeholder="Descripción para mobile"
              />
            </label>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <label class="text-sm text-slate-700 block">
                Reemplazar imagen desktop
                <input
                  type="file"
                  accept="image/*"
                  class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
                  @change="handleDesktopImageChange(slide, $event)"
                />
              </label>
              <label class="text-sm text-slate-700 block">
                Reemplazar imagen móvil
                <input
                  type="file"
                  accept="image/*"
                  class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
                  @change="handleMobileImageChange(slide, $event)"
                />
              </label>
            </div>

            <div v-if="slide.imagen_mobile_url" class="text-xs text-slate-500">
              <p class="mb-1">Vista previa móvil:</p>
              <img
                :src="slide.imagen_mobile_url"
                :alt="slide.titulo_mobile || `Slide móvil ${slide.id}`"
                class="w-28 h-20 object-cover rounded border border-slate-200"
              />
            </div>

            <label class="inline-flex items-center gap-2 text-sm text-slate-700">
              <input v-model="slide.activo" type="checkbox" />
              Activo
            </label>

            <div class="flex flex-wrap gap-2">
              <button
                type="button"
                class="rounded bg-emerald-600 hover:bg-emerald-700 px-3 py-1.5 text-sm text-white"
                @click="saveSlide(slide)"
              >
                Guardar cambios
              </button>
              <button
                type="button"
                class="rounded bg-rose-600 hover:bg-rose-700 px-3 py-1.5 text-sm text-white"
                @click="deleteSlide(slide.id)"
              >
                Eliminar
              </button>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { obtenerHomeSlider, crearHomeSlide, actualizarHomeSlide, eliminarHomeSlide } from '@/services/api'

defineOptions({ name: 'AdminHomeEditor' })

const slides = ref([])
const loading = ref(false)
const uploading = ref(false)
const error = ref('')
const feedback = ref('')
const titleColorPalette = ['#ea580c', '#dc2626', '#2563eb', '#0891b2', '#16a34a', '#a16207', '#7c3aed', '#111827']

const clearMessages = () => {
  error.value = ''
  feedback.value = ''
}

const fetchSlides = async () => {
  loading.value = true
  clearMessages()
  try {
    const { data } = await obtenerHomeSlider({ include_inactive: 1, ordering: 'orden' })
    slides.value = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
  } catch (err) {
    error.value = 'No se pudieron cargar las imágenes del slider.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const buildSlideFormData = (slide) => {
  const fd = new FormData()
  fd.append('titulo', slide.titulo ?? '')
  fd.append('descripcion', slide.descripcion ?? '')
  const safeHex = /^#[0-9A-Fa-f]{6}$/.test(slide.titulo_color || '') ? slide.titulo_color : '#ea580c'
  fd.append('titulo_color', safeHex)
  fd.append('titulo_mobile', slide.titulo_mobile ?? '')
  fd.append('descripcion_mobile', slide.descripcion_mobile ?? '')
  fd.append('orden', String(Number(slide.orden) || 0))
  fd.append('activo', slide.activo ? 'true' : 'false')
  if (slide.newDesktopImageFile instanceof File) {
    fd.append('imagen', slide.newDesktopImageFile)
  }
  if (slide.newMobileImageFile instanceof File) {
    fd.append('imagen_mobile', slide.newMobileImageFile)
  }
  return fd
}

const handleDesktopImageChange = (slide, event) => {
  const file = event.target.files?.[0]
  if (!file) return
  slide.newDesktopImageFile = file
}

const handleMobileImageChange = (slide, event) => {
  const file = event.target.files?.[0]
  if (!file) return
  slide.newMobileImageFile = file
}

const handleUpload = async (event) => {
  const files = Array.from(event.target.files || [])
  if (!files.length) return

  uploading.value = true
  clearMessages()
  try {
    const currentMaxOrder = slides.value.reduce((max, item) => Math.max(max, Number(item.orden) || 0), 0)
    await Promise.all(
      files.map((file, index) => {
        const fd = new FormData()
        fd.append('imagen', file)
        fd.append('titulo', file.name.replace(/\.[^/.]+$/, ''))
        fd.append('descripcion', '')
        fd.append('titulo_color', '#ea580c')
        fd.append('orden', String(currentMaxOrder + index + 1))
        fd.append('activo', 'true')
        return crearHomeSlide(fd)
      }),
    )
    feedback.value = `Se guardaron ${files.length} imagen(es) en el slider.`
    await fetchSlides()
  } catch (err) {
    error.value = 'No se pudieron subir todas las imágenes.'
    console.error(err)
  } finally {
    uploading.value = false
    event.target.value = ''
  }
}

const saveSlide = async (slide) => {
  clearMessages()
  try {
    const fd = buildSlideFormData(slide)
    await actualizarHomeSlide(slide.id, fd)
    feedback.value = `Slide #${slide.id} actualizado.`
    await fetchSlides()
  } catch (err) {
    error.value = `No se pudo actualizar el slide #${slide.id}.`
    console.error(err)
  }
}

const deleteSlide = async (slideId) => {
  if (!window.confirm('¿Eliminar esta imagen del slider?')) return
  clearMessages()
  try {
    await eliminarHomeSlide(slideId)
    feedback.value = 'Slide eliminado.'
    slides.value = slides.value.filter((item) => item.id !== slideId)
  } catch (err) {
    error.value = 'No se pudo eliminar el slide.'
    console.error(err)
  }
}

onMounted(fetchSlides)
</script>

<style scoped>
.hex-color-btn {
  width: 28px;
  height: 28px;
  clip-path: polygon(25% 6.7%, 75% 6.7%, 100% 50%, 75% 93.3%, 25% 93.3%, 0% 50%);
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 1px #cbd5e1;
}

.hex-color-btn:hover {
  transform: scale(1.06);
}
</style>
