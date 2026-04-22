import { defineStore } from 'pinia'
import { obtenerListaDeseos, agregarAListaDeseos, eliminarDeListaDeseos } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { trackEvento } from '@/composables/useTracking'

export const useWishlistStore = defineStore('wishlist', {
  state: () => ({
    items: [],
    _loaded: false,
  }),

  getters: {
    total: (state) => state.items.length,
    esFavorito: (state) => (productoId) =>
      state.items.some((i) => i.producto_id === productoId),
    itemId: (state) => (productoId) =>
      state.items.find((i) => i.producto_id === productoId)?.id ?? null,
  },

  actions: {
    async cargar() {
      const auth = useAuthStore()
      if (!auth.isAuthenticated) return
      try {
        const { data } = await obtenerListaDeseos()
        this.items = Array.isArray(data) ? data : (data?.results ?? [])
        this._loaded = true
      } catch {
        // ignore
      }
    },

    async ensureLoaded() {
      if (!this._loaded) await this.cargar()
    },

    async toggle(productoId) {
      const auth = useAuthStore()
      if (!auth.isAuthenticated) return false

      await this.ensureLoaded()

      if (this.esFavorito(productoId)) {
        const id = this.itemId(productoId)
        await eliminarDeListaDeseos(id)
        this.items = this.items.filter((i) => i.id !== id)
        trackEvento('wishlist_remove', { producto_id: productoId })
        return false
      } else {
        const { data } = await agregarAListaDeseos(productoId)
        this.items.push(data)
        trackEvento('wishlist_add', { producto_id: productoId })
        return true
      }
    },

    clear() {
      this.items = []
      this._loaded = false
    },
  },
})
