import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAdminUsersStore } from '@/stores/adminUsers'
import AdminLayout from '@/layouts/AdminLayout.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/productos',
    name: 'productos',
    component: () => import('@/views/Productos.vue')
  },
  {
    path: '/categorias',
    name: 'categorias',
    component: () => import('@/views/CategoriesView.vue'),
  },
  {
    path: '/nuevo-producto',
    name: 'nuevo-producto',
    component: () => import('@/views/NuevoProducto.vue'),
    meta: { requiresAuth: true, roles: ['admin', 'super_admin'] }
  },
  {
    path: '/registro',
    name: 'registro',
    component: () => import('@/views/Registro.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: () => import('@/views/ResetPasswordView.vue')
  },
  {
    path: '/producto/:id',
    name: 'producto',
    component: () => import('@/views/ProductView.vue')
  },
  {
    path: '/carrito',
    name: 'carrito',
    component: () => import('@/views/CarritoView.vue'),
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: () => import('@/views/CheckoutView.vue'),
  },
  {
    path: '/checkout/fallo',
    name: 'checkout-fallo',
    component: () => import('@/views/CheckoutFalloView.vue'),
  },
  {
    path: '/checkout/pendiente',
    name: 'checkout-pendiente',
    component: () => import('@/views/CheckoutPendienteView.vue'),
  },
  {
    path: '/gracias',
    name: 'gracias',
    component: () => import('@/views/GraciasView.vue'),
  },
  {
    path: '/pedido-cancelado',
    name: 'pedido-cancelado',
    component: () => import('@/views/PedidoCanceladoView.vue'),
  },
  {
    path: '/mi-cuenta',
    name: 'mi-cuenta',
    component: () => import('@/views/MiCuenta.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, roles: ['admin','super_admin'] },
    children: [
      { 
        path: '', 
        name: 'admin', 
        component: () => import('@/views/AdminDashboard.vue'), 
        meta: { title: 'Dashboard' } 
      },
      { 
        path: 'productos', 
        name: 'admin-productos', 
        component: () => import('@/views/AdminProductos.vue'), 
        meta: { title: 'Gestión de productos' } 
      },
      {
        path: 'productos/nuevo',
        name: 'admin-producto-nuevo',
        component: () => import('@/views/NuevoProducto.vue'),
        meta: { title: 'Nuevo producto', requiresAuth: true, roles: ['admin','super_admin'] }
      },
      { 
        path: 'pedidos',   
        name: 'admin-pedidos',   
        component: () => import('@/views/AdminPedidos.vue'),   
        meta: { title: 'Gestión de pedidos' } 
      },
      { 
        path: 'pedidos/:id', 
        name: 'admin-pedido-detalle', 
        component: () => import('@/views/OrderDetail.vue'), 
        meta: { title: 'Detalle de pedido' } 
      },
      { 
        path: 'usuarios',
        name: 'admin-usuarios',
        component: () => import('@/views/AdminUsuarios.vue'),
        meta: { 
          title: 'Gestión de usuarios', 
          requiresAuth: true, 
          roles: ['admin', 'super_admin'] 
        },
        async beforeEnter(to) {
          const store = useAdminUsersStore()
          const search = to.query.search ?? ''
          const rol    = to.query.rol ?? ''
          await store.fetchUsers({ search, rol, _t: Date.now() })
          return true
        }
      },
      { 
        path: 'usuarios/:id', 
        name: 'admin-usuario-detalle', 
        component: () => import('@/views/AdminUsuarioDetalle.vue'), 
        meta: { title: 'Usuario' } 
      },
      {
        path: 'promotions',
        name: 'admin-promotions',
        component: () => import('@/views/AdminPromotions.vue'),
        meta: { title: 'Promociones', roles:['admin', 'super_admin'] }
      },
      {
        path: 'home-editor',
        name: 'admin-home-editor',
        component: () => import('@/views/AdminHomeEditor.vue'),
        meta: { title: 'Editar Home', requiresAuth: true, roles: ['admin', 'super_admin'] }
      },
      {
        path: 'promo-banners',
        name: 'admin-promo-banners',
        component: () => import('@/views/AdminPromoBannersEditor.vue'),
        meta: { title: 'Banners promocionales', requiresAuth: true, roles: ['admin', 'super_admin'] }
      },
      {
        path: 'configuracion',
        name: 'admin-configuracion',
        component: () => import('@/views/AdminConfiguracion.vue'),
        meta: { title: 'Configuración', roles:['super_admin'] }
      },
      {
        path: 'ai/clasificar-productos',
        name: 'admin-ai-clasificar-productos',
        component: () => import('@/views/ClasificarProductos.vue'),
        meta: { title: 'Clasificación con IA', requiresAuth: true, roles: ['admin', 'super_admin'] }
      },
      {
        path: 'ai/revisar-clasificaciones',
        name: 'admin-ai-revisar-clasificaciones',
        component: () => import('@/views/RevisarClasificaciones.vue'),
        meta: { title: 'Revisión de clasificaciones', requiresAuth: true, roles: ['admin', 'super_admin'] }
      },
      {
        path: 'ai/learning-stats',
        name: 'admin-ai-learning-stats',
        component: () => import('@/views/AiLearningStats.vue'),
        meta: { title: 'Estadisticas de aprendizaje IA', requiresAuth: true, roles: ['super_admin'] }
      },
      {
        path: 'suppliers/supermex',
        name: 'admin-suppliers-supermex',
        component: () => import('@/views/SupermexImporter.vue'),
        meta: {
          title: 'Importar catálogo Supermex',
          requiresAuth: true,
          roles: ['admin', 'super_admin']
        }
      },
      {
        path: 'configuracion/metodos-pago',
        name: 'admin-configuracion-metodos-pago',
        component: () => import('@/views/MetodosPago.vue'),
        meta: { title: 'Métodos de pago', requiresAuth: true, roles: ['super_admin'] }
      },
      {
        path: 'configuracion/metodos-envio',
        name: 'admin-configuracion-metodos-envio',
        component: () => import('@/views/MetodosEnvio.vue'),
        meta: { title: 'Métodos de envío', requiresAuth: true, roles: ['super_admin'] }
      },
      {
        path: 'cupones',
        name: 'admin-cupones',
        component: () => import('@/views/AdminCupones.vue'),
        meta: { title: 'Cupones de descuento', requiresAuth: true, roles: ['admin', 'super_admin'] }
      },
      {
        path: 'productos/editar/:id',
        name: 'editar-producto',
        component: () => import('@/views/EditarProducto.vue'),
        meta: { requiresAuth: true, roles: ['admin', 'super_admin'] }
      },
    ]
  },
  {
    path: '/acceso-denegado',
    name: 'acceso-denegado',
    component: () => import('@/views/AccesoDenegado.vue')
  },
  {
    path: '/mis-pedidos',
    name: 'MisPedidos',
    component: () => import('@/views/MisPedidos.vue')
  },
  {
    path: '/mis-pedidos/:id',
    name: 'MiPedidoDetalle',
    component: () => import('@/views/MiPedidoDetalle.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/seguridad',
    name: 'Seguridad',
    component: () => import('@/views/Seguridad.vue')
  },
  {
    path: '/direcciones',
    name: 'Direcciones',
    component: () => import('@/views/Direcciones.vue')
  },
  {
    path: '/lista-deseos',
    name: 'lista-deseos',
    component: () => import('@/views/WishlistView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/busqueda',
    name: 'busqueda',
    component: () => import('@/views/ResultadosBusqueda.vue')
  },
  {
    path: '/categoria/:categoriaId',
    name: 'categoria',
    component: () => import('@/views/CategoriaView.vue')
  },
  {
    path: '/marca/:marcaId',
    name: 'marca',
    component: () => import('@/views/MarcaView.vue')
  },
  {
    path: '/contacto',
    name: 'contacto',
    component: () => import('@/views/Contacto.vue')
  },
  {
    path: '/politica-de-privacidad',
    name: 'privacidad',
    component: () => import('@/views/Privacidad.vue')
  },
  {
    path: '/terminos-y-condiciones',
    name: 'terminos',
    component: () => import('@/views/Terminos.vue')
  },
  {
    path: '/politica-de-devoluciones',
    name: 'devoluciones',
    component: () => import('@/views/Devoluciones.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  }
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }
  if (to.meta.roles && !auth.hasAnyRole(to.meta.roles)) {
    return next('/acceso-denegado')
  }
  next()
})

// Cuando el navegador tiene cacheado un index.html viejo y los chunks JS
// ya no existen en el servidor (nuevo deploy), fuerza una recarga completa.
router.onError((error, to) => {
  const isChunkError =
    error.message?.includes('Failed to fetch dynamically imported module') ||
    error.message?.includes('Importing a module script failed') ||
    error.message?.includes('Unable to preload CSS')
  if (isChunkError) {
    window.location.href = to.fullPath
  }
})

export default router
