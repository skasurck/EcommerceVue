import { defineStore } from 'pinia'
import api from '../axios'

export const useCarritoStore = defineStore('carrito', {
  state: () => ({ items: [] }),
  actions: {
    async cargar() {
      const res = await api.get('carrito/')
      this.items = res.data
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
      this.items = this.items.filter(i => i.id !== id)
    },
  }
})