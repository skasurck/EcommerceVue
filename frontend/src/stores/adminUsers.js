import { defineStore } from 'pinia'
import api from '../axios'

export const useAdminUsersStore = defineStore('adminUsers', {
  state: () => ({
    items: [],
    userDetail: null,
    changedAt: 0,           // <- pulso de cambios
  }),
  actions: {
    async fetchUsers(params = {}) {
      const { data } = await api.get('admin/users/', { params })
      this.items = data.results || data
      return data
    },
    async fetchUser(id) {
      const { data } = await api.get(`admin/users/${id}/`, { params: { _t: Date.now() } })
      this.userDetail = data
      // sincroniza si ya está listado
      const i = this.items.findIndex(u => u.id === id)
      if (i !== -1) this.items[i] = { ...this.items[i], ...data }
      return data
    },
    async updateUser(id, payload) {
      const { data } = await api.patch(`admin/users/${id}/`, payload)
      const i = this.items.findIndex(u => u.id === id)
      if (i !== -1) this.items[i] = { ...this.items[i], ...data }
      this.changedAt = Date.now()     // <- notifica
      return data
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
      const { data } = await api.post(`admin/users/${userId}/reset_password_link/`)
      return data
    },
    async deleteUser(id) {
      await api.delete(`admin/users/${id}/`)
      this.items = this.items.filter(u => u.id !== id)
      this.changedAt = Date.now()     // <- notifica
    },
  }
})
