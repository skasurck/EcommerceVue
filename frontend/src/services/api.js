// src/services/api.js
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000/api/'

export const obtenerProductos = () => {
  return axios.get(`${API_BASE_URL}productos/`)
}
