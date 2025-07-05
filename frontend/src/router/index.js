import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Productos from '../views/Productos.vue'
import NuevoProducto from '../views/NuevoProducto.vue'
import Registro from '../views/Registro.vue'
import Login from '../views/Login.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
     {
    path: '/productos',
    name: 'Productos',
    component: Productos
  },
  {
  path: '/nuevo-producto',
  name: 'nuevo-producto',
  component: NuevoProducto
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
  ],
})

export default router
