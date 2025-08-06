import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Productos from '../views/Productos.vue'
import NuevoProducto from '../views/NuevoProducto.vue'
import Registro from '../views/Registro.vue'
import Login from '../views/Login.vue'
import ProductView from '../views/ProductView.vue'
import CarritoView from '../views/CarritoView.vue'
import CheckoutView from '../views/CheckoutView.vue'
import MiCuenta from '../views/MiCuenta.vue'
import AccesoDenegado from '../views/AccesoDenegado.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import AdminProductos from '../views/AdminProductos.vue'
import AdminPedidos from '../views/AdminPedidos.vue'
import AdminUsuarios from '../views/AdminUsuarios.vue'
import AdminConfiguracion from '../views/AdminConfiguracion.vue'
import MetodosPago from '../views/MetodosPago.vue'
import MetodosEnvio from '../views/MetodosEnvio.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/productos',
    name: 'productos',
    component: Productos
  },
  {
    path: '/nuevo-producto',
    name: 'nuevo-producto',
    component: NuevoProducto,
    meta: { requiresAuth: true, roles: ['admin', 'super_admin'] }
  },
  {
    path: '/registro',
    name: 'registro',
    component: Registro
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/producto/:id',
    name: 'producto',
    component: ProductView
  },
  {
    path: '/carrito',
    name: 'carrito',
    component: CarritoView,
    meta: { requiresAuth: true }
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: CheckoutView,
    meta: { requiresAuth: true }
  },
  {
    path: '/mi-cuenta',
    name: 'mi-cuenta',
    component: MiCuenta,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'admin',
    component: AdminDashboard,
    meta: { requiresAuth: true, roles: ['admin', 'super_admin'] }
  },
  {
    path: '/admin/productos',
    name: 'admin-productos',
    component: AdminProductos,
    meta: { requiresAuth: true, roles: ['admin', 'super_admin'] }
  },
  {
    path: '/admin/pedidos',
    name: 'admin-pedidos',
    component: AdminPedidos,
    meta: { requiresAuth: true, roles: ['admin', 'super_admin'] }
  },
  {
    path: '/admin/usuarios',
    name: 'admin-usuarios',
    component: AdminUsuarios,
    meta: { requiresAuth: true, roles: ['admin', 'super_admin'] }
  },
  {
    path: '/admin/configuracion',
    name: 'admin-configuracion',
    component: AdminConfiguracion,
    meta: { requiresAuth: true, roles: ['super_admin'] }
  },
  {
    path: '/admin/configuracion/metodos-pago',
    name: 'admin-configuracion-metodos-pago',
    component: MetodosPago,
    meta: { requiresAuth: true, roles: ['super_admin'] }
  },
  {
    path: '/admin/configuracion/metodos-envio',
    name: 'admin-configuracion-metodos-envio',
    component: MetodosEnvio,
    meta: { requiresAuth: true, roles: ['super_admin'] }
  },
  {
    path: '/acceso-denegado',
    name: 'acceso-denegado',
    component: AccesoDenegado
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }
  if (to.meta.roles && !auth.hasAnyRole(to.meta.roles)) {
    return next('/acceso-denegado')
  }
  next()
})

export default router
