<template>
  <div class="max-w-6xl mx-auto px-4 py-6">
    <h1 class="text-3xl font-bold mb-4">Mi cuenta</h1>

    <!-- GRID tipo Amazon -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
      <AccountTile
        title="Mis pedidos"
        desc="Rastrear paquetes, devolver pedidos o comprar algo de nuevo"
        icon="mdi:package-variant-closed"
        :to="'/mis-pedidos'"
      />
      <AccountTile
        title="Inicio de sesión y seguridad"
        desc="Cambiar correo, contraseña y número de teléfono"
        icon="mdi:shield-lock-outline"
        @click="seccion='Cambiar contraseña'"
      />
      <AccountTile
        title="Prime / Suscripción"
        desc="Administra tu membresía y pagos de suscripción"
        icon="mdi:amazon"
      />
      <AccountTile
        title="Direcciones"
        desc="Editar direcciones para pedidos y regalos"
        icon="mdi:home-map-marker"
        @click="seccion='Direcciones'"
      />
      <AccountTile
        title="Mis pagos"
        desc="Administrar métodos de pago y transacciones"
        icon="mdi:credit-card-outline"
      />
      <AccountTile
        title="Servicio al cliente"
        desc="Ayuda, artículos y contacto"
        icon="mdi:headset"
      />
    </div>

    <!-- BLOQUES DETALLADOS (tu info actual) -->
    <section class="bg-white border rounded-lg p-5 mb-6">
      <h2 class="text-xl font-semibold mb-3">Perfil</h2>
      <div class="flex items-start gap-4">
        <img :src="profileImg" alt="Perfil" class="w-20 h-20 rounded-full imagen_perfil" />
        <form @submit.prevent="guardarPerfil" class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
          <input v-model="perfil.first_name" placeholder="Nombre" class="border p-2 rounded" />
          <input v-model="perfil.last_name"  placeholder="Apellidos" class="border p-2 rounded" />
          <input v-model="perfil.email"      placeholder="Email" class="border p-2 rounded sm:col-span-2" />
          <input v-model="perfil.perfil.telefono" placeholder="Teléfono" class="border p-2 rounded" />
          <input v-model="perfil.perfil.empresa"  placeholder="Empresa" class="border p-2 rounded" />
          <div class="sm:col-span-2">
            <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
              Guardar
            </button>
          </div>
        </form>
      </div>
    </section>

    <section class="bg-white border rounded-lg p-5 mb-6">
      <h2 class="text-xl font-semibold mb-3">Direcciones</h2>
      <ul class="space-y-2">
        <li v-for="dir in direcciones" :key="dir.id" class="flex items-center justify-between border p-3 rounded">
          <div>
            <div class="font-medium">
              {{ dir.calle }} {{ dir.numero_exterior }} — {{ dir.ciudad }}
              <span v-if="dir.predeterminada" class="ml-2 text-xs text-green-700 bg-green-100 px-2 py-0.5 rounded">
                Predeterminada
              </span>
            </div>
            <div class="text-sm text-gray-600">{{ dir.estado }}, {{ dir.pais }} · CP {{ dir.codigo_postal }}</div>
          </div>
          <div class="flex gap-3">
            <button class="text-blue-700 hover:underline" @click="editarDireccion(dir)">Editar</button>
            <button class="text-red-600 hover:underline" @click="borrarDireccion(dir.id)">Eliminar</button>
          </div>
        </li>
      </ul>
      <button class="mt-3 text-blue-700 hover:underline" @click="nuevaDireccion">Agregar dirección</button>

      <div v-if="mostrarFormDir" class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
        <input v-model="dirForm.nombre" placeholder="Nombre" class="border p-2 rounded" />
        <input v-model="dirForm.apellidos" placeholder="Apellidos" class="border p-2 rounded" />
        <input v-model="dirForm.email" placeholder="Email" class="border p-2 rounded sm:col-span-2" />
        <input v-model="dirForm.nombre_empresa" placeholder="Empresa" class="border p-2 rounded sm:col-span-2" />
        <input v-model="dirForm.calle" placeholder="Calle" class="border p-2 rounded" />
        <input v-model="dirForm.numero_exterior" placeholder="No. exterior" class="border p-2 rounded" />
        <input v-model="dirForm.numero_interior" placeholder="No. interior" class="border p-2 rounded" />
        <input v-model="dirForm.colonia" placeholder="Colonia" class="border p-2 rounded" />
        <input v-model="dirForm.ciudad" placeholder="Ciudad" class="border p-2 rounded" />
        <input v-model="dirForm.estado" placeholder="Estado" class="border p-2 rounded" />
        <input v-model="dirForm.pais" placeholder="País" class="border p-2 rounded" />
        <input v-model="dirForm.codigo_postal" placeholder="Código postal" class="border p-2 rounded" />
        <input v-model="dirForm.telefono" placeholder="Teléfono" class="border p-2 rounded" />
        <textarea v-model="dirForm.referencias" placeholder="Referencias" class="border p-2 rounded sm:col-span-2"></textarea>
        <label class="flex items-center gap-2 sm:col-span-2">
          <input type="checkbox" v-model="dirForm.predeterminada" class="rounded" />
          <span>Predeterminada</span>
        </label>
        <div class="sm:col-span-2 flex gap-3">
          <button type="button" @click="guardarDireccion" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
            Guardar
          </button>
          <button type="button" @click="mostrarFormDir=false" class="px-4 py-2 border rounded">Cancelar</button>
        </div>
      </div>
    </section>

    <section class="bg-white border rounded-lg p-5 mb-6">
      <h2 class="text-xl font-semibold mb-3">Pedidos</h2>

      <!-- DETALLE DEL PEDIDO -->
      <div v-if="pedidoDetalle" class="mb-4 border rounded p-4">
        <h3 class="font-semibold mb-2">Detalle del pedido #{{ pedidoDetalle.id }}</h3>
        <p class="mb-2">Total: {{ pedidoDetalle.total }} — Estado: {{ pedidoDetalle.estado }}</p>
        <div class="grid sm:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 class="font-medium">Productos</h4>
            <ul class="list-disc ml-5">
              <li v-for="item in pedidoDetalle.detalles" :key="item.producto">
                {{ item.producto_nombre }} — {{ item.cantidad }} × {{ item.precio_unitario }} = {{ item.subtotal }}
              </li>
            </ul>
          </div>
          <div>
            <h4 class="font-medium">Envío</h4>
            <p>{{ pedidoDetalle.direccion.calle }} {{ pedidoDetalle.direccion.numero_exterior }}, {{ pedidoDetalle.direccion.ciudad }}</p>
            <h4 class="mt-2 font-medium">Pago</h4>
            <p>{{ pedidoDetalle.metodo_pago_display }}</p>
          </div>
        </div>
      </div>

      <!-- LISTA DE PEDIDOS -->
      <ul class="space-y-2">
        <li v-for="pedido in pedidos" :key="pedido.id" class="flex items-center justify-between border p-3 rounded">
          <div>Pedido #{{ pedido.id }} · <span class="text-gray-600">Estado:</span> {{ pedido.estado }}</div>
          <button class="text-blue-700 hover:underline" @click="verPedido(pedido.id)">Ver detalle</button>
        </li>
      </ul>
    </section>

    <section class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
      <div class="bg-white border rounded-lg p-5">
        <h3 class="font-semibold mb-2">Contenido digital y dispositivos</h3>
        <ul class="text-sm text-blue-700 space-y-1">
          <li><a href="#" class="hover:underline">Aplicaciones y más</a></li>
          <li><a href="#" class="hover:underline">Gestionar contenido y dispositivos</a></li>
        </ul>
      </div>
      <div class="bg-white border rounded-lg p-5">
        <h3 class="font-semibold mb-2">Alertas por correo</h3>
        <ul class="text-sm text-blue-700 space-y-1">
          <li><a href="#" class="hover:underline">Preferencias de comunicación</a></li>
        </ul>
      </div>
      <div class="bg-white border rounded-lg p-5">
        <h3 class="font-semibold mb-2">Más métodos de pago</h3>
        <ul class="text-sm text-blue-700 space-y-1">
          <li><a href="#" class="hover:underline">Preferencias 1-Clic</a></li>
        </ul>
      </div>
    </section>
    <section class="bg-white border rounded-lg p-5 mb-6">
      <h2 class="text-xl font-semibold mb-3">Cambiar contraseña</h2>
      <form @submit.prevent="cambiarPass" class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
        <input v-model="password.old_password" type="password" placeholder="Contraseña actual" class="border p-2 rounded" />
        <input v-model="password.new_password" type="password" placeholder="Nueva contraseña" class="border p-2 rounded" />
        <div class="sm:col-span-2">
          <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
            Guardar contraseña
          </button>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AccountTile from '@/components/AccountTile.vue'
import profileImg from '../assets/profile-placeholder.svg'
import {
  obtenerPedidos,
  obtenerDirecciones,
  obtenerPerfil,
  actualizarPerfil,
  cambiarPassword,
  obtenerPedido,
  crearDireccion,
  actualizarDireccion,
  eliminarDireccion,
} from '../services/account'


const tabs = ['Resumen', 'Pedidos', 'Direcciones', 'Cambiar contraseña']
const seccion = ref('Resumen')

const pedidos = ref([])
const pedidoDetalle = ref(null)
const direcciones = ref([])
const perfil = ref({ perfil: { telefono: '', empresa: '' } })
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
  direcciones.value = dir.data.direcciones
  perfil.value = prof.data
  perfil.value.perfil = perfil.value.perfil || { telefono: '', empresa: '' }
}

const guardarPerfil = async () => { await actualizarPerfil(perfil.value) }
const cambiarPass   = async () => { await cambiarPassword(password.value); password.value={old_password:'',new_password:''} }
const verPedido     = async (id) => { const r = await obtenerPedido(id); pedidoDetalle.value = r.data }

const nuevaDireccion = () => {
  editandoDir.value = null
  dirForm.value = { nombre:'', apellidos:'', email:'', nombre_empresa:'', calle:'', numero_exterior:'', numero_interior:'',
    colonia:'', ciudad:'', pais:'', estado:'', codigo_postal:'', telefono:'', referencias:'', predeterminada:false }
  mostrarFormDir.value = true
}

const editarDireccion = (dir) => { editandoDir.value = dir.id; dirForm.value = { ...dir }; mostrarFormDir.value = true }
const guardarDireccion = async () => { editandoDir.value ? await actualizarDireccion(editandoDir.value, dirForm.value) : await crearDireccion(dirForm.value); mostrarFormDir.value=false; await cargarDatos() }
const borrarDireccion  = async (id) => { await eliminarDireccion(id); await cargarDatos() }

onMounted(cargarDatos)
</script>
<style scoped>
.imagen_perfil{ object-fit: cover; border:2px solid #e5e7eb; }
</style>