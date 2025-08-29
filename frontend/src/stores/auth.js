import { defineStore } from 'pinia'

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
     * Inicia sesión guardando tokens y usuario
     */
    login(tokens, user) {
      this.setTokens(tokens.access, tokens.refresh)
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
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
