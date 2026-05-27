import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/chat': 'http://api:8000',
      '/health': 'http://api:8000',
      '/ws': {
        target: 'ws://api:8000',
        ws: true,
      },
    },
  },
})
