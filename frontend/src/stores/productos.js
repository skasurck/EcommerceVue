// stores/productos.js
export const useProductoStore = defineStore('producto', {
  state: () => ({ cache: {} }),
  actions: {
    async get(id) {
      if (!this.cache[id]) {
        const { data } = await obtenerProducto(id)
        this.cache[id] = data
      }
      return this.cache[id]
    }
  }
})
