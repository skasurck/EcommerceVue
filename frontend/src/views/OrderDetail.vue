<template>
  <div v-if="pedido" class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <div class="text-sm text-slate-500">Pedidos / <span class="text-slate-700">Detalle</span></div>
        <h1 class="text-2xl font-bold text-slate-800">Pedido #{{ pedido.id }}</h1>
      </div>
      <button @click="cancelar" class="text-sm text-blue-700 hover:underline">← Volver a la lista</button>
    </div>

    <!-- Resumen + Estado -->
    <section class="bg-white border rounded-xl p-4 shadow-sm">
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <div class="text-xs text-slate-500">Creado</div>
          <div class="font-medium text-slate-800">{{ formatFecha(pedido.creado) }}</div>
        </div>
        <div>
          <div class="text-xs text-slate-500">Método de envío</div>
          <div class="font-medium text-slate-800">{{ pedido.metodo_envio_detalle?.nombre || '—' }}</div>
        </div>
        <div>
          <div class="text-xs text-slate-500">Método de pago</div>
          <div class="font-medium text-slate-800">{{ pedido.metodo_pago_display || '—' }}</div>
        </div>
        <div class="flex items-end gap-2">
          <div class="w-full">
            <label class="block text-xs text-slate-500 mb-1">Estado</label>
            <div class="flex items-center gap-2">
              <select
                v-model="pedido.estado"
                class="h-9 rounded-md border border-slate-300 px-2 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="pendiente">Pendiente</option>
                <option value="pagado">Pagado</option>
                <option value="confirmado">Confirmado</option>
                <option value="enviado">Enviado</option>
                <option value="fallido">Fallido</option>
                <option value="cancelado">Cancelado</option>
              </select>
              <span :class="estadoBadge(pedido.estado)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs">
                {{ pedido.estado }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="grid sm:grid-cols-3 gap-4 mt-4">
        <div class="bg-slate-50 rounded-lg p-3 border">
          <div class="text-xs text-slate-500">Subtotal</div>
          <div class="text-lg font-semibold text-slate-800">{{ money(pedido.subtotal) }}</div>
        </div>
        <div class="bg-slate-50 rounded-lg p-3 border">
          <div class="text-xs text-slate-500">Costo envío</div>
          <div class="text-lg font-semibold text-slate-800">{{ money(pedido.costo_envio) }}</div>
        </div>
        <div class="bg-slate-50 rounded-lg p-3 border">
          <div class="text-xs text-slate-500">Total</div>
          <div class="text-lg font-semibold text-slate-800">{{ money(pedido.total) }}</div>
        </div>
      </div>

      <!-- Número de guía -->
      <div class="mt-4">
        <label class="block text-xs text-slate-500 mb-1">Número de guía de rastreo</label>
        <div class="flex items-center gap-2">
          <input
            v-model="pedido.numero_guia"
            type="text"
            placeholder="Sin guía asignada"
            class="h-9 rounded-md border border-slate-300 px-3 text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-72 font-mono"
          />
          <span
            v-if="pedido.numero_guia"
            class="inline-flex items-center gap-1 rounded-full bg-indigo-100 text-indigo-800 text-xs px-2 py-0.5 border border-indigo-200"
          >
            🚚 Con guía
          </span>
        </div>
      </div>
    </section>

    <!-- Artículos -->
    <section class="bg-white border rounded-xl shadow-sm overflow-hidden">
      <div class="p-4 border-b">
        <h2 class="text-lg font-semibold text-slate-800">Artículos</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-slate-50 text-slate-600">
            <tr class="border-b">
              <th class="text-left font-semibold px-3 py-2">Producto</th>
              <th class="text-right font-semibold px-3 py-2 w-32">Precio</th>
              <th class="text-center font-semibold px-3 py-2 w-40">Cantidad</th>
              <th class="text-right font-semibold px-3 py-2 w-36">Subtotal</th>
              <th class="text-right font-semibold px-3 py-2 w-28">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in pedido.detalles" :key="idx" class="border-b last:border-0 hover:bg-slate-50">
              <td class="px-3 py-2">
                <div class="font-medium text-slate-800">{{ item.producto_nombre || item.producto }}</div>
                <div class="text-xs text-slate-500">ID: {{ item.producto }}</div>
              </td>
              <td class="px-3 py-2 text-right text-slate-800">{{ money(item.precio_unitario) }}</td>
              <td class="px-3 py-2">
                <div class="flex items-center justify-center gap-2">
                  <button @click="dec(idx)" class="w-8 h-8 rounded border hover:bg-slate-100">−</button>
                  <input
                    type="number"
                    min="1"
                    v-model.number="item.cantidad"
                    @input="recalc"
                    class="w-16 h-9 text-center rounded border border-slate-300 focus:ring-2 focus:ring-blue-500"
                  />
                  <button @click="inc(idx)" class="w-8 h-8 rounded border hover:bg-slate-100">+</button>
                </div>
              </td>
              <td class="px-3 py-2 text-right font-medium text-slate-800">
                {{ money(item.subtotal || (item.precio_unitario * item.cantidad)) }}
              </td>
              <td class="px-3 py-2">
                <div class="flex justify-end">
                  <button @click="removeItem(idx)" class="px-2 py-1.5 rounded bg-rose-600 hover:bg-rose-700 text-white">
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!pedido.detalles?.length">
              <td colspan="5" class="px-3 py-6 text-center text-slate-500">No hay artículos en este pedido.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Agregar producto -->
      <div class="p-4 border-t bg-slate-50">
        <div class="flex flex-wrap items-end gap-3">
          <div>
            <label class="block text-xs text-slate-500 mb-1">ID producto</label>
            <input
              v-model.number="nuevoProducto"
              type="number"
              placeholder="Ej. 123"
              class="h-9 w-40 rounded border border-slate-300 px-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-xs text-slate-500 mb-1">Cantidad</label>
            <input
              v-model.number="nuevaCantidad"
              type="number"
              min="1"
              class="h-9 w-32 rounded border border-slate-300 px-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button @click="agregarItem" class="h-9 px-4 rounded bg-emerald-600 hover:bg-emerald-700 text-white">
            Añadir
          </button>
        </div>
      </div>
    </section>

    <!-- Dirección -->
    <section class="bg-white border rounded-xl p-4 shadow-sm">
      <h2 class="text-lg font-semibold text-slate-800 mb-3">Dirección</h2>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <input v-model="pedido.direccion.calle"           placeholder="Calle"           class="h-10 rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <input v-model="pedido.direccion.numero_exterior" placeholder="Número"          class="h-10 rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <input v-model="pedido.direccion.colonia"         placeholder="Colonia"         class="h-10 rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <input v-model="pedido.direccion.ciudad"          placeholder="Ciudad"          class="h-10 rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <input v-model="pedido.direccion.estado"          placeholder="Estado"          class="h-10 rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <input v-model="pedido.direccion.codigo_postal"   placeholder="CP"              class="h-10 rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <input v-model="pedido.direccion.email"           placeholder="Email (cliente)" class="h-10 rounded-md border border-slate-300 px-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 lg:col-span-3" />
      </div>
    </section>

    <!-- Historial del cliente -->
    <section class="bg-white border rounded-xl p-4 shadow-sm">
      <h2 class="text-lg font-semibold text-slate-800 mb-3">Historial del cliente</h2>
      <div v-if="summary" class="grid sm:grid-cols-3 gap-3">
        <div class="bg-slate-50 rounded-lg p-3 border">
          <div class="text-xs text-slate-500">Pedidos</div>
          <div class="text-lg font-semibold text-slate-800">{{ summary.orders_count }}</div>
        </div>
        <div class="bg-slate-50 rounded-lg p-3 border">
          <div class="text-xs text-slate-500">Gastado</div>
          <div class="text-lg font-semibold text-slate-800">{{ money(summary.total_spent) }}</div>
        </div>
        <div class="bg-slate-50 rounded-lg p-3 border">
          <div class="text-xs text-slate-500">Ticket promedio</div>
          <div class="text-lg font-semibold text-slate-800">{{ money(summary.avg_ticket) }}</div>
        </div>
      </div>
      <div v-else class="text-slate-500 text-sm">Sin datos (ingresa email para consultar).</div>
    </section>

    <!-- Warning si vacío -->
    <div v-if="!pedido.detalles.length" class="text-sm text-rose-600">
      El pedido no puede quedar vacío.
    </div>

    <!-- Barra de acciones fija -->
    <div class="sticky bottom-0 bg-white/95 backdrop-blur border-t p-3">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="text-sm text-slate-600">
          <span class="mr-3">Subtotal: <span class="font-medium text-slate-800">{{ money(pedido.subtotal) }}</span></span>
          <span class="mr-3">Envío: <span class="font-medium text-slate-800">{{ money(pedido.costo_envio) }}</span></span>
          <span>Total: <span class="font-semibold text-slate-900">{{ money(pedido.total) }}</span></span>
        </div>
        <div class="flex items-center gap-2">
          <button @click="cancelar" class="px-4 py-2 rounded border border-slate-300 hover:bg-slate-100 text-sm">
            Cancelar
          </button>
          <button
            :disabled="!pedido.detalles.length"
            @click="guardar"
            class="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm"
          >
            Guardar cambios
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/axios'
import { money, formatFecha } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()
const pedido = ref(null)
const summary = ref(null)
const nuevoProducto = ref(null)
const nuevaCantidad = ref(1)

const estadoBadge = (estado) => ({
  'pendiente':  'bg-amber-100 text-amber-800 border border-amber-200',
  'pagado':     'bg-emerald-100 text-emerald-800 border border-emerald-200',
  'confirmado': 'bg-blue-100 text-blue-800 border border-blue-200',
  'enviado':    'bg-indigo-100 text-indigo-800 border border-indigo-200',
  'fallido':    'bg-rose-100 text-rose-800 border border-rose-200',
  'cancelado':  'bg-rose-100 text-rose-800 border border-rose-200',
}[estado] || 'bg-slate-100 text-slate-700 border')

async function cargar() {
  const res = await axios.get(`pedidos/${route.params.id}/`)
  pedido.value = res.data
  recalc()
  obtenerResumen()
}

async function agregarItem() {
  if (nuevoProducto.value && nuevaCantidad.value) {
    const res = await axios.get(`productos/${nuevoProducto.value}/`)
    const prod = res.data
    const precio = Number(prod.precio_rebajado || prod.precio_normal)
    pedido.value.detalles.push({
      producto: prod.id,
      producto_nombre: prod.nombre,
      precio_unitario: precio,
      cantidad: nuevaCantidad.value,
      subtotal: precio * nuevaCantidad.value
    })
    recalc()
    nuevoProducto.value = null
    nuevaCantidad.value = 1
  }
}

async function guardar() {
  if (!pedido.value.detalles.length) return alert('El pedido no puede quedar vacío.')
  const payload = {
    estado: pedido.value.estado,
    numero_guia: pedido.value.numero_guia ?? '',
    direccion: pedido.value.direccion,
    items: pedido.value.detalles.map(i => ({ producto: i.producto, cantidad: i.cantidad }))
  }
  await axios.put(`pedidos/${pedido.value.id}/`, payload)
  router.push('/admin/pedidos')
}

function cancelar() {
  router.push('/admin/pedidos')
}

async function obtenerResumen() {
  const email = pedido.value?.direccion?.email
  if (!email) { summary.value = null; return }
  const res = await axios.get('clientes/summary/', { params: { email } })
  summary.value = res.data
}

function recalc() {
  if (!pedido.value) return
  let sub = 0
  pedido.value.detalles.forEach(it => {
    it.cantidad = Math.max(1, Number(it.cantidad))
    it.subtotal = Number(it.precio_unitario) * Number(it.cantidad)
    sub += it.subtotal
  })
  pedido.value.subtotal = sub
  pedido.value.total = sub + Number(pedido.value.costo_envio || 0)
}

function inc(idx) {
  const it = pedido.value.detalles[idx]
  it.cantidad++
  recalc()
}

function dec(idx) {
  const it = pedido.value.detalles[idx]
  if (it.cantidad > 1) {
    it.cantidad--
    recalc()
  }
}

function removeItem(idx) {
  pedido.value.detalles.splice(idx, 1)
  recalc()
  if (!pedido.value.detalles.length) alert('El pedido no puede quedar vacío.')
}

cargar()
</script>
