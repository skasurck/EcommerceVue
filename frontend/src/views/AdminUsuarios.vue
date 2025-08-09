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
          <th class="border px-2 py-1"></th>
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
          <td class="border px-2 py-1"><router-link :to="`/admin/usuarios/${u.id}`" class="underline">Ver</router-link></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminUsersStore } from '../stores/adminUsers'

defineOptions({ name: 'AdminUsuarios' })

const store = useAdminUsersStore()
const users = ref([])
const search = ref('')
const role = ref('')

async function fetch() {
  const data = await store.fetchUsers({ search: search.value, rol: role.value })
  users.value = data.results || data
}

onMounted(fetch)
</script>
