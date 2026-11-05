import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'node:path'

export default defineConfig({
  plugins: [vue()],
  base: process.env.VITE_BASE_PATH || (process.env.GITHUB_ACTIONS ? '/CGID/' : '/'),
  server: {
    fs: {
      allow: [resolve(__dirname, '../..')],
    },
  },
})
