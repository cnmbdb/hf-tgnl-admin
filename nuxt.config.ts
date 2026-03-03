// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: false },
  ssr: false,
  
  // 过滤日志输出，避免开发期卡顿
  logLevel: 'silent',

  app: {
    baseURL: process.env.APP_BASE_PATH || '/'
  },

  modules: [
    '@nuxt/ui',
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
  ],

  tailwindcss: {
    viewer: false,
    quiet: true
  },

  css: ['~/assets/css/main.css'],

  ui: {
    global: true
  },

  // colorMode 配置已移除 - 使用 Tailwind 的 dark class 代替

  typescript: {
    strict: false,
    typeCheck: false
  },

  vite: {
    server: {
      port: Number(process.env.PORT || 3000),
      strictPort: true,
      host: 'localhost',
      hmr: {
        overlay: false
      },
      watch: {
        usePolling: false,
        ignored: [
          '**/.nuxt/**',
          '**/node_modules/**',
          '**/nl-2333/**',
          '**/*.sql',
          '**/*.log',
          '**/*.md',
          '**/zibll-order-api.php'
        ]
      },
      fs: {
        strict: true
      }
    },
    optimizeDeps: {
      include: ['@nuxt/ui'],
      // 限制优化范围
      exclude: []
    },
    build: {
      // 减少构建内存使用
      chunkSizeWarningLimit: 1000,
      rollupOptions: {
        output: {
          manualChunks: undefined
        }
      }
    }
  },

  runtimeConfig: {
    // Private keys (only available on server-side)
    // 数据库配置 - 使用空字符串作为默认值，运行时从环境变量读取
    dbHost: process.env.DB_HOST || '',
    dbUser: process.env.DB_USER || '',
    dbPassword: process.env.DB_PASSWORD || '',
    dbName: process.env.DB_NAME || '',
    dbPort: Number(process.env.DB_PORT || 3306),
    
    // WordPress API 配置
    WORDPRESS_URL: process.env.WORDPRESS_URL || '',
    WORDPRESS_USERNAME: process.env.WORDPRESS_USERNAME || '',
    WORDPRESS_APP_PASSWORD: process.env.WORDPRESS_APP_PASSWORD || '',
    WORDPRESS_PRODUCT_ID: process.env.WORDPRESS_PRODUCT_ID || '',
    
    // 授权配置
    ORDER_NUMBER: process.env.ORDER_NUMBER || '',
    
    // Public keys (exposed to client-side)
    public: {
      apiBase: '/api',
      siteTitle: process.env.NUXT_PUBLIC_SITE_TITLE || '后台管理',
      robotsIndex: (process.env.NUXT_PUBLIC_ROBOTS_INDEX === 'true')
    }
  },

  routeRules: process.env.NODE_ENV === 'production' ? {
    '/**': {
      headers: {
        'x-robots-tag': 'noindex, nofollow',
        'x-frame-options': 'DENY',
        'x-content-type-options': 'nosniff',
        'referrer-policy': 'no-referrer',
        'permissions-policy': 'interest-cohort=()'
      }
    }
  } : {},

  nitro: {
    // 最小化配置,防止问题
    logLevel: 0,
    // 减少内存使用
    minify: false,
    sourceMap: false
  },
  
  // 忽略构建警告
  build: {
    transpile: []
  },

  // 禁用 appManifest 解决 manifest-route-rule 重复警告
  experimental: {
    appManifest: false
  },

  // 去重中间件，防止 manifest-route-rule 重复注册的警告
  hooks: {
    'app:resolve'(app) {
      const seen = new Set<string>()
      const deduped: any[] = []
      for (const mw of app.middleware as any[]) {
        const name = typeof mw === 'string' ? mw : (mw?.name || mw?.key || '')
        const key = name || JSON.stringify(mw)
        if (!seen.has(key)) {
          seen.add(key)
          deduped.push(mw)
        }
      }
      app.middleware = deduped
    }
  },

  // 开发服务器优化
  devServer: {
    port: Number(process.env.PORT) || 3000,
    host: 'localhost',
    url: `http://localhost:${process.env.PORT || 3000}`
  },

  compatibilityDate: '2025-11-07'
})
