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
        <img :src="profileImg" alt="Perfil" class="w-24 h-24 rounded-full" />
        <div>
          <p class="font-semibold">{{ perfil.first_name }} {{ perfil.last_name }}</p>
          <p>{{ perfil.email }}</p>
          <p>{{ perfil.perfil?.telefono }}</p>
        </div>
      </div>
      <div>
        <h2 class="font-semibold mb-2">Direcciones</h2>
        <ul>
          <li v-for="dir in direcciones" :key="dir.id" class="mb-1">
            {{ dir.calle }} {{ dir.numero_exterior }} - {{ dir.ciudad }}
          </li>
        </ul>
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
        <button type="submit" class="bg-blue-500 text-white px-3 py-1">Guardar</button>
      </form>
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
} from '../services/account'

import profileImg from '../assets/profile-placeholder.svg'

const tabs = ['Resumen', 'Pedidos', 'Direcciones', 'Perfil', 'Cambiar contraseña']
const seccion = ref('Resumen')

const pedidos = ref([])
const pedidoDetalle = ref(null)
const direcciones = ref([])
const perfil = ref({ perfil: {} })
const password = ref({ old_password: '', new_password: '' })

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

onMounted(() => {
  cargarDatos()
})
</script>
