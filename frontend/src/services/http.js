import axios from 'axios'
import { getAccessToken, getRefreshToken, refreshAccessToken, logout } from './auth'

// ===== Base URL =====
const buildBaseURL = () => {
  const rawBase = import.meta.env?.VITE_API_BASE?.trim?.()
  if (rawBase) return `${rawBase.replace(/\/+$/, '')}/api/`

  if (import.meta.env?.DEV) return 'http://localhost:8000/api/'

  if (typeof window !== 'undefined' && window.location?.origin) {
    return `${window.location.origin.replace(/\/+$/, '')}/api/`
  }
  return '/api/'
}

// ===== Axios instance =====
export const api = axios.create({
  baseURL: buildBaseURL(),
  timeout: 30000,
  withCredentials: true,        // OK si usas cookies en otros endpoints; para JWT puro no es necesario
  xsrfCookieName: 'csrftoken',  // idem
  xsrfHeaderName: 'X-CSRFToken',
  headers: { 'Content-Type': 'application/json' },
})

let interceptorsSet = false
let refreshPromise = null

// ===== Helpers =====
const b64UrlDecode = (str) => {
  try {
    // Corrige base64 url-safe y padding
    str = str.replace(/-/g, '+').replace(/_/g, '/')
    const pad = str.length % 4
    if (pad) str += '='.repeat(4 - pad)
    return atob(str)
  } catch {
    return ''
  }
}

const decodeToken = (token) => {
  try {
    const payload = token.split('.')[1]
    return JSON.parse(b64UrlDecode(payload) || '{}')
  } catch {
    return {}
  }
}

const isAuthEndpoint = (url = '') =>
  url.includes('auth/login') ||
  url.includes('auth/refresh') || // alias que agregaste en backend
  url.includes('token/')          // por si usas /api/token/ y /api/token/refresh/

// ===== Interceptors =====
export const ensureInterceptors = () => {
  if (interceptorsSet) return
  interceptorsSet = true

  // --- REQUEST ---
  api.interceptors.request.use(async (config) => {
    if (isAuthEndpoint(config.url)) return config

    const token = getAccessToken()
    if (!token) return config

    // Si hay un refresh en curso, espera y usa el nuevo access
    if (refreshPromise) {
      const newToken = await refreshPromise
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${newToken}`
      return config
    }

    // Pre-refresh si el access expira en <=60s y existe refresh
    const { exp } = decodeToken(token)
    const now = Math.floor(Date.now() / 1000)
    const hasRefresh = !!getRefreshToken()

    if (hasRefresh && exp && now >= exp - 60) {
      refreshPromise = refreshAccessToken().finally(() => { refreshPromise = null })
      const newToken = await refreshPromise
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${newToken}`
      return config
    }

    // Usa el access actual
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
    return config
  })

  // --- RESPONSE ---
  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const { response, config } = error
      if (!response || isAuthEndpoint(config?.url)) {
        return Promise.reject(error)
      }

      // Intenta refresh en 401 o 403 (tu caso)
      if (response.status === 401 || response.status === 403) {
        const refresh = getRefreshToken()
        if (!refresh) {
          // Si tampoco hay access token, es un invitado — no redirigir al login
          if (getAccessToken()) logout()
          return Promise.reject(error)
        }

        if (!config._retry) {
          config._retry = true
          try {
            // Evita múltiples refresh simultáneos
            refreshPromise = refreshPromise || refreshAccessToken().finally(() => { refreshPromise = null })
            const newToken = await refreshPromise
            config.headers = config.headers || {}
            config.headers.Authorization = `Bearer ${newToken}`
            return api(config) // reintento con el nuevo access
          } catch (err) {
            logout()
            return Promise.reject(err)
          }
        }
        // Ya lo intentamos una vez y falló
        logout()
      }

      return Promise.reject(error)
    }
  )
}

export default api
