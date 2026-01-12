import './assets/style.css'
import './assets/main.css'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth'
import { ensureInterceptors } from './axios'
import vClickOutside from 'v-click-outside'

const app = createApp(App)
const pinia = createPinia()

app.use(vClickOutside)
app.use(pinia)
ensureInterceptors()
app.use(router)

const auth = useAuthStore()
auth.checkLogin()  // <- esto restaura el estado al recargar

app.mount('#app')
