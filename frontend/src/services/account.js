import api from '@/axios'

export const obtenerPerfil = () => api.get('profile/')
export const actualizarPerfil = (data) => api.put('profile/', data)
export const subirFotoPerfil = (file) => {
  const form = new FormData()
  form.append('foto', file)
  return api.post('profile/foto/', form, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const cambiarPassword = (data) => api.post('change-password/', data)

export const obtenerDirecciones = () => api.get('direcciones/')
export const crearDireccion = (data) => api.post('direcciones/', data)
export const actualizarDireccion = (id, data) => api.put(`direcciones/${id}/`, data)
export const eliminarDireccion = (id) => api.delete(`direcciones/${id}/`)

export const obtenerPedidos = (page = 1) => api.get('pedidos/', { params: { page } })
export const obtenerPedido = (id) => api.get(`pedidos/${id}/`)
