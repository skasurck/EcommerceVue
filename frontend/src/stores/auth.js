import { defineStore } from 'pinia'
import api from '../services/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // Tokens persistidos para mantener la sesión al recargar la página
    accessToken: localStorage.getItem('accessToken') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null,
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
      if (!data.access || !data.refresh) throw new Error('Tokens missing')
      this.setTokens(data.access, data.refresh)
      if (data.user) {
        this.user = data.user
        localStorage.setItem('user', JSON.stringify(data.user))
      }
      return data
    },
    /**
     * Cierra sesión y limpia estado
     */
    logout() {
      this.setTokens(null, null)
      this.user = null
      localStorage.removeItem('user')
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
    }
  }
})
