import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import svgr from 'vite-plugin-svgr'
import fs from 'fs'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), svgr()],
  server: {
    host: true,
  },
})
