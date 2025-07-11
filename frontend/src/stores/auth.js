import { defineStore } from 'pinia'
import axios from '../axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isLoggedIn: !!localStorage.getItem('access'),
    profile: null,
  }),
  actions: {
    login(token, refresh) {
      localStorage.setItem('access', token)
      localStorage.setItem('refresh', refresh)
      this.isLoggedIn = true
      this.fetchProfile()
    },
    logout() {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      this.isLoggedIn = false
      this.profile = null
    },
    async fetchProfile() {
      try {
        const res = await axios.get('profile/')
        this.profile = res.data
      } catch (err) {
        console.error('Error cargando perfil:', err)
      }
    },
    checkLogin() {
      this.isLoggedIn = !!localStorage.getItem('access')
      if (this.isLoggedIn) {
        this.fetchProfile()
      }
    }
  },
})
