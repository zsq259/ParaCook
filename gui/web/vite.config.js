import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { readFileSync } from 'fs'
import { resolve } from 'path'

const configPath = resolve(__dirname, '../../config/gui_config.json')
const config = JSON.parse(readFileSync(configPath, 'utf-8'))


export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: config.web.port,
    proxy: {
      '/api': {
        target: `http://${config.api.host}:${config.api.port}`,
        changeOrigin: true
      }
    }
  }
})