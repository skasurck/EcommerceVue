<template>
  <div v-if="pedido" class="container">
    <h1>Pedido #{{ pedido.id }}</h1>

    <section>
      <h2>Resumen</h2>
      <div>Creado: {{ formatFecha(pedido.creado) }}</div>
      <div>
        Estado:
        <select v-model="pedido.estado">
          <option value="pendiente">Pendiente</option>
          <option value="pagado">Pagado</option>
          <option value="confirmado">Confirmado</option>
          <option value="enviado">Enviado</option>
          <option value="cancelado">Cancelado</option>
        </select>
      </div>
      <div>Método de envío: {{ pedido.metodo_envio_detalle?.nombre }}</div>
      <div>Método de pago: {{ pedido.metodo_pago_display }}</div>
      <div>Subtotal: {{ money(pedido.subtotal) }}</div>
      <div>Costo envío: {{ money(pedido.costo_envio) }}</div>
      <div>Total: {{ money(pedido.total) }}</div>
    </section>

    <section>
      <h2>Artículos</h2>
      <div v-for="(item,idx) in pedido.detalles" :key="idx">
        {{ item.producto_nombre || item.producto }} - {{ money(item.precio_unitario) }}
        <input type="number" v-model.number="item.cantidad" min="1" />
        <button @click="pedido.detalles.splice(idx,1)">Eliminar</button>
      </div>
      <div>
        <input type="number" v-model.number="nuevoProducto" placeholder="ID producto" />
        <input type="number" v-model.number="nuevaCantidad" placeholder="Cantidad" />
        <button @click="agregarItem">Añadir</button>
      </div>
    </section>

    <section>
      <h2>Dirección</h2>
      <input v-model="pedido.direccion.calle" placeholder="Calle" />
      <input v-model="pedido.direccion.numero_exterior" placeholder="Número" />
      <input v-model="pedido.direccion.colonia" placeholder="Colonia" />
      <input v-model="pedido.direccion.ciudad" placeholder="Ciudad" />
      <input v-model="pedido.direccion.estado" placeholder="Estado" />
      <input v-model="pedido.direccion.codigo_postal" placeholder="CP" />
    </section>

    <section>
      <h2>Historial del cliente</h2>
      <div v-if="summary">Pedidos: {{ summary.orders_count }} | Gastado: {{ money(summary.total_spent) }} | Ticket promedio: {{ money(summary.avg_ticket) }}</div>
    </section>

    <button @click="guardar">Guardar</button>
    <button @click="cancelar">Cancelar</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../axios'
import { money, formatFecha } from '../utils/formatters'

const route = useRoute()
const router = useRouter()
const pedido = ref(null)
const summary = ref(null)
const nuevoProducto = ref(null)
const nuevaCantidad = ref(1)

async function cargar(){
  const res = await axios.get(`pedidos/${route.params.id}/`)
  pedido.value = res.data
  obtenerResumen()
}

function agregarItem(){
  if (nuevoProducto.value && nuevaCantidad.value){
    pedido.value.detalles.push({ producto: nuevoProducto.value, cantidad: nuevaCantidad.value, producto_nombre: '' })
    nuevoProducto.value = null
    nuevaCantidad.value = 1
  }
}

async function guardar(){
  const payload = {
    estado: pedido.value.estado,
    direccion: pedido.value.direccion,
    items: pedido.value.detalles.map(i => ({ producto: i.producto, cantidad: i.cantidad }))
  }
  await axios.put(`pedidos/${pedido.value.id}/`, payload)
  router.push('/admin/pedidos')
}

function cancelar(){
  router.push('/admin/pedidos')
}

async function obtenerResumen(){
  const email = pedido.value.direccion.email
  const res = await axios.get('clientes/summary/', { params: { email } })
  summary.value = res.data
}

cargar()
</script>
