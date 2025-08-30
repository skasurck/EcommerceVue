import axios from 'axios'
import { getAccessToken, refreshAccessToken, logout } from './auth'

export const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
})

let interceptorsSet = false
let refreshPromise = null

const decodeToken = (token) => {
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch {
    return {}
  }
}

const isAuthEndpoint = (url = '') => url.includes('auth/login') || url.includes('auth/refresh')

export const ensureInterceptors = () => {
  if (interceptorsSet) return
  interceptorsSet = true

  api.interceptors.request.use(async (config) => {
    if (isAuthEndpoint(config.url)) return config

    const token = getAccessToken()
    if (!token) return config

    if (refreshPromise) {
      const newToken = await refreshPromise
      config.headers.Authorization = `Bearer ${newToken}`
      return config
    }

    const { exp } = decodeToken(token)
    const now = Math.floor(Date.now() / 1000)

    if (exp && now >= exp - 60) {
      refreshPromise = refreshAccessToken().finally(() => {
        refreshPromise = null
      })
      const newToken = await refreshPromise
      config.headers.Authorization = `Bearer ${newToken}`
      return config
    }

    config.headers.Authorization = `Bearer ${token}`
    return config
  })

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const { response, config } = error
      if (!response || isAuthEndpoint(config?.url)) {
        return Promise.reject(error)
      }

      if (response.status === 401) {
        if (!config._retry) {
          config._retry = true
          try {
            refreshPromise = refreshPromise || refreshAccessToken().finally(() => {
              refreshPromise = null
            })
            const newToken = await refreshPromise
            config.headers.Authorization = `Bearer ${newToken}`
            return api(config)
          } catch (err) {
            logout()
            return Promise.reject(err)
          }
        }
        logout()
      }
      return Promise.reject(error)
    }
  )
}

export default api
