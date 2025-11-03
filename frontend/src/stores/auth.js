import { defineStore } from 'pinia'
import api from '../services/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // Tokens persistidos para mantener la sesión al recargar la página
    accessToken: localStorage.getItem('accessToken') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null,
    inactivityTimer: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },
  actions: {
    /**
     * Guarda los tokens en el estado y en localStorage
     */
    setTokens(access, refresh) {
      this.accessToken = access
      this.refreshToken = refresh
      if (access) {
        localStorage.setItem('accessToken', access)
      } else {
        localStorage.removeItem('accessToken')
      }
      if (refresh) {
        localStorage.setItem('refreshToken', refresh)
      } else {
        localStorage.removeItem('refreshToken')
      }
    },
    /**
     * Realiza login contra el backend y guarda tokens y usuario
     * @param {{username:string, password:string}} creds
     * @param {AbortSignal} [signal]
     */
    async login({ username, password }, signal) {
      const { data } = await api.post('auth/login/', { username, password }, { signal })
      if (import.meta.env.DEV) console.debug('login response', data)

      const access =
        data.access ||
        data.access_token ||
        data.token ||
        data.auth_token ||
        data?.jwt?.access ||
        data?.tokens?.access ||
        null

      const refresh =
        data.refresh ||
        data.refresh_token ||
        data?.jwt?.refresh ||
        data?.tokens?.refresh ||
        null

      if (!access) {
        const detail = data.detail || (Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : null)
        if (detail) {
          if (import.meta.env.DEV) console.debug('login rejected', detail)
          const err = new Error(detail)
          err.response = { status: 401 }
          throw err
        }
        if (import.meta.env.DEV) console.debug('login without tokens', data)
        throw new Error('Respuesta inválida del servidor')
      }

      this.setTokens(access, refresh)
      if (data.user) {
        this.user = data.user
        localStorage.setItem('user', JSON.stringify(data.user))
      }
      this.resetInactivityTimer()
      return data
    },
    /**
     * Cierra sesión y limpia estado
     */
    logout() {
      this.setTokens(null, null)
      this.user = null
      localStorage.removeItem('user')
      this.clearInactivityTimer()
    },
    hasRole(role) {
      return this.user?.rol === role
    },
    hasAnyRole(roles) {
      return roles.includes(this.user?.rol)
    },
    checkLogin() {
      this.accessToken = localStorage.getItem('accessToken') || null
      this.refreshToken = localStorage.getItem('refreshToken') || null
      this.user = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null
      if (this.isAuthenticated) {
        this.resetInactivityTimer()
      }
    },
    clearInactivityTimer() {
      if (this.inactivityTimer) {
        clearTimeout(this.inactivityTimer)
        this.inactivityTimer = null
      }
    },
    resetInactivityTimer() {
      this.clearInactivityTimer()
      this.inactivityTimer = setTimeout(() => {
        if (this.isAuthenticated) {
          this.logout()
        }
      }, 3 * 60 * 60 * 1000) // 3 hours
    },
  }
})
