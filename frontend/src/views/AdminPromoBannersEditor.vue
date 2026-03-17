<template>
  <div class="max-w-6xl mx-auto space-y-6">
    <header class="flex flex-col gap-2">
      <h1 class="text-2xl font-bold text-slate-900">Banners promocionales</h1>
      <p class="text-sm text-slate-600">
        Gestiona los banners que aparecen en la página principal. Solo administradores pueden realizar cambios.
      </p>
    </header>

    <section class="bg-white border border-slate-200 rounded-lg p-4 shadow-sm space-y-3">
      <h2 class="text-lg font-semibold text-slate-800">Agregar banner</h2>
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
        <h2 class="text-lg font-semibold text-slate-800">Banners guardados</h2>
        <button
          class="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
          type="button"
          @click="fetchBanners"
        >
          Recargar
        </button>
      </div>

      <div v-if="loading" class="p-4 text-sm text-slate-500">Cargando banners...</div>
      <div v-else-if="banners.length === 0" class="p-4 text-sm text-slate-500">
        No hay banners guardados todavía.
      </div>

      <div v-else class="divide-y divide-slate-200">
        <article
          v-for="banner in banners"
          :key="banner.id"
          class="p-4 grid grid-cols-1 lg:grid-cols-[13rem_1fr] gap-4"
        >
          <img
            :src="banner.imagen_url"
            :alt="banner.titulo || `Banner ${banner.id}`"
            class="w-full h-40 object-cover rounded border border-slate-200"
          />

          <div class="space-y-3">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <label class="text-sm text-slate-700">
                Título
                <input
                  v-model="banner.titulo"
                  type="text"
                  class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5"
                  placeholder="Título del banner"
                />
              </label>
              <label class="text-sm text-slate-700">
                Orden
                <input
                  v-model.number="banner.orden"
                  type="number"
                  min="0"
                  class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5"
                />
              </label>
            </div>

            <label class="text-sm text-slate-700 block">
              Descripción
              <input
                v-model="banner.descripcion"
                type="text"
                class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5"
                placeholder="Descripción del banner"
              />
            </label>

            <label class="text-sm text-slate-700 block">
              Enlace (URL al hacer clic)
              <input
                v-model="banner.enlace"
                type="text"
                class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5"
                placeholder="/productos?categoria=... o https://..."
              />
            </label>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="text-sm text-slate-700">
                <p class="mb-1">Color del título</p>
                <div class="flex flex-wrap items-center gap-2">
                  <button
                    v-for="color in colorPalette"
                    :key="`${banner.id}-${color}`"
                    type="button"
                    class="hex-color-btn"
                    :style="{ backgroundColor: color }"
                    :title="color"
                    @click="banner.titulo_color = color"
                  />
                </div>
              </div>
              <label class="text-sm text-slate-700 block">
                Código HEX
                <input
                  v-model="banner.titulo_color"
                  type="text"
                  maxlength="7"
                  placeholder="#ffffff"
                  class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5"
                />
              </label>
            </div>

            <label class="text-sm text-slate-700 block">
              Reemplazar imagen
              <input
                type="file"
                accept="image/*"
                class="mt-1 w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
                @change="handleImageChange(banner, $event)"
              />
            </label>

            <label class="inline-flex items-center gap-2 text-sm text-slate-700">
              <input v-model="banner.activo" type="checkbox" />
              Activo
            </label>

            <div class="flex flex-wrap gap-2">
              <button
                type="button"
                class="rounded bg-emerald-600 hover:bg-emerald-700 px-3 py-1.5 text-sm text-white"
                @click="saveBanner(banner)"
              >
                Guardar cambios
              </button>
              <button
                type="button"
                class="rounded bg-rose-600 hover:bg-rose-700 px-3 py-1.5 text-sm text-white"
                @click="deleteBanner(banner.id)"
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
import { obtenerPromoBanners, crearPromoBanner, actualizarPromoBanner, eliminarPromoBanner } from '@/services/api'

defineOptions({ name: 'AdminPromoBannersEditor' })

const banners = ref([])
const loading = ref(false)
const uploading = ref(false)
const error = ref('')
const feedback = ref('')
const colorPalette = ['#ffffff', '#111827', '#ea580c', '#dc2626', '#2563eb', '#0891b2', '#16a34a', '#7c3aed']

const clearMessages = () => {
  error.value = ''
  feedback.value = ''
}

const fetchBanners = async () => {
  loading.value = true
  clearMessages()
  try {
    const { data } = await obtenerPromoBanners({ include_inactive: 1, ordering: 'orden' })
    banners.value = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
  } catch (err) {
    error.value = 'No se pudieron cargar los banners.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const buildFormData = (banner) => {
  const fd = new FormData()
  fd.append('titulo', banner.titulo ?? '')
  fd.append('descripcion', banner.descripcion ?? '')
  const safeHex = /^#[0-9A-Fa-f]{6}$/.test(banner.titulo_color || '') ? banner.titulo_color : '#ffffff'
  fd.append('titulo_color', safeHex)
  fd.append('enlace', banner.enlace ?? '')
  fd.append('orden', String(Number(banner.orden) || 0))
  fd.append('activo', banner.activo ? 'true' : 'false')
  if (banner.newImageFile instanceof File) {
    fd.append('imagen', banner.newImageFile)
  }
  return fd
}

const handleImageChange = (banner, event) => {
  const file = event.target.files?.[0]
  if (!file) return
  banner.newImageFile = file
}

const handleUpload = async (event) => {
  const files = Array.from(event.target.files || [])
  if (!files.length) return

  uploading.value = true
  clearMessages()
  try {
    const currentMaxOrder = banners.value.reduce((max, item) => Math.max(max, Number(item.orden) || 0), 0)
    await Promise.all(
      files.map((file, index) => {
        const fd = new FormData()
        fd.append('imagen', file)
        fd.append('titulo', file.name.replace(/\.[^/.]+$/, ''))
        fd.append('descripcion', '')
        fd.append('titulo_color', '#ffffff')
        fd.append('enlace', '')
        fd.append('orden', String(currentMaxOrder + index + 1))
        fd.append('activo', 'true')
        return crearPromoBanner(fd)
      }),
    )
    feedback.value = `Se guardaron ${files.length} banner(es).`
    await fetchBanners()
  } catch (err) {
    error.value = 'No se pudieron subir todas las imágenes.'
    console.error(err)
  } finally {
    uploading.value = false
    event.target.value = ''
  }
}

const saveBanner = async (banner) => {
  clearMessages()
  try {
    const fd = buildFormData(banner)
    await actualizarPromoBanner(banner.id, fd)
    feedback.value = `Banner #${banner.id} actualizado.`
    await fetchBanners()
  } catch (err) {
    error.value = `No se pudo actualizar el banner #${banner.id}.`
    console.error(err)
  }
}

const deleteBanner = async (bannerId) => {
  if (!window.confirm('¿Eliminar este banner?')) return
  clearMessages()
  try {
    await eliminarPromoBanner(bannerId)
    feedback.value = 'Banner eliminado.'
    banners.value = banners.value.filter((item) => item.id !== bannerId)
  } catch (err) {
    error.value = 'No se pudo eliminar el banner.'
    console.error(err)
  }
}

onMounted(fetchBanners)
</script>

<style scoped>
.hex-color-btn {
  width: 28px;
  height: 28px;
  clip-path: polygon(25% 6.7%, 75% 6.7%, 100% 50%, 75% 93.3%, 25% 93.3%, 0% 50%);
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 1px #cbd5e1;
}
</style>
