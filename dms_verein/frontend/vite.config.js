import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

const webserver_port = (() => {
  try {
    return require('../../../../sites/common_site_config.json').webserver_port
  } catch {
    return 8000
  }
})()

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 8083,
    proxy: {
      '/api': { target: `http://127.0.0.1:${webserver_port}`, changeOrigin: true },
      '/assets': { target: `http://127.0.0.1:${webserver_port}`, changeOrigin: true },
      '/files': { target: `http://127.0.0.1:${webserver_port}`, changeOrigin: true },
    },
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  build: {
    outDir: '../public/frontend',
    emptyOutDir: true,
    target: 'es2015',
    rollupOptions: {
      output: {
        entryFileNames: 'assets/index.js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/index.[ext]',
      },
    },
  },
  base: '/assets/dms_verein/frontend/',
})
