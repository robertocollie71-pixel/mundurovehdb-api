import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        public: './src/public/main.tsx'
      },
      output: {
        entryFileNames: 'public/index.js',
        chunkFileNames: 'public/[name]-[hash].js',
        assetFileNames: 'public/[name]-[hash][extname]'
      }
    }
  }
});