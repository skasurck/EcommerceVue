import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCarritoStore } from '@/stores/carrito'

// vi.mock se hoistea al tope del archivo, por eso el factory no puede referenciar
// variables declaradas después. Se usa vi.hoisted() para crearlas antes del hoist.
const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
}))
vi.mock('@/axios', () => ({ default: apiMock }))

const makeItem = (overrides = {}) => ({
  id: 1,
  cantidad: 2,
  producto: {
    id: 10,
    nombre: 'Teclado mecánico',
    precio_normal: '500.00',
    precio_rebajado: null,
    stock: 5,
    precios_escalonados: [],
  },
  reserva_expira: null,
  ...overrides,
})

const carritoApiResponse = { data: { items: [makeItem()] } }

describe('Carrito Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  // ── Getters ─────────────────────────────────────────────────────────────────

  it('totalCantidad suma las cantidades de todos los items', () => {
    const store = useCarritoStore()
    store.items = [makeItem({ cantidad: 2 }), makeItem({ id: 2, cantidad: 3 })]
    expect(store.totalCantidad).toBe(5)
  })

  it('totalCantidad es 0 cuando el carrito está vacío', () => {
    const store = useCarritoStore()
    expect(store.totalCantidad).toBe(0)
  })

  it('precioUnitario usa precio_rebajado si existe', () => {
    const store = useCarritoStore()
    const item = makeItem()
    item.producto.precio_rebajado = '350.00'
    expect(store.precioUnitario(item)).toBe(350)
  })

  it('precioUnitario aplica precio escalonado si la cantidad califica', () => {
    const store = useCarritoStore()
    const item = makeItem({ cantidad: 10 })
    item.producto.precios_escalonados = [
      { cantidad_minima: 5, precio_unitario: '450.00' },
      { cantidad_minima: 10, precio_unitario: '400.00' },
    ]
    expect(store.precioUnitario(item)).toBe(400)
  })

  it('subtotal multiplica precio × cantidad para cada item', () => {
    const store = useCarritoStore()
    store.items = [
      makeItem({ cantidad: 2 }),  // precio_normal = 500 → 1000
    ]
    expect(store.subtotal).toBe(1000)
  })

  // ── Actions ─────────────────────────────────────────────────────────────────

  it('cargar normaliza la respuesta de la API y guarda los items', async () => {
    apiMock.get.mockResolvedValueOnce(carritoApiResponse)
    const store = useCarritoStore()
    await store.cargar()

    expect(store.items).toHaveLength(1)
    expect(store.items[0].cantidad).toBe(2)
    expect(store._loaded).toBe(true)
  })

  it('cargar establece error si la API falla', async () => {
    apiMock.get.mockRejectedValueOnce(new Error('Network Error'))
    const store = useCarritoStore()
    await store.cargar()

    expect(store.error).toBeTruthy()
    expect(store.items).toHaveLength(0)
  })

  it('agregar llama POST si el producto no está en el carrito', async () => {
    apiMock.get.mockResolvedValue(carritoApiResponse)
    apiMock.post.mockResolvedValueOnce({ data: {} })
    const store = useCarritoStore()
    store._loaded = true
    store.items = []

    const producto = { id: 99, nombre: 'Mouse', precio_normal: '200', stock: 3, precios_escalonados: [] }
    await store.agregar(producto, 1)

    expect(apiMock.post).toHaveBeenCalledWith('carrito/', { producto: 99, cantidad: 1 })
    expect(store.drawerOpen).toBe(true)
    expect(store.lastAdded.id).toBe(99)
  })

  it('agregar no hace nada si el producto está agotado y no está en el carrito', async () => {
    const store = useCarritoStore()
    store._loaded = true
    store.items = []

    const producto = { id: 99, nombre: 'Mouse', precio_normal: '200', stock: 0 }
    await store.agregar(producto)

    expect(apiMock.post).not.toHaveBeenCalled()
  })

  it('eliminar llama DELETE y recarga el carrito', async () => {
    apiMock.get.mockResolvedValue(carritoApiResponse)
    apiMock.delete.mockResolvedValueOnce({})
    const store = useCarritoStore()
    store._loaded = true
    store.items = [makeItem()]

    await store.eliminar(1)

    expect(apiMock.delete).toHaveBeenCalledWith('carrito/1/')
    expect(apiMock.get).toHaveBeenCalled()
  })

  it('eliminar establece error si falla el servidor', async () => {
    apiMock.delete.mockRejectedValueOnce({ response: { data: { detail: 'No encontrado' } } })
    const store = useCarritoStore()
    store._loaded = true
    store.items = [makeItem()]

    await store.eliminar(1)
    expect(store.error).toBeTruthy()
  })

  it('limpiar vacía items y reservaExpira localmente', async () => {
    apiMock.delete.mockResolvedValueOnce({})
    const store = useCarritoStore()
    store.items = [makeItem()]
    store.reservaExpira = '2026-01-01T00:00:00Z'

    await store.limpiar()

    expect(store.items).toHaveLength(0)
    expect(store.reservaExpira).toBeNull()
  })
})
