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
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Estado</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <template v-for="pedido in pedidos" :key="pedido.id">
          <tr>
            <td>{{ pedido.id }}</td>
            <td>{{ pedido.estado }}</td>
            <td><button @click="pedido.editar = !pedido.editar">Editar</button></td>
          </tr>
          <tr v-if="pedido.editar">
            <td colspan="3">
              <div class="editor">
                <div>
                  <label>Estado:</label>
                  <select v-model="pedido.estado">
                    <option value="pendiente">Pendiente</option>
                    <option value="pagado">Pagado</option>
                    <option value="confirmado">Confirmado</option>
                    <option value="enviado">Enviado</option>
                    <option value="cancelado">Cancelado</option>
                  </select>
                </div>
                <div>
                  <h4>Productos</h4>
                  <div v-for="(item,idx) in pedido.detalles" :key="idx">
                    {{ item.producto_nombre || item.producto }}
                    <input type="number" v-model.number="item.cantidad" min="1" />
                    <button @click="pedido.detalles.splice(idx,1)">Eliminar</button>
                  </div>
                  <div>
                    <input type="number" v-model.number="pedido.nuevoProducto" placeholder="ID producto" />
                    <input type="number" v-model.number="pedido.nuevaCantidad" placeholder="Cantidad" />
                    <button @click="agregarItem(pedido)">Añadir</button>
                  </div>
                </div>
                <div>
                  <h4>Dirección</h4>
                  <input v-model="pedido.direccion.calle" placeholder="Calle" />
                  <input v-model="pedido.direccion.ciudad" placeholder="Ciudad" />
                  <input v-model="pedido.direccion.estado" placeholder="Estado" />
                </div>
                <button @click="guardarPedido(pedido)">Guardar</button>
              </div>
            </td>
          </tr>
        </template>
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

const pedidos = ref([])
const pagina = ref(1)
const siguiente = ref(false)
const estadoFiltro = ref('')

async function fetchPedidos(p=1){
  pagina.value = p
  const params = { page: p }
  if (estadoFiltro.value) params.estado = estadoFiltro.value
  const res = await axios.get('pedidos/', { params })
  pedidos.value = res.data.results || res.data
  pedidos.value.forEach(p => {
    p.editar = false
    p.nuevoProducto = null
    p.nuevaCantidad = 1
  })
  siguiente.value = !!res.data.next
}

function agregarItem(pedido){
  if (pedido.nuevoProducto && pedido.nuevaCantidad){
    pedido.detalles.push({ producto: pedido.nuevoProducto, cantidad: pedido.nuevaCantidad, producto_nombre: '' })
    pedido.nuevoProducto = null
    pedido.nuevaCantidad = 1
  }
}

async function guardarPedido(pedido){
  const payload = {
    estado: pedido.estado,
    direccion: pedido.direccion,
    items: pedido.detalles.map(i => ({ producto: i.producto, cantidad: i.cantidad }))
  }
  await axios.put(`pedidos/${pedido.id}/`, payload)
  pedido.editar = false
  fetchPedidos(pagina.value)
}

fetchPedidos()
</script>
