import { defineConfig } from 'vite'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '127.0.0.1',  // Nutze IPv4 statt IPv6 (::1)
    port: 5173,  // Vites Standard-Port (3000 oft durch Firewall blockiert)
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  assetsInclude: ['**/*.svg', '**/*.csv', '**/*.png', '**/*.jpg'],
})
