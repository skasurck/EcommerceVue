<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">Usuario {{ user?.username }}</h2>
    <form @submit.prevent="guardarUsuario" class="space-y-2 mb-6">
      <div class="grid grid-cols-2 gap-2">
        <input v-model="form.first_name" placeholder="Nombre" class="border p-1" />
        <input v-model="form.last_name" placeholder="Apellidos" class="border p-1" />
        <input v-model="form.email" placeholder="Email" class="border p-1 col-span-2" />
        <input v-model="form.perfil.telefono" placeholder="Teléfono" class="border p-1 col-span-2" />
        <input v-model="form.perfil.empresa" placeholder="Empresa" class="border p-1 col-span-2" />
        <select v-model="form.perfil.rol" class="border p-1 col-span-2" :disabled="user?.perfil?.rol==='super_admin'">
          <option value="cliente">Cliente</option>
          <option value="admin">Administrador</option>
        </select>
        <p v-if="user?.perfil?.rol==='super_admin'" class="text-xs text-gray-600 col-span-2">El rol Super Administrador solo se asigna desde consola o Django Admin</p>
      </div>
      <button class="bg-blue-500 text-white px-3 py-1">Guardar</button>
    </form>

    <div class="mb-6">
      <h3 class="font-semibold mb-2">Dirección predeterminada</h3>
      <div v-if="defaultDir">
        <div class="grid grid-cols-2 gap-2 mb-2">
          <input v-model="defaultDir.nombre" placeholder="Nombre" class="border p-1" />
          <input v-model="defaultDir.apellidos" placeholder="Apellidos" class="border p-1" />
          <input v-model="defaultDir.email" placeholder="Email" class="border p-1 col-span-2" />
          <input v-model="defaultDir.nombre_empresa" placeholder="Empresa" class="border p-1 col-span-2" />
          <input v-model="defaultDir.calle" placeholder="Calle" class="border p-1 col-span-2" />
          <input v-model="defaultDir.numero_exterior" placeholder="Número exterior" class="border p-1" />
          <input v-model="defaultDir.numero_interior" placeholder="Número interior" class="border p-1" />
          <input v-model="defaultDir.colonia" placeholder="Colonia" class="border p-1" />
          <input v-model="defaultDir.ciudad" placeholder="Ciudad" class="border p-1" />
          <input v-model="defaultDir.estado" placeholder="Estado" class="border p-1" />
          <input v-model="defaultDir.codigo_postal" placeholder="CP" class="border p-1" />
          <input v-model="defaultDir.pais" placeholder="País" class="border p-1" />
          <input v-model="defaultDir.telefono" placeholder="Teléfono" class="border p-1 col-span-2" />
          <textarea v-model="defaultDir.referencias" placeholder="Referencias" class="border p-1 col-span-2"></textarea>
        </div>
        <button @click="guardarDireccionPredeterminada" class="bg-blue-500 text-white px-2 py-1">Guardar</button>
      </div>
      <div v-else>
        <button @click="crearDefaultDir" class="bg-green-500 text-white px-2 py-1">Crear</button>
      </div>
    </div>

    <div>
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Otras direcciones</h3>
        <button @click="abrirNuevaDireccion" class="bg-green-500 text-white px-2 py-1">Agregar dirección</button>
      </div>
      <table class="w-full text-sm border">
        <thead>
          <tr class="bg-gray-100">
            <th class="border px-2 py-1">Nombre</th>
            <th class="border px-2 py-1">Calle y número</th>
            <th class="border px-2 py-1">Colonia</th>
            <th class="border px-2 py-1">Ciudad</th>
            <th class="border px-2 py-1">Estado</th>
            <th class="border px-2 py-1">CP</th>
            <th class="border px-2 py-1">País</th>
            <th class="border px-2 py-1">Teléfono</th>
            <th class="border px-2 py-1">Predeterminada</th>
            <th class="border px-2 py-1">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="dir in otrasDirecciones" :key="dir.id">
            <td class="border px-2 py-1">{{ dir.nombre }} {{ dir.apellidos }}</td>
            <td class="border px-2 py-1">{{ dir.calle }} {{ dir.numero_exterior }}</td>
            <td class="border px-2 py-1">{{ dir.colonia }}</td>
            <td class="border px-2 py-1">{{ dir.ciudad }}</td>
            <td class="border px-2 py-1">{{ dir.estado }}</td>
            <td class="border px-2 py-1">{{ dir.codigo_postal }}</td>
            <td class="border px-2 py-1">{{ dir.pais }}</td>
            <td class="border px-2 py-1">{{ dir.telefono }}</td>
            <td class="border px-2 py-1">{{ dir.predeterminada ? 'Sí' : '' }}</td>
            <td class="border px-2 py-1 space-x-2">
              <button @click="editarDireccion(dir)" class="underline">Editar</button>
              <button @click="eliminarDireccion(dir)" class="text-red-600 underline">Eliminar</button>
              <button @click="hacerPredeterminada(dir)" v-if="!dir.predeterminada" class="underline">Hacer predeterminada</button>
            </td>
          </tr>
        </tbody>
      </table>
      <button @click="importarDirecciones" class="mt-2 px-2 py-1 border">Importar direcciones usadas en pedidos</button>
    </div>

    <section class="mt-6">
      <h3 class="font-semibold mb-2">Seguridad</h3>
      <button @click="abrirModalPassword" class="bg-gray-800 text-white px-3 py-1 text-sm rounded">Cambiar contraseña</button>
    </section>

    <div v-if="showPwdModal" class="fixed inset-0 bg-black/50 flex items-center justify-center">
      <div class="bg-white p-4 w-96 space-y-2">
        <h4 class="font-semibold">Cambiar contraseña</h4>
        <input v-model="pwd.new1" type="password" placeholder="Nueva contraseña" class="border p-1 w-full" />
        <input v-model="pwd.new2" type="password" placeholder="Confirmar contraseña" class="border p-1 w-full" />
        <div class="text-right space-x-2">
          <button @click="guardarPassword" class="bg-blue-600 text-white px-3 py-1 rounded">Guardar</button>
          <button @click="showPwdModal=false" class="px-3 py-1 border rounded">Cancelar</button>
        </div>
      </div>
    </div>

    <div v-if="mostrarModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white p-4 w-96 space-y-2">
        <h3 class="font-semibold">{{ editDir ? 'Editar' : 'Nueva' }} dirección</h3>
        <div class="space-y-1">
          <input v-model="modalDir.nombre" placeholder="Nombre" class="border p-1 w-full" />
          <input v-model="modalDir.apellidos" placeholder="Apellidos" class="border p-1 w-full" />
          <input v-model="modalDir.email" placeholder="Email" class="border p-1 w-full" />
          <input v-model="modalDir.nombre_empresa" placeholder="Empresa" class="border p-1 w-full" />
          <input v-model="modalDir.calle" placeholder="Calle" class="border p-1 w-full" />
          <input v-model="modalDir.numero_exterior" placeholder="Número exterior" class="border p-1 w-full" />
          <input v-model="modalDir.numero_interior" placeholder="Número interior" class="border p-1 w-full" />
          <input v-model="modalDir.colonia" placeholder="Colonia" class="border p-1 w-full" />
          <input v-model="modalDir.ciudad" placeholder="Ciudad" class="border p-1 w-full" />
          <input v-model="modalDir.estado" placeholder="Estado" class="border p-1 w-full" />
          <input v-model="modalDir.codigo_postal" placeholder="CP" class="border p-1 w-full" />
          <input v-model="modalDir.pais" placeholder="País" class="border p-1 w-full" />
          <input v-model="modalDir.telefono" placeholder="Teléfono" class="border p-1 w-full" />
          <textarea v-model="modalDir.referencias" placeholder="Referencias" class="border p-1 w-full"></textarea>
          <label class="flex items-center space-x-2"><input type="checkbox" v-model="modalDir.predeterminada" /> <span>Predeterminada</span></label>
        </div>
        <div class="text-right space-x-2">
          <button @click="guardarModalDireccion" class="bg-blue-500 text-white px-2 py-1">Guardar</button>
          <button @click="cerrarModal" class="px-2 py-1 border">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAdminUsersStore } from '../stores/adminUsers'

defineOptions({ name: 'AdminUsuarioDetalle' })

const route = useRoute()
const store = useAdminUsersStore()
const user = ref(null)
const form = reactive({ first_name:'', last_name:'', email:'', perfil:{ telefono:'', empresa:'', rol:'cliente' } })
const defaultDir = ref(null)
const otrasDirecciones = ref([])
const mostrarModal = ref(false)
const modalDir = reactive({})
const editDir = ref(null)
const showPwdModal = ref(false)
const pwd = reactive({ new1:'', new2:'' })

onMounted(async () => {
  const data = await store.fetchUser(route.params.id)
  user.value = data
  Object.assign(form, { first_name: data.first_name, last_name: data.last_name, email: data.email, perfil: { ...data.perfil } })
  defaultDir.value = data.direccion_predeterminada || null
  otrasDirecciones.value = data.direcciones || []
})

async function guardarUsuario() {
  const payload = { ...form, perfil: form.perfil }
  if (defaultDir.value) payload.direccion_predeterminada = defaultDir.value
  const data = await store.updateUser(user.value.id, payload)
  user.value = data
  alert('Usuario actualizado')
}

async function guardarDireccionPredeterminada() {
  const payload = { ...defaultDir.value, predeterminada: true }
  const data = await store.updateUser(user.value.id, { direccion_predeterminada: payload })
  defaultDir.value = data.direccion_predeterminada
  otrasDirecciones.value = data.direcciones
  alert('Dirección actualizada')
}

function crearDefaultDir() {
  defaultDir.value = { nombre:'', apellidos:'', email:'', nombre_empresa:'', calle:'', numero_exterior:'', numero_interior:'', colonia:'', ciudad:'', estado:'', codigo_postal:'', pais:'', telefono:'', referencias:'', predeterminada:true }
}

function abrirNuevaDireccion() {
  editDir.value = null
  Object.assign(modalDir, { nombre:'', apellidos:'', email:'', nombre_empresa:'', calle:'', numero_exterior:'', numero_interior:'', colonia:'', ciudad:'', estado:'', codigo_postal:'', pais:'', telefono:'', referencias:'', predeterminada:false })
  mostrarModal.value = true
}

function cerrarModal() { mostrarModal.value = false }

function editarDireccion(dir) { editDir.value = dir.id; Object.assign(modalDir, { ...dir }); mostrarModal.value = true }

async function guardarModalDireccion() {
  if (editDir.value) {
    await store.updateDireccion(user.value.id, editDir.value, modalDir)
  } else {
    await store.createDireccion(user.value.id, modalDir)
  }
  const resp = await store.getDirecciones(user.value.id)
  otrasDirecciones.value = resp
  const data = await store.fetchUser(user.value.id)
  defaultDir.value = data.direccion_predeterminada
  mostrarModal.value = false
}

async function eliminarDireccion(dir) {
  await store.deleteDireccion(user.value.id, dir.id)
  otrasDirecciones.value = await store.getDirecciones(user.value.id)
  const data = await store.fetchUser(user.value.id)
  defaultDir.value = data.direccion_predeterminada
}

async function hacerPredeterminada(dir) {
  await store.setDefaultDireccion(user.value.id, dir.id)
  const data = await store.fetchUser(user.value.id)
  defaultDir.value = data.direccion_predeterminada
  otrasDirecciones.value = data.direcciones
}

async function importarDirecciones() {
  const res = await store.importarDirecciones(user.value.id)
  alert(`Importadas: ${res.importadas}, ya existían: ${res.ya_existian}`)
  const data = await store.fetchUser(user.value.id)
  defaultDir.value = data.direccion_predeterminada
  otrasDirecciones.value = data.direcciones
}

function abrirModalPassword(){
  showPwdModal.value = true
  pwd.new1 = ''
  pwd.new2 = ''
}

async function guardarPassword(){
  if (!pwd.new1 || pwd.new1.length < 8) return alert('La contraseña debe tener al menos 8 caracteres.')
  if (pwd.new1 !== pwd.new2) return alert('Las contraseñas no coinciden.')
  try {
    await store.setPassword(user.value.id, pwd.new1)
    showPwdModal.value = false
    alert('Contraseña actualizada')
  } catch (e) {
    alert('Error al actualizar contraseña')
  }
}
</script>
