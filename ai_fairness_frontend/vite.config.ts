import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],

  // --- 新增内容 ---
  server: {
    proxy: {
      // 匹配所有以 /api 开头的请求
      '/api': {
        // 将请求转发到 Docker Compose 中名为 'backend' 的服务
        // 5000 是我们为 Flask 暴露的端口
        target: 'http://backend:5000',
        changeOrigin: true,
        // 将 /api/run-analysis 重写为 /run-analysis
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    }
  }
  // --- 新增结束 ---
})