import { defineStore } from 'pinia'
import api from '../axios'

export const useAdminUsersStore = defineStore('adminUsers', {
  state: () => ({
    items: [],
    userDetail: null,
  }),
  actions: {
    async fetchUsers(params = {}) {
      const { data } = await api.get('admin/users/', {
        params,
        headers: { 'Cache-Control': 'no-cache' }
      })
      this.items = data.results || data
      return data
    },
    async fetchUser(id) {
      const res = await api.get(`admin/users/${id}/`)
      this.userDetail = res.data
      return res.data
    },
    async updateUser(id, payload) {
      const res = await api.patch(`admin/users/${id}/`, payload)
      this.userDetail = res.data
      return res.data
    },
    async getDirecciones(userId) {
      const res = await api.get(`admin/users/${userId}/direcciones/`)
      return res.data
    },
    async createDireccion(userId, payload) {
      const res = await api.post(`admin/users/${userId}/direcciones/`, payload)
      return res.data
    },
    async updateDireccion(userId, dirId, payload) {
      const res = await api.patch(`admin/users/${userId}/direcciones/${dirId}/`, payload)
      return res.data
    },
    async deleteDireccion(userId, dirId) {
      const res = await api.delete(`admin/users/${userId}/direcciones/${dirId}/`)
      return res.data
    },
    async setDefaultDireccion(userId, dirId) {
      const res = await api.post(`admin/users/${userId}/direcciones/${dirId}/set_default/`)
      return res.data
    },
    async importarDirecciones(userId) {
      const res = await api.post(`admin/users/${userId}/importar_direcciones/`)
      return res.data
    },
    async setPassword(userId, newPassword) {
      const res = await api.post(`admin/users/${userId}/set_password/`, { new_password: newPassword })
      return res.data
    },
    async resetPasswordLink(userId) {
      try {
        const res = await api.post(`admin/users/${userId}/reset_password_link/`)
        return res.data
      } catch (error) {
        throw error
      }
    },
    async deleteUser(userId) {
      try {
        const res = await api.delete(`admin/users/${userId}/`)
        return res.data
      } catch (error) {
        throw error
      }
    }
  }
})
