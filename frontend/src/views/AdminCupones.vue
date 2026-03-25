<template>
  <div class="p-6 bg-white rounded-lg shadow-md">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-semibold text-slate-800">Cupones de descuento</h2>
      <button
        class="px-4 py-2 bg-slate-800 text-white rounded hover:bg-slate-700 text-sm"
        @click="abrirNuevo"
      >+ Nuevo cupón</button>
    </div>

    <!-- Tabla -->
    <div v-if="cargando" class="text-slate-500 text-sm">Cargando...</div>
    <div v-else-if="!cupones.length" class="text-slate-500 text-sm">No hay cupones creados.</div>
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm border-collapse">
        <thead>
          <tr class="bg-slate-100 text-slate-600 text-left">
            <th class="px-3 py-2">Código</th>
            <th class="px-3 py-2">Tipo</th>
            <th class="px-3 py-2">Valor</th>
            <th class="px-3 py-2">Vigencia</th>
            <th class="px-3 py-2">Usos</th>
            <th class="px-3 py-2">Estado</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in cupones" :key="c.id" class="border-t hover:bg-slate-50">
            <td class="px-3 py-2 font-mono font-semibold">{{ c.codigo }}</td>
            <td class="px-3 py-2">{{ c.tipo === 'porcentaje' ? 'Porcentaje' : 'Monto fijo' }}</td>
            <td class="px-3 py-2">
              {{ c.tipo === 'porcentaje' ? `${c.valor}%` : `$${c.valor}` }}
            </td>
            <td class="px-3 py-2 text-xs text-slate-500">
              <span v-if="c.fecha_inicio || c.fecha_fin">
                {{ c.fecha_inicio ? formatFecha(c.fecha_inicio) : '—' }}
                →
                {{ c.fecha_fin ? formatFecha(c.fecha_fin) : '∞' }}
              </span>
              <span v-else>Sin límite</span>
            </td>
            <td class="px-3 py-2">
              {{ c.usos_actuales }}{{ c.usos_maximos ? ` / ${c.usos_maximos}` : '' }}
            </td>
            <td class="px-3 py-2">
              <span
                class="px-2 py-0.5 rounded text-xs font-medium"
                :class="c.activo ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'"
              >{{ c.activo ? 'Activo' : 'Inactivo' }}</span>
            </td>
            <td class="px-3 py-2 flex gap-2">
              <button class="text-blue-500 hover:underline text-xs" @click="abrirEditar(c)">Editar</button>
              <button class="text-red-400 hover:underline text-xs" @click="eliminar(c)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div
      v-if="modal"
      class="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
      @click.self="cerrarModal"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">{{ editando ? 'Editar cupón' : 'Nuevo cupón' }}</h3>
        <form @submit.prevent="guardar" class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-slate-700">Código *</label>
            <input
              v-model="form.codigo"
              type="text"
              required
              class="mt-1 w-full border rounded px-3 py-1.5 text-sm uppercase"
              placeholder="VERANO20"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700">Descripción</label>
            <input v-model="form.descripcion" type="text" class="mt-1 w-full border rounded px-3 py-1.5 text-sm" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-slate-700">Tipo *</label>
              <select v-model="form.tipo" class="mt-1 w-full border rounded px-3 py-1.5 text-sm">
                <option value="porcentaje">Porcentaje (%)</option>
                <option value="monto_fijo">Monto fijo ($)</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700">Valor *</label>
              <input
                v-model="form.valor"
                type="number"
                min="0.01"
                step="0.01"
                required
                class="mt-1 w-full border rounded px-3 py-1.5 text-sm"
              />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-slate-700">Fecha inicio</label>
              <input v-model="form.fecha_inicio" type="datetime-local" class="mt-1 w-full border rounded px-3 py-1.5 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700">Fecha fin</label>
              <input v-model="form.fecha_fin" type="datetime-local" class="mt-1 w-full border rounded px-3 py-1.5 text-sm" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-slate-700">Usos máximos</label>
              <input v-model="form.usos_maximos" type="number" min="1" placeholder="Ilimitado" class="mt-1 w-full border rounded px-3 py-1.5 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700">Monto mínimo</label>
              <input v-model="form.monto_minimo" type="number" min="0" step="0.01" placeholder="Sin mínimo" class="mt-1 w-full border rounded px-3 py-1.5 text-sm" />
            </div>
          </div>
          <div class="flex items-center gap-2">
            <input v-model="form.activo" type="checkbox" id="activo" class="rounded" />
            <label for="activo" class="text-sm text-slate-700">Activo</label>
          </div>
          <p v-if="errorModal" class="text-red-600 text-xs">{{ errorModal }}</p>
          <div class="flex gap-2 justify-end pt-2">
            <button type="button" class="px-4 py-1.5 text-sm border rounded hover:bg-slate-50" @click="cerrarModal">Cancelar</button>
            <button type="submit" :disabled="guardando" class="px-4 py-1.5 bg-slate-800 text-white text-sm rounded hover:bg-slate-700 disabled:opacity-50">
              {{ guardando ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/axios'

const cupones = ref([])
const cargando = ref(true)
const modal = ref(false)
const editando = ref(null)
const guardando = ref(false)
const errorModal = ref('')

const formVacio = () => ({
  codigo: '',
  descripcion: '',
  tipo: 'porcentaje',
  valor: '',
  fecha_inicio: '',
  fecha_fin: '',
  usos_maximos: '',
  monto_minimo: '',
  activo: true,
})
const form = ref(formVacio())

const cargar = async () => {
  cargando.value = true
  try {
    const { data } = await api.get('promotions/cupones/')
    cupones.value = Array.isArray(data) ? data : (data.results ?? [])
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

const abrirNuevo = () => {
  editando.value = null
  form.value = formVacio()
  errorModal.value = ''
  modal.value = true
}

const abrirEditar = (c) => {
  editando.value = c
  form.value = {
    codigo: c.codigo,
    descripcion: c.descripcion,
    tipo: c.tipo,
    valor: c.valor,
    fecha_inicio: c.fecha_inicio ? c.fecha_inicio.slice(0, 16) : '',
    fecha_fin: c.fecha_fin ? c.fecha_fin.slice(0, 16) : '',
    usos_maximos: c.usos_maximos ?? '',
    monto_minimo: c.monto_minimo ?? '',
    activo: c.activo,
  }
  errorModal.value = ''
  modal.value = true
}

const cerrarModal = () => {
  modal.value = false
  editando.value = null
}

const guardar = async () => {
  guardando.value = true
  errorModal.value = ''
  try {
    const payload = {
      ...form.value,
      codigo: form.value.codigo.toUpperCase().trim(),
      usos_maximos: form.value.usos_maximos || null,
      monto_minimo: form.value.monto_minimo || null,
      fecha_inicio: form.value.fecha_inicio || null,
      fecha_fin: form.value.fecha_fin || null,
    }
    if (editando.value) {
      await api.put(`promotions/cupones/${editando.value.id}/`, payload)
    } else {
      await api.post('promotions/cupones/', payload)
    }
    cerrarModal()
    await cargar()
  } catch (e) {
    const data = e.response?.data
    if (typeof data === 'object') {
      errorModal.value = Object.values(data).flat().join(' ')
    } else {
      errorModal.value = 'Error al guardar'
    }
  } finally {
    guardando.value = false
  }
}

const eliminar = async (c) => {
  if (!confirm(`¿Eliminar el cupón "${c.codigo}"?`)) return
  try {
    await api.delete(`promotions/cupones/${c.id}/`)
    await cargar()
  } catch {
    alert('No se pudo eliminar el cupón')
  }
}

const formatFecha = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>
