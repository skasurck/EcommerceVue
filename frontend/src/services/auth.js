import { api } from './http'
import { useAuthStore } from '../stores/auth'
import router from '../router'

// Almacenamiento de tokens y utilidades de autenticación
export const setTokens = (access, refresh) => {
  const auth = useAuthStore()
  auth.setTokens(access, refresh)
}

export const getAccessToken = () => useAuthStore().accessToken

export const getRefreshToken = () => useAuthStore().refreshToken

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
    const { data } = await api.post('auth/refresh/', { refresh })
    if (import.meta.env.DEV) console.debug('refresh response', data)
    const access =
      data.access ||
      data.access_token ||
      data.token ||
      data.auth_token ||
      data?.jwt?.access ||
      data?.tokens?.access ||
      null
    if (!access) throw new Error('No access token in refresh response')
    auth.setTokens(access, refresh)
    return access
  } catch (err) {
    logout()
    throw err
  }
}
