import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

// Mock del módulo http para no hacer requests reales
vi.mock('@/services/http', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
  ensureInterceptors: vi.fn(),
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('inicia sin sesión cuando localStorage está vacío', () => {
    const auth = useAuthStore()
    expect(auth.isAuthenticated).toBe(false)
    expect(auth.user).toBeNull()
    expect(auth.accessToken).toBeNull()
  })

  it('setTokens guarda access y refresh en localStorage', () => {
    const auth = useAuthStore()
    auth.setTokens('access-123', 'refresh-456')

    expect(auth.accessToken).toBe('access-123')
    expect(auth.refreshToken).toBe('refresh-456')
    expect(localStorage.getItem('accessToken')).toBe('access-123')
    expect(localStorage.getItem('refreshToken')).toBe('refresh-456')
    expect(auth.isAuthenticated).toBe(true)
  })

  it('setTokens con null limpia localStorage', () => {
    const auth = useAuthStore()
    auth.setTokens('access-123', 'refresh-456')
    auth.setTokens(null, null)

    expect(auth.accessToken).toBeNull()
    expect(auth.refreshToken).toBeNull()
    expect(localStorage.getItem('accessToken')).toBeNull()
    expect(localStorage.getItem('refreshToken')).toBeNull()
    expect(auth.isAuthenticated).toBe(false)
  })

  it('logout limpia tokens y usuario', () => {
    const auth = useAuthStore()
    auth.setTokens('tok', 'ref')
    auth.user = { id: 1, username: 'test', rol: 'cliente' }
    localStorage.setItem('user', JSON.stringify(auth.user))

    auth.logout()

    expect(auth.accessToken).toBeNull()
    expect(auth.refreshToken).toBeNull()
    expect(auth.user).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
  })

  it('hasRole devuelve true para el rol correcto', () => {
    const auth = useAuthStore()
    auth.user = { id: 1, rol: 'admin' }

    expect(auth.hasRole('admin')).toBe(true)
    expect(auth.hasRole('cliente')).toBe(false)
  })

  it('hasAnyRole devuelve true si el rol está en la lista', () => {
    const auth = useAuthStore()
    auth.user = { id: 1, rol: 'super_admin' }

    expect(auth.hasAnyRole(['admin', 'super_admin'])).toBe(true)
    expect(auth.hasAnyRole(['cliente'])).toBe(false)
  })

  it('checkLogin restaura sesión desde localStorage', () => {
    const userData = { id: 5, username: 'irving', rol: 'admin' }
    localStorage.setItem('accessToken', 'restored-access')
    localStorage.setItem('refreshToken', 'restored-refresh')
    localStorage.setItem('user', JSON.stringify(userData))

    const auth = useAuthStore()
    auth.checkLogin()

    expect(auth.accessToken).toBe('restored-access')
    expect(auth.refreshToken).toBe('restored-refresh')
    expect(auth.user).toEqual(userData)
    expect(auth.isAuthenticated).toBe(true)
  })

  it('login llama al endpoint correcto y guarda tokens', async () => {
    const api = (await import('@/services/http')).default
    api.post.mockResolvedValueOnce({
      data: {
        token: 'new-access',
        refresh: 'new-refresh',
        user: { id: 1, username: 'irving', rol: 'admin' },
      },
    })

    const auth = useAuthStore()
    await auth.login({ username: 'irving', password: 'pass123' })

    expect(api.post).toHaveBeenCalledWith('auth/login/', { username: 'irving', password: 'pass123' }, expect.any(Object))
    expect(auth.isAuthenticated).toBe(true)
    expect(auth.user.username).toBe('irving')
  })

  it('login lanza error con mensaje del servidor en credenciales incorrectas', async () => {
    const api = (await import('@/services/http')).default
    api.post.mockResolvedValueOnce({
      data: { detail: 'Credenciales inválidas.' },
    })

    const auth = useAuthStore()
    await expect(auth.login({ username: 'x', password: 'y' })).rejects.toThrow('Credenciales inválidas.')
  })

  it('login retorna data con requires_2fa sin lanzar error', async () => {
    const api = (await import('@/services/http')).default
    api.post.mockResolvedValueOnce({
      data: { requires_2fa: true, challenge: 'ch-abc' },
    })

    const auth = useAuthStore()
    const result = await auth.login({ username: 'admin', password: 'pass' })

    expect(result.requires_2fa).toBe(true)
    expect(auth.isAuthenticated).toBe(false)
  })
})
