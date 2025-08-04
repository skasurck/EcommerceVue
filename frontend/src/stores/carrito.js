import { defineStore } from 'pinia'
import api from '../axios'

export const useCarritoStore = defineStore('carrito', {
  state: () => ({ items: [], reservaExpira: null }),
  getters: {
    precioUnitario: () => (item) => {
      if (!item.producto) return 0
      let precio = +(item.producto.precio_rebajado ?? item.producto.precio_normal)
      const tiers = item.producto.precios_escalonados || []
      for (const tier of tiers) {
        if (item.cantidad >= tier.cantidad_minima) {
          const p = +tier.precio_unitario
          if (p < precio) precio = p
        }
      }
      return precio
    },
    totalCantidad: (state) => state.items.reduce((s, i) => s + i.cantidad, 0),
    subtotal(state) {
      return state.items.reduce((sum, i) => sum + this.precioUnitario(i) * i.cantidad, 0)
    },
  },
  actions: {
    async cargar() {
      const res = await api.get('carrito/')
      this.items = res.data
      this.reservaExpira = res.data[0]?.reserva_expira || null
    },
    async agregar(producto, cantidad = 1) {
      if (!producto || producto.stock <= 0) return
      const existente = this.items.find(i => i.producto.id === producto.id)
      const max = producto.stock + (existente?.cantidad || 0)
      const nuevaCantidad = (existente?.cantidad || 0) + cantidad
      if (nuevaCantidad > max) return
      if (existente) {
        await this.actualizar(existente.id, nuevaCantidad)
      } else {
        await api.post('carrito/', { producto: producto.id, cantidad })
        await this.cargar()
      }
    },
    async actualizar(id, cantidad) {
      const item = this.items.find(i => i.id === id)
      if (!item) return
      const max = item.producto.stock + item.cantidad
      if (cantidad > max) return
      await api.patch(`carrito/${id}/`, { cantidad })
      await this.cargar()
    },
    async eliminar(id) {
      await api.delete(`carrito/${id}/`)
      await this.cargar()
    },
  }
})
