<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">Gestión de usuarios</h2>
    <div class="mb-2 space-x-2">
      <input v-model="search" placeholder="Buscar..." class="border p-1" />
      <select v-model="role" class="border p-1">
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
import { ref, computed, onMounted, onActivated, onBeforeUnmount, watch } from 'vue'
import { useAdminUsersStore } from '@/stores/adminUsers'

defineOptions({ name: 'AdminUsuarios' })

const store  = useAdminUsersStore()
const users  = computed(() => store.items)

const search = ref('')
const role   = ref('')

const bc = new BroadcastChannel('admin-users')

async function fetchNow() {
  await store.fetchUsers({ search: search.value, rol: role.value, _t: Date.now() })
}

onMounted(fetchNow)
onActivated(fetchNow)                 // <- CLAVE: al volver desde el detalle, vuelve a pedir datos

// refresca cuando la pestaña recupera foco o vienes del historial (BFCache)
const onFocus = () => fetchNow()
const onPageShow = () => fetchNow()
window.addEventListener('focus', onFocus)
window.addEventListener('pageshow', onPageShow)

// Escuchar cambios publicados por el detalle
bc.onmessage = (ev) => { if (ev?.data?.type === 'changed') fetchNow() }

onBeforeUnmount(() => {
  window.removeEventListener('focus', onFocus)
  window.removeEventListener('pageshow', onPageShow)
   bc.close()
})

// filtros
let t = null
function refetchDebounced(){ clearTimeout(t); t = setTimeout(fetchNow, 300) }
watch(search, refetchDebounced)
watch(role,   fetchNow)



// acciones
async function resetPassword(id) {
  try { await store.resetPasswordLink(id); alert('Si existe, enviamos el correo.') }
  catch { alert('Error al solicitar el restablecimiento de contraseña') }
}

async function deleteUser(id) {
  if (!confirm('¿Eliminar usuario?')) return
  try {
    await store.deleteUser(id)
    await fetchNow()                  // asegura coherencia con paginación/servidor
    alert('Usuario eliminado')
  } catch (e) {
    if (e?.response?.status === 403) alert('No se puede eliminar un superadmin')
    else alert('Error al eliminar usuario')
  }
}
</script>