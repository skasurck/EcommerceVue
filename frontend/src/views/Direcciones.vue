<template>
  <div class="max-w-3xl mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-4">Direcciones</h1>

    <ul class="space-y-2 mb-3">
      <li v-for="dir in direcciones" :key="dir.id" class="flex items-center justify-between border p-3 rounded bg-white">
        <div>
          <div class="font-medium">
            {{ dir.calle }} {{ dir.numero_exterior }} — {{ dir.ciudad }}
            <span v-if="dir.predeterminada" class="ml-2 text-xs text-green-700 bg-green-100 px-2 py-0.5 rounded">Predeterminada</span>
          </div>
          <div class="text-sm text-gray-600">{{ dir.estado }}, {{ dir.pais }} · CP {{ dir.codigo_postal }}</div>
        </div>
        <div class="flex gap-3">
          <button class="text-blue-700 hover:underline" @click="editar(dir)">Editar</button>
          <button class="text-red-600 hover:underline" @click="borrar(dir.id)">Eliminar</button>
        </div>
      </li>
    </ul>

    <button class="mb-3 text-blue-700 hover:underline" @click="nueva">Agregar dirección</button>

    <div v-if="show" class="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-white border rounded p-4" :key="formKey">
      <input v-model="form.nombre"           placeholder="Nombre"          class="border p-2 rounded" />
      <input v-model="form.apellidos"        placeholder="Apellidos"       class="border p-2 rounded" />
      <input v-model="form.email"            placeholder="Email"           class="border p-2 rounded sm:col-span-2" />
      <input v-model="form.nombre_empresa"   placeholder="Empresa"         class="border p-2 rounded sm:col-span-2" />
      <input v-model="form.calle"            placeholder="Calle"           class="border p-2 rounded" />
      <input v-model="form.numero_exterior"  placeholder="No. exterior"    class="border p-2 rounded" />
      <input v-model="form.numero_interior"  placeholder="No. interior"    class="border p-2 rounded" />
      <input v-model="form.colonia"          placeholder="Colonia"         class="border p-2 rounded" />
      <input v-model="form.ciudad"           placeholder="Ciudad"          class="border p-2 rounded" />
      <input v-model="form.estado"           placeholder="Estado"          class="border p-2 rounded" />
      <input v-model="form.pais"             placeholder="País"            class="border p-2 rounded" />
      <input v-model="form.codigo_postal"    placeholder="Código postal"   class="border p-2 rounded" />
      <input v-model="form.telefono"         placeholder="Teléfono"        class="border p-2 rounded" />
      <textarea v-model="form.referencias"   placeholder="Referencias"     class="border p-2 rounded sm:col-span-2"></textarea>

      <label class="flex items-center gap-2 sm:col-span-2">
        <input type="checkbox" v-model="form.predeterminada" class="rounded" />
        <span>Predeterminada</span>
      </label>

      <div class="sm:col-span-2 flex gap-3">
        <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded" @click="guardar">Guardar</button>
        <button class="px-4 py-2 border rounded" @click="show=false">Cancelar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { obtenerDirecciones, crearDireccion, actualizarDireccion, eliminarDireccion } from '@/services/account'

const direcciones = ref([])
const form = ref({})
const editingId = ref(null)
const show = ref(false)
const formKey = ref(0) // fuerza rerender del form cuando editas

const blank = () => ({
  nombre: '', apellidos: '', email: '', nombre_empresa: '',
  calle: '', numero_exterior: '', numero_interior: '',
  colonia: '', ciudad: '', pais: '', estado: '',
  codigo_postal: '', telefono: '', referencias: '',
  predeterminada: false,
})

const cargar = async () => {
  const r = await obtenerDirecciones()
  direcciones.value = r.data.direcciones
}

onMounted(cargar)

const nueva = () => {
  editingId.value = null
  form.value = blank()
  show.value = true
  formKey.value++ // resetea estado visual del form
}

const editar = (d) => {
  editingId.value = d.id
  // Clonado profundo para no mutar la lista al tipear
  form.value = JSON.parse(JSON.stringify({ ...blank(), ...d }))
  show.value = true
  formKey.value++
}

const guardar = async () => {
  // Si tu API espera PUT (reemplazo total), le mandamos el objeto completo (form.value).
  // Si soporta PATCH, podrías llamar actualizarDireccion con método PATCH y solo cambios.
  if (editingId.value) {
    await actualizarDireccion(editingId.value, form.value) // asegúrate que este servicio use PUT o PATCH según tu backend
  } else {
    await crearDireccion(form.value)
  }
  show.value = false
  await cargar()
}

const borrar = async (id) => {
  await eliminarDireccion(id)
  await cargar()
}
</script>
