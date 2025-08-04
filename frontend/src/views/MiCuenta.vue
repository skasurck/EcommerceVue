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

    <div v-if="seccion === 'Pedidos'">
      <ul>
        <li v-for="pedido in pedidos" :key="pedido.id">
          Pedido #{{ pedido.id }} - Total: {{ pedido.total }}
        </li>
      </ul>
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
} from '../services/account'

const tabs = ['Pedidos', 'Direcciones', 'Perfil', 'Cambiar contraseña']
const seccion = ref('Pedidos')

const pedidos = ref([])
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

onMounted(() => {
  cargarDatos()
})
</script>
