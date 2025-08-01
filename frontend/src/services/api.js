// src/services/api.js
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000/api/'

export const obtenerProductos = () => {
  return axios.get(`${API_BASE_URL}productos/`)
}
export const obtenerProducto = (id) =>
    axios.get(`productos/${id}/`)

// Carrito
export const obtenerCarrito = () => axios.get('carrito/')
export const agregarAlCarrito = (producto, cantidad = 1) =>
  axios.post('carrito/', { producto, cantidad })
export const actualizarCarritoItem = (id, cantidad) =>
  axios.patch(`carrito/${id}/`, { cantidad })
export const eliminarCarritoItem = (id) => axios.delete(`carrito/${id}/`)