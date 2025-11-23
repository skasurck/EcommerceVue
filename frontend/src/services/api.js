import api from '../axios'

export const obtenerProductos = (params = {}) => api.get('productos/', { params })
export const obtenerProducto = (id) => api.get(`productos/${id}/`)
export const obtenerMarcas = (params = {}) => api.get('marcas/', { params })
export const obtenerRangoPrecios = () => api.get('price-range/')

// Carrito
export const obtenerCarrito = () => api.get('carrito/')
export const agregarAlCarrito = (producto, cantidad = 1) =>
  api.post('carrito/', { producto, cantidad })
export const actualizarCarritoItem = (id, cantidad) => api.patch(`carrito/${id}/`, { cantidad })
export const eliminarCarritoItem = (id) => api.delete(`carrito/${id}/`)
