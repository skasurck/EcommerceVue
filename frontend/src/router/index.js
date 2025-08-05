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
import AdminPedidos from '../views/AdminPedidos.vue'
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
    meta: { requiereAuth: true, roles: ['admin', 'super_admin'] }
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
    meta: { requiereAuth: true }
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: CheckoutView,
    meta: { requiereAuth: true }
  },
  {
    path: '/mi-cuenta',
    name: 'mi-cuenta',
    component: MiCuenta,
    meta: { requiereAuth: true }
  },
  {
    path: '/admin/pedidos',
    name: 'admin-pedidos',
    component: AdminPedidos,
    meta: { requiereAuth: true, roles: ['admin', 'super_admin'] }
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

// 🔐 Protección por ruta y roles
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('access')
  const auth = useAuthStore()
  if (to.meta.requiereAuth && !token) {
    return next('/login')
  }
  if (to.meta.roles) {
    if (!auth.profile) {
      await auth.fetchProfile()
    }
    const rol = auth.profile?.perfil?.rol
    if (!to.meta.roles.includes(rol)) {
      return next('/acceso-denegado')
    }
  }
  next()
})

export default router
