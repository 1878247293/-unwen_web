import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  define: {
    // 为 react-markdown-editor-lite 提供全局 React
    'global': 'globalThis',
  },
  optimizeDeps: {
    // 确保 React 被正确处理
    include: ['react', 'react-dom', 'react-markdown-editor-lite'],
  },
})
