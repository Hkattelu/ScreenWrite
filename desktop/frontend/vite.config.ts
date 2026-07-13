import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Dev mode: `python -m desktop.app --dev` serves the API on :8765.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3100,
    proxy: {
      '/api': 'http://127.0.0.1:8765',
    },
  },
  build: {
    outDir: 'dist',
  },
});
