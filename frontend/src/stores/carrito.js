import { defineStore } from 'pinia'
import api from '../axios'

export const useCarritoStore = defineStore('carrito', {
  state: () => ({
    items: [],
    reservaExpira: null,
  }),
  getters: {
    totalCantidad: (state) => state.items.reduce((s, i) => s + i.cantidad, 0),
  },
  actions: {
    async cargar() {
      const res = await api.get('carrito/')
      this.items = res.data
      this.reservaExpira = res.data[0]?.reserva_expira || null
    },
    async agregar(producto, cantidad = 1) {
      await api.post('carrito/', { producto, cantidad })
      await this.cargar()
    },
    async actualizar(id, cantidad) {
      await api.patch(`carrito/${id}/`, { cantidad })
      await this.cargar()
    },
    async eliminar(id) {
      await api.delete(`carrito/${id}/`)
      await this.cargar()
    },
  }
})
