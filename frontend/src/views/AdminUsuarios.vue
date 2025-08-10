<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">Gestión de usuarios</h2>
    <div class="mb-2 space-x-2">
      <input v-model="search" @input="fetch" placeholder="Buscar..." class="border p-1" />
      <select v-model="role" @change="fetch" class="border p-1">
        <option value="">Todos</option>
        <option value="cliente">Cliente</option>
        <option value="admin">Administrador</option>
        <option value="super_admin">Super Administrador</option>
      </select>
    </div>
    <table class="w-full text-sm border">
      <thead>
        <tr class="bg-gray-100">
          <th class="border px-2 py-1">Username</th>
          <th class="border px-2 py-1">Nombre</th>
          <th class="border px-2 py-1">Email</th>
          <th class="border px-2 py-1">Rol</th>
          <th class="border px-2 py-1">2FA</th>
          <th class="border px-2 py-1">Último acceso</th>
          <th class="border px-2 py-1">Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td class="border px-2 py-1">{{ u.username }}</td>
          <td class="border px-2 py-1">{{ u.nombre_completo }}</td>
          <td class="border px-2 py-1">{{ u.email }}</td>
          <td class="border px-2 py-1">{{ u.rol }}</td>
          <td class="border px-2 py-1">{{ u.estado_2fa ? 'Sí' : 'No' }}</td>
          <td class="border px-2 py-1">{{ u.ultimo_acceso }}</td>
          <td class="border px-2 py-1">
            <div class="flex space-x-1">
              <router-link :to="`/admin/usuarios/${u.id}`" class="underline">Ver</router-link>
              <button @click="resetPassword(u.id)" class="bg-blue-500 text-white px-2 py-1 text-xs rounded hover:bg-blue-600">Restablecer contraseña</button>
              <button v-if="u.rol !== 'super_admin'" @click="deleteUser(u.id)" class="bg-red-500 text-white px-2 py-1 text-xs rounded hover:bg-red-600">Eliminar</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAdminUsersStore } from '../stores/adminUsers'

defineOptions({ name: 'AdminUsuarios' })

const store = useAdminUsersStore()
const route = useRoute()

const users = ref([])
const search = ref('')
const role = ref('')

// Refresco centralizado
async function fetchNow() {
  // cache-buster para evitar caches de proxy/navegador
  const data = await store.fetchUsers({ search: search.value, rol: role.value, _t: Date.now() })
  users.value = data.results || data
}

// 1) Primera carga
onMounted(fetchNow)

// 2) Al reactivar (si la vista está dentro de <keep-alive/>)
onActivated(fetchNow)

// 3) Si cambian los filtros por ruta (opcional si usas query/params)
watch(() => route.fullPath, () => fetchNow())

// 4) Cuando la pestaña vuelve del historial (BFCache) o recupera foco
function onPageShow() { fetchNow() }         // se dispara también al volver con atrás/adelante
function onFocus() { fetchNow() }            // por si el usuario cambia de pestaña
window.addEventListener('pageshow', onPageShow)
window.addEventListener('focus', onFocus)
onBeforeUnmount(() => {
  window.removeEventListener('pageshow', onPageShow)
  window.removeEventListener('focus', onFocus)
})

// Handlers de filtros en la UI
async function fetch() { await fetchNow() }

// Acciones
async function resetPassword(id) {
  try {
    await store.resetPasswordLink(id)
    alert('Si existe, hemos enviado el correo de restablecimiento de contraseña.')
  } catch {
    alert('Error al solicitar el restablecimiento de contraseña')
  }
}

async function deleteUser(id) {
  if (!confirm('¿Eliminar usuario?')) return
  try {
    await store.deleteUser(id)
    await fetchNow() // refrescar inmediatamente tras eliminar
    alert('Usuario eliminado')
  } catch (e) {
    if (e?.response?.status === 403) alert('No se puede eliminar un superadmin')
    else alert('Error al eliminar usuario')
  }
}
</script>
