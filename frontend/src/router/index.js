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
import OrderDetail from '../views/OrderDetail.vue'
import AdminUsuarios from '../views/AdminUsuarios.vue'
import AdminUsuarioDetalle from '../views/AdminUsuarioDetalle.vue'
import AdminConfiguracion from '../views/AdminConfiguracion.vue'
import MetodosPago from '../views/MetodosPago.vue'
import MetodosEnvio from '../views/MetodosEnvio.vue'
import EditarProducto from '../views/EditarProducto.vue'
import ClasificarProductos from '../views/ClasificarProductos.vue'
import RevisarClasificaciones from '../views/RevisarClasificaciones.vue'
import { useAuthStore } from '../stores/auth'
import { useAdminUsersStore } from '../stores/adminUsers'
import AdminLayout from '@/layouts/AdminLayout.vue'

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
        component: AdminUsuarios,
        meta: { 
          title: 'Gestión de usuarios', 
          requiresAuth: true, 
          roles: ['admin', 'super_admin'] 
        },
        async beforeEnter(to, from) {
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
        path: 'configuracion',
        name: 'admin-configuracion',
        component: () => import('@/views/AdminConfiguracion.vue'),
        meta: { title: 'Configuración', roles:['super_admin'] }
      },
      {
        path: 'ai/clasificar-productos',
        name: 'admin-ai-clasificar-productos',
        component: ClasificarProductos,
        meta: { title: 'Clasificación con IA', requiresAuth: true, roles: ['admin', 'super_admin'] }
      },
      {
        path: 'ai/revisar-clasificaciones',
        name: 'admin-ai-revisar-clasificaciones',
        component: RevisarClasificaciones,
        meta: { title: 'Revisión de clasificaciones', requiresAuth: true, roles: ['admin', 'super_admin'] }
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
        path: '/productos/editar/:id',
        name: 'editar-producto',
        component: EditarProducto,
        meta: { requiresAuth: true, roles: ['admin', 'super_admin'] }
      },
    ]
  },
  
  {
    path: '/acceso-denegado',
    name: 'acceso-denegado',
    component: AccesoDenegado
  },
  {
  path: '/mis-pedidos',
  name: 'MisPedidos',
  component: () => import('@/views/MisPedidos.vue')
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
