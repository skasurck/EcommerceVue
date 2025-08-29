import axios from 'axios'
import { getAccessToken, refreshAccessToken, logout } from './services/auth'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Maneja una única promesa de refresh compartida
let refreshPromise = null

// Decodifica el JWT sin dependencias externas
const decodeToken = (token) => {
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch {
    return {}
  }
}

// Realiza el refresh de manera compartida
const queueRefresh = () => {
  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null
    })
  }
  return refreshPromise
}

api.interceptors.request.use(async (config) => {
  const token = getAccessToken()
  if (!token) return config

  // Si ya hay un refresh en curso, espera a que termine
  if (refreshPromise) {
    const newToken = await queueRefresh()
    config.headers.Authorization = `Bearer ${newToken}`
    return config
  }

  const { exp } = decodeToken(token)
  const now = Math.floor(Date.now() / 1000)

  if (exp && now >= exp - 60) {
    try {
      const newToken = await queueRefresh()
      config.headers.Authorization = `Bearer ${newToken}`
    } catch (e) {
      return Promise.reject(e)
    }
  } else {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { response, config } = error
    if (!response) return Promise.reject(error)

    if (response.status === 401) {
      if (!config._retry) {
        config._retry = true
        try {
          const newToken = await queueRefresh()
          config.headers.Authorization = `Bearer ${newToken}`
          return api(config)
        } catch (e) {
          logout()
          return Promise.reject(e)
        }
      }
      logout()
    }

    return Promise.reject(error)
  }
)

export default api
