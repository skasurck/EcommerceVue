import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor to add the Authorization header with the token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor de respuesta para manejar expiración
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true
      try {
        const refresh = localStorage.getItem('refresh')
        const res = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: refresh
        })

        localStorage.setItem('access', res.data.access)
        originalRequest.headers.Authorization = `Bearer ${res.data.access}`
        return api(originalRequest)
      } catch (err) {
        console.error('Error al refrescar token', err)
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        window.location.href = '/login'
        return Promise.reject(err)
      }
    }
    return Promise.reject(error)
  }
)

export default api