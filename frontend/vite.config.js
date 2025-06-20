import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // Point API requests to the new FastAPI server on port 8000
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // No rewrite needed if endpoints start with /api in the server
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'map-vendor': ['leaflet', 'react-leaflet'],
          'chart-vendor': ['recharts'],
          'animation-vendor': ['framer-motion'],
        },
      },
    },
  },
});
