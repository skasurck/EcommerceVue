<template>
  <div class="p-4 max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">Mi cuenta</h1>
    <div class="flex gap-4 mb-4 border-b">
      <button
        v-for="tab in tabs"
        :key="tab"
        @click="seccion = tab"
        :class="['pb-2', seccion === tab ? 'border-b-2 border-blue-500' : '']"
      >
        {{ tab }}
      </button>
    </div>

    <div v-if="seccion === 'Resumen'" class="space-y-4">
      <div class="flex items-center space-x-4">
        <img :src="profileImg" alt="Perfil" class="w-24 h-24 rounded-full img-perfil" />
        <div>
          <p class="font-semibold">{{ perfil.first_name }} {{ perfil.last_name }}</p>
          <p>{{ perfil.email }}</p>
          <p>{{ perfil.perfil?.telefono }}</p>
          <p v-if="perfil.perfil?.empresa">{{ perfil.perfil.empresa }}</p>
        </div>
      </div>
      <div>
        <h2 class="font-semibold mb-2">Direcciones</h2>
        <ul>
          <li v-for="dir in direcciones" :key="dir.id" class="mb-1">
            {{ dir.calle }} {{ dir.numero_exterior }} - {{ dir.ciudad }}
            <span v-if="dir.predeterminada">(Predeterminada)</span>
            <button class="ml-2 underline" @click="editarDireccion(dir)">Editar</button>
          </li>
        </ul>
        <button class="underline mt-2" @click="nuevaDireccion">Agregar dirección</button>
        <div v-if="mostrarFormDir" class="space-y-2 mt-2">
          <input v-model="dirForm.nombre" placeholder="Nombre" class="border p-1 w-full" />
          <input v-model="dirForm.apellidos" placeholder="Apellidos" class="border p-1 w-full" />
          <input v-model="dirForm.email" placeholder="Email" class="border p-1 w-full" />
          <input v-model="dirForm.nombre_empresa" placeholder="Empresa" class="border p-1 w-full" />
          <input v-model="dirForm.calle" placeholder="Calle" class="border p-1 w-full" />
          <input v-model="dirForm.numero_exterior" placeholder="Número exterior" class="border p-1 w-full" />
          <input v-model="dirForm.numero_interior" placeholder="Número interior" class="border p-1 w-full" />
          <input v-model="dirForm.colonia" placeholder="Colonia" class="border p-1 w-full" />
          <input v-model="dirForm.ciudad" placeholder="Ciudad" class="border p-1 w-full" />
          <input v-model="dirForm.estado" placeholder="Estado" class="border p-1 w-full" />
          <input v-model="dirForm.pais" placeholder="País" class="border p-1 w-full" />
          <input v-model="dirForm.codigo_postal" placeholder="Código postal" class="border p-1 w-full" />
          <input v-model="dirForm.telefono" placeholder="Teléfono" class="border p-1 w-full" />
          <textarea v-model="dirForm.referencias" placeholder="Referencias" class="border p-1 w-full"></textarea>
          <label class="flex items-center space-x-2">
            <input type="checkbox" v-model="dirForm.predeterminada" />
            <span>Predeterminada</span>
          </label>
          <div class="space-x-2">
            <button type="button" @click="guardarDireccion" class="bg-blue-500 text-white px-3 py-1">Guardar</button>
            <button type="button" @click="mostrarFormDir = false" class="px-3 py-1 border">Cancelar</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="seccion === 'Pedidos'" class="space-y-4">
      <ul>
        <li v-for="pedido in pedidos" :key="pedido.id" class="mb-2">
          <button class="underline" @click="verPedido(pedido.id)">
            Pedido #{{ pedido.id }} - Total: {{ pedido.total }}
          </button>
        </li>
      </ul>
      <div v-if="pedidoDetalle" class="border p-4">
        <h2 class="font-semibold mb-2">Detalle del pedido #{{ pedidoDetalle.id }}</h2>
        <div class="mb-2">
          <h3 class="font-medium">Productos</h3>
          <ul class="ml-4 list-disc">
            <li v-for="item in pedidoDetalle.detalles" :key="item.producto">
              {{ item.producto_nombre }} - {{ item.cantidad }} x {{ item.precio_unitario }} = {{ item.subtotal }}
            </li>
          </ul>
        </div>
        <div class="mb-2">
          <h3 class="font-medium">Dirección de envío</h3>
          <p>{{ pedidoDetalle.direccion.calle }} {{ pedidoDetalle.direccion.numero_exterior }}, {{ pedidoDetalle.direccion.ciudad }}</p>
        </div>
        <div class="mb-2">
          <h3 class="font-medium">Método de envío</h3>
          <p>{{ pedidoDetalle.metodo_envio_detalle.nombre }} - {{ pedidoDetalle.metodo_envio_detalle.descripcion }} ({{ pedidoDetalle.metodo_envio_detalle.costo }})</p>
        </div>
        <div class="mb-2">
          <h3 class="font-medium">Método de pago</h3>
          <p>{{ pedidoDetalle.metodo_pago_display }}</p>
        </div>
      </div>
    </div>

    <div v-if="seccion === 'Direcciones'">
      <ul>
        <li v-for="dir in direcciones" :key="dir.id" class="mb-2">
          {{ dir.calle }} {{ dir.numero_exterior }} - {{ dir.ciudad }}
        </li>
      </ul>
    </div>

    <div v-if="seccion === 'Perfil'">
      <form @submit.prevent="guardarPerfil" class="space-y-2">
        <input v-model="perfil.first_name" placeholder="Nombre" class="border p-1 w-full" />
        <input v-model="perfil.last_name" placeholder="Apellidos" class="border p-1 w-full" />
        <input v-model="perfil.email" placeholder="Email" class="border p-1 w-full" />
        <input v-model="perfil.perfil.telefono" placeholder="Teléfono" class="border p-1 w-full" />
        <input v-model="perfil.perfil.empresa" placeholder="Empresa" class="border p-1 w-full" />
        <button type="submit" class="bg-blue-500 text-white px-3 py-1">Guardar</button>
      </form>
      <div class="mt-4">
        <h2 class="font-semibold mb-2">Direcciones</h2>
        <ul>
          <li v-for="dir in direcciones" :key="dir.id" class="mb-1">
            {{ dir.calle }} {{ dir.numero_exterior }} - {{ dir.ciudad }}
            <span v-if="dir.predeterminada">(Predeterminada)</span>
            <button class="ml-2 underline" @click="editarDireccion(dir)">Editar</button>
          </li>
        </ul>
        <button class="underline mt-2" @click="nuevaDireccion">Agregar dirección</button>
        <div v-if="mostrarFormDir" class="space-y-2 mt-2">
          <input v-model="dirForm.nombre" placeholder="Nombre" class="border p-1 w-full" />
          <input v-model="dirForm.apellidos" placeholder="Apellidos" class="border p-1 w-full" />
          <input v-model="dirForm.email" placeholder="Email" class="border p-1 w-full" />
          <input v-model="dirForm.nombre_empresa" placeholder="Empresa" class="border p-1 w-full" />
          <input v-model="dirForm.calle" placeholder="Calle" class="border p-1 w-full" />
          <input v-model="dirForm.numero_exterior" placeholder="Número exterior" class="border p-1 w-full" />
          <input v-model="dirForm.numero_interior" placeholder="Número interior" class="border p-1 w-full" />
          <input v-model="dirForm.colonia" placeholder="Colonia" class="border p-1 w-full" />
          <input v-model="dirForm.ciudad" placeholder="Ciudad" class="border p-1 w-full" />
          <input v-model="dirForm.estado" placeholder="Estado" class="border p-1 w-full" />
          <input v-model="dirForm.pais" placeholder="País" class="border p-1 w-full" />
          <input v-model="dirForm.codigo_postal" placeholder="Código postal" class="border p-1 w-full" />
          <input v-model="dirForm.telefono" placeholder="Teléfono" class="border p-1 w-full" />
          <textarea v-model="dirForm.referencias" placeholder="Referencias" class="border p-1 w-full"></textarea>
          <label class="flex items-center space-x-2">
            <input type="checkbox" v-model="dirForm.predeterminada" />
            <span>Predeterminada</span>
          </label>
          <div class="space-x-2">
            <button type="button" @click="guardarDireccion" class="bg-blue-500 text-white px-3 py-1">Guardar</button>
            <button type="button" @click="mostrarFormDir = false" class="px-3 py-1 border">Cancelar</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="seccion === 'Cambiar contraseña'">
      <form @submit.prevent="cambiarPass" class="space-y-2">
        <input v-model="password.old_password" type="password" placeholder="Contraseña actual" class="border p-1 w-full" />
        <input v-model="password.new_password" type="password" placeholder="Nueva contraseña" class="border p-1 w-full" />
        <button type="submit" class="bg-blue-500 text-white px-3 py-1">Cambiar</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  obtenerPedidos,
  obtenerDirecciones,
  obtenerPerfil,
  actualizarPerfil,
  cambiarPassword,
  obtenerPedido,
  crearDireccion,
  actualizarDireccion,
} from '../services/account'

import profileImg from '../assets/profile-placeholder.svg'

const tabs = ['Resumen', 'Pedidos', 'Direcciones', 'Perfil', 'Cambiar contraseña']
const seccion = ref('Resumen')

const pedidos = ref([])
const pedidoDetalle = ref(null)
const direcciones = ref([])
const perfil = ref({ perfil: {} })
const password = ref({ old_password: '', new_password: '' })
const dirForm = ref(null)
const editandoDir = ref(null)
const mostrarFormDir = ref(false)

const cargarDatos = async () => {
  const [ped, dir, prof] = await Promise.all([
    obtenerPedidos(),
    obtenerDirecciones(),
    obtenerPerfil(),
  ])
  pedidos.value = ped.data
  direcciones.value = dir.data
  perfil.value = prof.data
}

const guardarPerfil = async () => {
  await actualizarPerfil(perfil.value)
}

const cambiarPass = async () => {
  await cambiarPassword(password.value)
  password.value.old_password = ''
  password.value.new_password = ''
}

const verPedido = async (id) => {
  const resp = await obtenerPedido(id)
  pedidoDetalle.value = resp.data
}

const nuevaDireccion = () => {
  editandoDir.value = null
  dirForm.value = {
    nombre: '',
    apellidos: '',
    email: '',
    nombre_empresa: '',
    calle: '',
    numero_exterior: '',
    numero_interior: '',
    colonia: '',
    ciudad: '',
    pais: '',
    estado: '',
    codigo_postal: '',
    telefono: '',
    referencias: '',
    predeterminada: false,
  }
  mostrarFormDir.value = true
}

const editarDireccion = (dir) => {
  editandoDir.value = dir.id
  dirForm.value = { ...dir }
  mostrarFormDir.value = true
}

const guardarDireccion = async () => {
  if (editandoDir.value) {
    await actualizarDireccion(editandoDir.value, dirForm.value)
  } else {
    await crearDireccion(dirForm.value)
  }
  mostrarFormDir.value = false
  await cargarDatos()
}

onMounted(() => {
  cargarDatos()
})
</script>
<style scoped>
.img-perfil {
  width: 48px; /* 24 * 4 */
  height: 48px; /* 24 * 4 */
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #4f46e5; /* Indigo-600 */
}
</style>