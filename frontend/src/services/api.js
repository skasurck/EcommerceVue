// src/services/api.js
import api from '../axios'

const API_BASE_URL = 'http://127.0.0.1:8000/api/'

export const obtenerProductos = () => {
  return api.get(`${API_BASE_URL}productos/`)
}
export const obtenerProducto = (id) => api.get(`${API_BASE_URL}productos/${id}/`)

// Carrito
export const obtenerCarrito = () => api.get('carrito/')
export const agregarAlCarrito = (producto, cantidad = 1) =>
  api.post('carrito/', { producto, cantidad })
export const actualizarCarritoItem = (id, cantidad) => api.patch(`carrito/${id}/`, { cantidad })
export const eliminarCarritoItem = (id) => api.delete(`carrito/${id}/`)