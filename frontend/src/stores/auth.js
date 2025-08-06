import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null,
    isAuthenticated: !!localStorage.getItem('token'),
  }),
  actions: {
    login(token, user) {
      this.token = token
      this.user = user
      this.isAuthenticated = true
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
    },
    logout() {
      this.token = null
      this.user = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
    hasRole(role) {
      return this.user?.rol === role
    },
    hasAnyRole(roles) {
      return roles.includes(this.user?.rol)
    },
    checkLogin() {
      this.token = localStorage.getItem('token') || null
      this.user = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null
      this.isAuthenticated = !!this.token
    }
  }
})
