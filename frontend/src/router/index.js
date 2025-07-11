import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Productos from '../views/Productos.vue'
import NuevoProducto from '../views/NuevoProducto.vue'
import Registro from '../views/Registro.vue'
import Login from '../views/Login.vue'
import ProductView from '../views/ProductView.vue'

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
    meta: { requiereAuth: true }
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
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 🔐 Protección por ruta
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access')
  if (to.meta.requiereAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
