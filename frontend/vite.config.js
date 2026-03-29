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
  build: {
    // CSS separado del JS principal para descarga paralela
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Separar Vue en su propio chunk (se cachea entre versiones)
          if (id.includes('node_modules/vue') || id.includes('node_modules/@vue')) {
            return 'vue'
          }
          // Separar pinia
          if (id.includes('node_modules/pinia')) {
            return 'pinia'
          }
          // Separar vue-router
          if (id.includes('node_modules/vue-router')) {
            return 'router'
          }
          // Separar axios
          if (id.includes('node_modules/axios')) {
            return 'axios'
          }
        },
      },
    },
  },
  server: {
    watch: {
      usePolling: !!process.env.VITE_USE_POLLING,
    },
  },
})
