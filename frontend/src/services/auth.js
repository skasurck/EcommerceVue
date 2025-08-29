import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

const BASE_URL = 'http://localhost:8000/api/'

// Almacenamiento de tokens y utilidades de autenticación
export const setTokens = (access, refresh) => {
  const auth = useAuthStore()
  auth.setTokens(access, refresh)
}

export const getAccessToken = () => useAuthStore().accessToken

export const login = async (credentials) => {
  const res = await axios.post(`${BASE_URL}auth/login/`, credentials)
  const { access, refresh, user } = res.data
  const auth = useAuthStore()
  auth.login({ access, refresh }, user)
  return res
}

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
    const res = await axios.post(`${BASE_URL}auth/refresh/`, { refresh })
    auth.setTokens(res.data.access, refresh)
    return res.data.access
  } catch (err) {
    logout()
    throw err
  }
}
