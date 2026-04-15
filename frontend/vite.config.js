import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: ['./src/tests/setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/stores/**', 'src/services/**', 'src/utils/**'],
    },
  },
  plugins: [
    vue(),
    vueDevTools(),
    // Convierte el <link rel="stylesheet"> bloqueante en carga asíncrona.
    // Seguro para un SPA: la página está vacía hasta que JS ejecuta de todos modos.
    {
      name: 'defer-css',
      transformIndexHtml(html) {
        return html.replace(
          /<link rel="stylesheet"([^>]*)>/g,
          (_, attrs) =>
            `<link rel="preload" as="style"${attrs} onload="this.onload=null;this.rel='stylesheet'">` +
            `<noscript><link rel="stylesheet"${attrs}></noscript>`
        )
      },
    },
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/vue') || id.includes('node_modules/@vue')) {
            return 'vue'
          }
          if (id.includes('node_modules/pinia')) {
            return 'pinia'
          }
          if (id.includes('node_modules/vue-router')) {
            return 'router'
          }
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
