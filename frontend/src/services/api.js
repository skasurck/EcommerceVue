import api from '../axios'

export const obtenerProductos = (params = {}) => api.get('productos/', { params })
export const obtenerProducto = (id) => api.get(`productos/${id}/`)

// Carrito
export const obtenerCarrito = () => api.get('carrito/')
export const agregarAlCarrito = (producto, cantidad = 1) =>
  api.post('carrito/', { producto, cantidad })
export const actualizarCarritoItem = (id, cantidad) => api.patch(`carrito/${id}/`, { cantidad })
export const eliminarCarritoItem = (id) => api.delete(`carrito/${id}/`)
