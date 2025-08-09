<template>
  <div class="container">
    <h1>Gestión de pedidos</h1>

    <div class="filtros">
      <label>Estado:</label>
      <select v-model="estadoFiltro" @change="fetchPedidos(1)">
        <option value="">Todos</option>
        <option value="pendiente">Pendiente</option>
        <option value="pagado">Pagado</option>
        <option value="confirmado">Confirmado</option>
        <option value="enviado">Enviado</option>
        <option value="cancelado">Cancelado</option>
      </select>
    </div>

    <div v-if="seleccionados.length" class="bulk-actions">
      <select v-model="estadoBulk">
        <option disabled value="">Estado...</option>
        <option value="pendiente">Pendiente</option>
        <option value="pagado">Pagado</option>
        <option value="confirmado">Confirmado</option>
        <option value="enviado">Enviado</option>
        <option value="cancelado">Cancelado</option>
      </select>
      <button @click="aplicarBulk">Aplicar</button>
    </div>

    <table>
      <thead>
        <tr>
          <th><input type="checkbox" v-model="seleccionarTodo" @change="toggleTodo" /></th>
          <th>ID</th>
          <th>Nombre</th>
          <th>Fecha</th>
          <th>Estado</th>
          <th>Dirección</th>
          <th>Total</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pedido in pedidos" :key="pedido.id">
          <td><input type="checkbox" v-model="seleccionados" :value="pedido.id" /></td>
          <td>{{ pedido.id }}</td>
          <td>{{ pedido.cliente_nombre_completo }}</td>
          <td>{{ formatFecha(pedido.creado) }}</td>
          <td>
            <select v-model="pedido.estado" @change="cambiarEstado(pedido)">
              <option value="pendiente">Pendiente</option>
              <option value="pagado">Pagado</option>
              <option value="confirmado">Confirmado</option>
              <option value="enviado">Enviado</option>
              <option value="cancelado">Cancelado</option>
            </select>
          </td>
          <td>{{ pedido.direccion_resumen }}</td>
          <td>{{ money(pedido.total) }}</td>
          <td><button @click="verDetalle(pedido.id)">Ver/Editar</button></td>
        </tr>
      </tbody>
    </table>

    <div class="paginacion">
      <button :disabled="pagina<=1" @click="fetchPedidos(pagina-1)">Anterior</button>
      <button :disabled="!siguiente" @click="fetchPedidos(pagina+1)">Siguiente</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from '../axios'
import { money, formatFecha } from '../utils/formatters'
import { useRouter } from 'vue-router'

const pedidos = ref([])
const pagina = ref(1)
const siguiente = ref(false)
const estadoFiltro = ref('')
const seleccionados = ref([])
const seleccionarTodo = ref(false)
const estadoBulk = ref('')
const router = useRouter()

async function fetchPedidos(p=1){
  pagina.value = p
  const params = { page: p }
  if (estadoFiltro.value) params.estado = estadoFiltro.value
  const res = await axios.get('pedidos/', { params })
  pedidos.value = res.data.results || res.data
  siguiente.value = !!res.data.next
  seleccionados.value = []
  seleccionarTodo.value = false
}

function toggleTodo(){
  if (seleccionarTodo.value){
    seleccionados.value = pedidos.value.map(p => p.id)
  } else {
    seleccionados.value = []
  }
}

async function cambiarEstado(pedido){
  if (!confirm('¿Cambiar estado del pedido?')){
    fetchPedidos(pagina.value)
    return
  }
  await axios.patch(`pedidos/${pedido.id}/`, { estado: pedido.estado })
  fetchPedidos(pagina.value)
}

async function aplicarBulk(){
  if (!estadoBulk.value) return
  if (!confirm('¿Aplicar cambio de estado a seleccionados?')) return
  const res = await axios.post('pedidos/bulk_update_estado/', { ids: seleccionados.value, estado: estadoBulk.value })
  alert(`Actualizados: ${res.data.updated}, Fallidos: ${res.data.failed.length}`)
  fetchPedidos(pagina.value)
}

function verDetalle(id){
  router.push(`/admin/pedidos/${id}`)
}

fetchPedidos()
</script>
