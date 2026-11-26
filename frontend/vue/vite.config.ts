import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'node:path'

export default defineConfig({
  plugins: [vue()],
  base: process.env.VITE_BASE_PATH || (process.env.GITHUB_ACTIONS ? '/CGID/' : '/'),
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          const normalized = id.replace(/\\/g, '/')
          if (normalized.includes('/data/processed/frontend/')) {
            return 'datos-catalogo'
          }
          if (
            normalized.includes('/node_modules/chart.js/')
            || normalized.includes('/node_modules/@kurkle/')
          ) {
            return 'charts'
          }
          if (
            normalized.includes('/node_modules/primevue/')
            || normalized.includes('/node_modules/@primeuix/')
            || normalized.includes('/node_modules/@primevue/')
          ) {
            return 'primevue'
          }
          if (
            normalized.includes('/node_modules/vue/')
            || normalized.includes('/node_modules/vue-router/')
            || normalized.includes('/node_modules/@vue/')
          ) {
            return 'vue-vendor'
          }
        },
      },
    },
  },
  server: {
    fs: {
      allow: [resolve(__dirname, '../..')],
    },
  },
})
