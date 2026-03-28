<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">

    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-slate-800">Gestión de usuarios</h2>
      <p class="text-sm text-slate-500 mt-1">Administra los usuarios registrados en la plataforma</p>
    </div>

    <!-- Filters -->
    <div class="bg-white border border-slate-200 rounded-xl p-4 mb-6 shadow-sm">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1">
          <label class="block text-xs font-medium text-slate-500 mb-1">Buscar usuario</label>
          <input
            v-model="search"
            placeholder="Nombre, email o username..."
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:border-transparent transition"
          />
        </div>
        <div class="sm:w-56">
          <label class="block text-xs font-medium text-slate-500 mb-1">Rol</label>
          <select
            v-model="role"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:border-transparent transition bg-white"
          >
            <option value="">Todos los roles</option>
            <option value="cliente">Cliente</option>
            <option value="admin">Administrador</option>
            <option value="super_admin">Super Administrador</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="users.length === 0" class="bg-white border border-slate-200 rounded-xl p-12 text-center shadow-sm">
      <div class="text-slate-300 text-5xl mb-4">👤</div>
      <p class="text-slate-500 font-medium">No se encontraron usuarios</p>
      <p class="text-slate-400 text-sm mt-1">Intenta ajustar los filtros de búsqueda</p>
    </div>

    <!-- Desktop table (lg+) -->
    <div v-else class="hidden lg:block bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200">
            <th class="text-left px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wide">Username</th>
            <th class="text-left px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wide">Nombre</th>
            <th class="text-left px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wide">Email</th>
            <th class="text-left px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wide">Rol</th>
            <th class="text-left px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wide">2FA</th>
            <th class="text-left px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wide">Último acceso</th>
            <th class="text-left px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wide">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="u in users"
            :key="u.id"
            class="hover:bg-slate-50 transition-colors"
          >
            <td class="px-4 py-3 text-slate-700 font-medium">{{ u.username }}</td>
            <td class="px-4 py-3 text-slate-800">{{ u.nombre_completo }}</td>
            <td class="px-4 py-3 text-slate-600">{{ u.email }}</td>
            <td class="px-4 py-3">
              <span :class="u.rol === 'super_admin' ? 'bg-purple-100 text-purple-700' : u.rol === 'admin' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                {{ u.rol }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span
                :class="u.estado_2fa ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
              >
                {{ u.estado_2fa ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-4 py-3 text-slate-500 text-xs">{{ u.ultimo_acceso }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <router-link
                  :to="`/admin/usuarios/${u.id}`"
                  class="text-slate-600 hover:text-slate-900 font-medium text-xs underline underline-offset-2 transition-colors"
                >
                  Ver detalle
                </router-link>
                <button
                  @click="resetPassword(u.id)"
                  class="bg-slate-100 hover:bg-blue-100 text-slate-600 hover:text-blue-700 px-2.5 py-1 text-xs rounded-lg font-medium transition-colors border border-slate-200 hover:border-blue-200"
                >
                  Restablecer pw
                </button>
                <button
                  v-if="u.rol !== 'super_admin'"
                  @click="deleteUser(u.id)"
                  class="bg-slate-100 hover:bg-red-100 text-slate-600 hover:text-red-700 px-2.5 py-1 text-xs rounded-lg font-medium transition-colors border border-slate-200 hover:border-red-200"
                >
                  Eliminar
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile cards (< lg) -->
    <div v-if="users.length > 0" class="lg:hidden space-y-3">
      <div
        v-for="u in users"
        :key="u.id"
        class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm"
      >
        <!-- Row 1: nombre + rol badge -->
        <div class="flex items-center justify-between gap-2 mb-2">
          <span class="font-semibold text-slate-800 text-sm leading-tight">{{ u.nombre_completo }}</span>
          <span :class="u.rol === 'super_admin' ? 'bg-purple-100 text-purple-700' : u.rol === 'admin' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium whitespace-nowrap shrink-0">
            {{ u.rol }}
          </span>
        </div>

        <!-- Row 2: email -->
        <p class="text-xs text-slate-500 mb-2 truncate">{{ u.email }}</p>

        <!-- Row 3: username + 2FA -->
        <div class="flex items-center gap-3 mb-3 text-xs text-slate-600">
          <span class="flex items-center gap-1">
            <span class="font-medium text-slate-500">@</span>{{ u.username }}
          </span>
          <span class="text-slate-300">·</span>
          <span class="flex items-center gap-1">
            <span class="font-medium text-slate-500">2FA:</span>
            <span
              :class="u.estado_2fa ? 'text-emerald-600' : 'text-slate-400'"
              class="font-medium"
            >
              {{ u.estado_2fa ? 'Sí' : 'No' }}
            </span>
          </span>
        </div>

        <!-- Row 4: actions -->
        <div class="flex flex-wrap gap-2 pt-3 border-t border-slate-100">
          <router-link
            :to="`/admin/usuarios/${u.id}`"
            class="flex-1 text-center bg-slate-800 hover:bg-slate-700 text-white px-3 py-2 text-xs rounded-lg font-medium transition-colors"
          >
            Ver detalle
          </router-link>
          <button
            @click="resetPassword(u.id)"
            class="flex-1 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 px-3 py-2 text-xs rounded-lg font-medium transition-colors"
          >
            Restablecer pw
          </button>
          <button
            v-if="u.rol !== 'super_admin'"
            @click="deleteUser(u.id)"
            class="flex-1 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 px-3 py-2 text-xs rounded-lg font-medium transition-colors"
          >
            Eliminar
          </button>
        </div>
      </div>
    </div>

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
