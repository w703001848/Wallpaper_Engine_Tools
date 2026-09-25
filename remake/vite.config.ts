import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Renderer build is kept separate from Electron so the preload boundary remains explicit.
export default defineConfig({
  root: 'src/renderer',
  plugins: [react()],
  base: './',
  build: { outDir: '../../dist', emptyOutDir: true },
  server: { port: 5173, strictPort: true },
});
