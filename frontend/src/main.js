import './assets/style.css'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth'
import { ensureInterceptors } from './axios'
import vClickOutside from 'v-click-outside'
import { createHead } from '@vueuse/head'

const app = createApp(App)
const pinia = createPinia()
const head = createHead()

app.use(vClickOutside.directive)
app.use(pinia)
app.use(head)
ensureInterceptors()
app.use(router)

const auth = useAuthStore()
auth.checkLogin()  // <- esto restaura el estado al recargar

app.mount('#app')
