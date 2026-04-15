import { defineStore } from 'pinia'
import api from '@/axios'

/** Normaliza la forma del carrito devuelto por la API */
function normalizeItems(data) {
  // Acepta: array directo, {items: [...]}, {results: [...]}
  const raw = Array.isArray(data)
    ? data
    : Array.isArray(data?.items)
      ? data.items
      : Array.isArray(data?.results)
        ? data.results
        : []

  // Asegura estructura mínima por ítem
  return raw
    .filter(Boolean)
    .map(i => ({
      id: i.id ?? i.pk ?? crypto.randomUUID(),
      cantidad: Number(i.cantidad ?? i.qty ?? 0),
      // producto puede venir expandido o solo id
      producto: i.producto && typeof i.producto === 'object' ? i.producto : null,
      reserva_expira: i.reserva_expira ?? i.expira ?? null,
    }))
}

export const useCarritoStore = defineStore('carrito', {
  state: () => ({
    items: /** @type {Array<{id:string|number,cantidad:number,producto:any,reserva_expira?:string|null}>} */ ([]),
    reservaExpira: /** @type {string|null} */ (null),
    _loaded: false,
    drawerOpen: false,
    lastAdded: /** @type {any|null} */ (null),
    /** Mensaje de error expuesto para que los componentes puedan mostrarlo al usuario */
    error: /** @type {string|null} */ (null),
    /** ID del producto que está siendo agregado ahora mismo (previene doble-clic) */
    addingProductId: /** @type {number|string|null} */ (null),
  }),

  getters: {
    precioUnitario: () => (item) => {
      const p = item?.producto
      if (!p) return 0
      let precio = +(p.precio_rebajado ?? p.precio_normal ?? 0)
      const tiers = Array.isArray(p.precios_escalonados) ? p.precios_escalonados : []
      for (const tier of tiers) {
        const min = Number(tier?.cantidad_minima ?? 0)
        const pu  = Number(tier?.precio_unitario ?? NaN)
        if (item.cantidad >= min && !Number.isNaN(pu) && pu < precio) precio = pu
      }
      return Number.isFinite(precio) ? precio : 0
    },

    totalCantidad: (state) =>
      Array.isArray(state.items) ? state.items.reduce((s, i) => s + Number(i.cantidad || 0), 0) : 0,

    subtotal() {
      if (!Array.isArray(this.items)) return 0
      return this.items.reduce((sum, i) => sum + this.precioUnitario(i) * Number(i.cantidad || 0), 0)
    },
  },

  actions: {
    async ensureSession() {
      if (this._loaded) return
      await this.cargar()
    },

    _setError(msg) {
      this.error = msg
      // Limpia el error automáticamente después de 5 segundos
      setTimeout(() => { if (this.error === msg) this.error = null }, 5000)
    },

    async cargar() {
      try {
        const res = await api.get('carrito/')
        const items = normalizeItems(res?.data)
        this.items = items
        // toma la expiración más próxima si existe
        this.reservaExpira = items.length ? (items[0]?.reserva_expira ?? null) : null
        this._loaded = true
      } catch (err) {
        console.error('[carrito] Error al cargar:', err)
        this._setError('No se pudo cargar el carrito. Verifica tu conexión.')
      }
    },

    async agregar(producto, cantidad = 1) {
      if (!producto) return
      // Previene doble-clic: si ya se está agregando este producto, ignorar
      if (this.addingProductId === producto.id) return
      await this.ensureSession()
      const items = Array.isArray(this.items) ? this.items : []
      const existente = items.find(i => i?.producto?.id === producto.id)
      // Si no hay nada en carrito y stock es 0, no agregar
      if (!existente && Number(producto.stock ?? 0) <= 0) return
      const nuevaCantidad = Number(existente?.cantidad ?? 0) + Number(cantidad ?? 0)

      this.addingProductId = producto.id
      try {
        if (existente) {
          await this._patchCarrito(existente.id, nuevaCantidad)
        } else {
          await api.post('carrito/', { producto: producto.id, cantidad: Number(cantidad || 1) })
          await this.cargar()
        }
        this.error = null
        this.lastAdded = { ...producto, cantidadAgregada: Number(cantidad || 1) }
        this.drawerOpen = true
      } catch (err) {
        console.error('[carrito] Error al agregar:', err)
        const msg = err?.response?.data?.detail || err?.response?.data?.non_field_errors?.[0] || 'No se pudo agregar el producto al carrito.'
        this._setError(msg)
      } finally {
        this.addingProductId = null
      }
    },

    // Actualiza cantidad directamente, sin re-validar stock en cliente (el servidor valida)
    async _patchCarrito(id, cantidad) {
      try {
        await api.patch(`carrito/${id}/`, { cantidad: Number(cantidad) })
        await this.cargar()
      } catch (err) {
        console.error('[carrito] Error al actualizar:', err)
        const msg = err?.response?.data?.detail || 'No se pudo actualizar la cantidad.'
        this._setError(msg)
      }
    },

    async actualizar(id, cantidad) {
      await this.ensureSession()
      const items = Array.isArray(this.items) ? this.items : []
      const item = items.find(i => i.id === id)
      if (!item) return
      await this._patchCarrito(id, cantidad)
    },

    async eliminar(id) {
      await this.ensureSession()
      try {
        await api.delete(`carrito/${id}/`)
        await this.cargar()
      } catch (err) {
        console.error('[carrito] Error al eliminar:', err)
        this._setError('No se pudo eliminar el producto del carrito.')
      }
    },

    async limpiar() {
      try {
        await api.delete('carrito/clear/')
      } catch (err) {
        console.error('[carrito] Error al limpiar:', err)
      }
      this.items = []
      this.reservaExpira = null
    },
  },
})
