import api from '@/axios'

export const obtenerProductos = (params = {}) => api.get('productos/', { params })
export const obtenerProducto = (id) => api.get(`productos/${id}/`)
export const obtenerMarcas = (params = {}) => api.get('marcas/', { params })
export const obtenerRangoPrecios = () => api.get('price-range/')
export const obtenerHomeSlider = (params = {}) => api.get('home-slider/', { params })
export const crearHomeSlide = (payload) =>
  api.post('home-slider/', payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const actualizarHomeSlide = (id, payload) =>
  api.patch(`home-slider/${id}/`, payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const eliminarHomeSlide = (id) => api.delete(`home-slider/${id}/`)

export const obtenerPromoBanners = (params = {}) => api.get('promo-banners/', { params })
export const crearPromoBanner = (payload) =>
  api.post('promo-banners/', payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const actualizarPromoBanner = (id, payload) =>
  api.patch(`promo-banners/${id}/`, payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const eliminarPromoBanner = (id) => api.delete(`promo-banners/${id}/`)

// Carrito
export const obtenerCarrito = () => api.get('carrito/')
export const agregarAlCarrito = (producto, cantidad = 1) =>
  api.post('carrito/', { producto, cantidad })
export const actualizarCarritoItem = (id, cantidad) => api.patch(`carrito/${id}/`, { cantidad })
export const eliminarCarritoItem = (id) => api.delete(`carrito/${id}/`)
