<template>
  <div class="max-w-6xl mx-auto px-4 py-6">
    <h1 class="text-3xl font-bold mb-4">Mi cuenta</h1>

    <section class="bg-white border rounded-lg p-5 mb-6">
      <h2 class="text-xl font-semibold mb-3">Perfil</h2>
      <div class="flex items-start gap-4">
        <div class="relative shrink-0 cursor-pointer group" @click="fileInput.click()">
          <img :src="fotoUrl" alt="Perfil" class="w-20 h-20 rounded-full object-cover border-2 border-gray-200" />
          <div class="absolute inset-0 flex items-center justify-center rounded-full bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity">
            <span class="text-white text-xs font-medium">Cambiar</span>
          </div>
          <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFotoChange" />
        </div>
        <form @submit.prevent="guardarPerfil" class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
          <input v-model="perfil.first_name" placeholder="Nombre" class="border p-2 rounded" />
          <input v-model="perfil.last_name" placeholder="Apellidos" class="border p-2 rounded" />
          <input v-model="perfil.email" placeholder="Email" class="border p-2 rounded sm:col-span-2" />
          <input v-model="perfil.perfil.telefono" placeholder="Teléfono" class="border p-2 rounded" />
          <input v-model="perfil.perfil.empresa" placeholder="Empresa" class="border p-2 rounded" />
          <div class="sm:col-span-2">
            <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
              Guardar
            </button>
          </div>
        </form>
      </div>
    </section>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
      <AccountTile
        title="Mis pedidos"
        desc="Rastrear paquetes, devolver pedidos o comprar algo de nuevo"
        icon="mdi:package-variant-closed"
        :to="'/mis-pedidos'"
      />
      <AccountTile
        title="Inicio de sesión y seguridad"
        desc="Cambiar contraseña"
        icon="mdi:shield-lock-outline"
        :to="'/seguridad'"
      />
      <AccountTile
        title="Direcciones"
        desc="Editar direcciones para pedidos y regalos"
        icon="mdi:home-map-marker"
        :to="'/direcciones'"
      />
    </div>

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

    <!-- Cerrar sesión -->
    <div class="mt-8 pt-6 border-t border-slate-200">
      <button
        type="button"
        @click="cerrarSesion"
        class="inline-flex items-center gap-2 rounded-xl border border-red-200 bg-white px-5 py-2.5 text-sm font-semibold text-red-600 hover:bg-red-50 hover:border-red-300 transition-colors"
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9"/>
        </svg>
        Cerrar sesión
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AccountTile from '@/components/AccountTile.vue'
import placeholderImg from '@/assets/profile-placeholder.svg'
import { obtenerPerfil, actualizarPerfil, subirFotoPerfil } from '@/services/account'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const perfil = ref({ perfil: { telefono: '', empresa: '' } })
const fotoUrl = ref(placeholderImg)
const fileInput = ref(null)

const cerrarSesion = () => {
  auth.logout()
  router.push('/')
}

const cargarDatos = async () => {
  const { data } = await obtenerPerfil()
  perfil.value = data
  perfil.value.perfil = perfil.value.perfil || { telefono: '', empresa: '' }
  fotoUrl.value = data.foto_url || placeholderImg
}

const guardarPerfil = async () => { await actualizarPerfil(perfil.value) }

const onFotoChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const { data } = await subirFotoPerfil(file)
  fotoUrl.value = data.foto_url
}

onMounted(cargarDatos)
</script>

