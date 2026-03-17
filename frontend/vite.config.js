import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    watch: {
      // Activar solo en entornos con sistema de archivos virtual (WSL, Docker).
      // En Windows/Mac nativo no es necesario y degrada el rendimiento.
      usePolling: !!process.env.VITE_USE_POLLING,
    },
  },
})
