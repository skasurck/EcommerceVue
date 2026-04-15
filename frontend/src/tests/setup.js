import { config } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, vi } from 'vitest'

// Pinia limpia en cada test
beforeEach(() => {
  setActivePinia(createPinia())
})

// Stub global de RouterLink y RouterView para tests que usan componentes con router
config.global.stubs = {
  RouterLink: { template: '<a><slot /></a>' },
  RouterView: { template: '<div />' },
}

// Mock de localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: (key) => store[key] ?? null,
    setItem: (key, value) => { store[key] = String(value) },
    removeItem: (key) => { delete store[key] },
    clear: () => { store = {} },
  }
})()
Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock })

// Mock global de crypto.randomUUID (usado en carrito.js)
Object.defineProperty(globalThis, 'crypto', {
  value: { randomUUID: () => `uuid-${Math.random().toString(36).slice(2)}` },
})
