import { api } from './http'
import { useAuthStore } from '../stores/auth'
import router from '../router'

// Almacenamiento de tokens y utilidades de autenticación
export const setTokens = (access, refresh) => {
  const auth = useAuthStore()
  auth.setTokens(access, refresh)
}

export const getAccessToken = () => useAuthStore().accessToken

export const logout = () => {
  const auth = useAuthStore()
  auth.logout()
  router.push('/login')
}

export const refreshAccessToken = async () => {
  const auth = useAuthStore()
  const refresh = auth.refreshToken
  if (!refresh) throw new Error('No refresh token')
  try {
    const res = await api.post('auth/refresh/', { refresh })
    auth.setTokens(res.data.access, refresh)
    return res.data.access
  } catch (err) {
    logout()
    throw err
  }
}
