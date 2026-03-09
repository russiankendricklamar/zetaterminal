import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

const isTauri = !!process.env.TAURI_ENV_PLATFORM

export default defineConfig(({ command }) => ({
  base: isTauri ? '/' : (command === 'build' ? '/zetaterminal/' : '/'),
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    target: isTauri ? ['es2021', 'chrome100', 'safari15'] : 'esnext',
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia', 'axios'],
          'echarts': ['echarts'],
          'three': ['three'],
          'chartjs': ['chart.js'],
          'xlsx': ['xlsx'],
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  clearScreen: !isTauri,
  server: {
    port: 5173,
    strictPort: isTauri
  }
}))
