import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base './' permite abrir la versión compilada desde cualquier carpeta o servidor.
export default defineConfig({
  base: './',
  plugins: [react()],
})
