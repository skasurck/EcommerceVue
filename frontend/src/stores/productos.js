// stores/productos.js
import { defineStore } from 'pinia'
import { obtenerProducto } from '../services/api.js'

export const useProductoStore = defineStore('producto', {
  state: () => ({ cache: {} }),
  actions: {
    async get(id) {
      if (!this.cache[id]) {
        try {
          const { data } = await obtenerProducto(id)
          console.log('Fetched product data:', data)
          this.cache[id] = data
        } catch (error) {
          console.error('Error fetching product:', error)
          this.cache[id] = null
        }
      }
      return this.cache[id]
    }
  }
})
