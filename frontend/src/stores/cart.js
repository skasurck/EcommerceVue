import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/http'

export const useCartStore = defineStore('cart', () => {
  // ------------------- STATE -------------------
  const items = ref([]) // Almacenará los items del carrito
  const loading = ref(false)
  const error = ref(null)

  // ------------------- GETTERS -------------------
  /**
   * Devuelve el número total de artículos en el carrito.
   */
  const itemCount = computed(() => items.value.length)

  /**
   * Calcula el precio total del carrito.
   */
  const totalPrice = computed(() => {
    return items.value.reduce((total, item) => {
      const price = item.producto?.precio_rebajado || item.producto?.precio_normal || 0
      return total + (price * item.cantidad)
    }, 0)
  })

  /**
   * Devuelve `true` si el carrito está vacío.
   */
  const isEmpty = computed(() => itemCount.value === 0)

  // ------------------- ACTIONS -------------------

  /**
   * Obtiene los artículos del carrito desde la API y los carga en el estado.
   */
  async function fetchCart() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/carrito/')
      items.value = response.data.results || response.data || []
    } catch (err) {
      error.value = 'No se pudo cargar el carrito.'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Agrega un producto al carrito.
   * @param {object} product - El objeto del producto a agregar.
   * @param {number} quantity - La cantidad a agregar.
   */
  async function addToCart(product, quantity = 1) {
    loading.value = true
    error.value = null
    
    // Buscamos si el producto ya está en el carrito para obtener su 'cart_item_id'
    const existingItem = items.value.find(item => item.producto.id === product.id)

    try {
      if (existingItem) {
        // Si ya existe, actualizamos la cantidad (PUT a /api/carrito/{id}/)
        const newQuantity = existingItem.cantidad + quantity
        await api.put(`/carrito/${existingItem.id}/`, {
          producto: product.id,
          cantidad: newQuantity
        })
      } else {
        // Si es nuevo, lo creamos (POST a /api/carrito/)
        await api.post('/carrito/', {
          producto: product.id,
          cantidad: quantity
        })
      }
      // Después de añadir o actualizar, volvemos a cargar el carrito para tener el estado más reciente.
      await fetchCart()
    } catch (err) {
      error.value = 'No se pudo agregar el producto al carrito.'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Elimina un artículo del carrito.
   * @param {number} itemId - El ID del CartItem a eliminar.
   */
  async function removeFromCart(itemId) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/carrito/${itemId}/`)
      // Actualizamos el estado local para reflejar el cambio inmediatamente
      const index = items.value.findIndex(item => item.id === itemId)
      if (index !== -1) {
        items.value.splice(index, 1)
      }
    } catch (err) {
      error.value = 'No se pudo eliminar el producto del carrito.'
      console.error(err)
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Vacía completamente el carrito local.
   * Útil para cuando el usuario hace logout.
   */
  function clearCart() {
    items.value = []
  }


  return {
    items,
    loading,
    error,
    itemCount,
    totalPrice,
    isEmpty,
    fetchCart,
    addToCart,
    removeFromCart,
    clearCart,
  }
})
