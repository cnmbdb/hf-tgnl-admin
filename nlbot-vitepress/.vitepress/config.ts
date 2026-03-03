import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'TGNL Admin 文档',
  description: 'Telegram Bot 管理后台完整文档',
  base: '/',
  
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1.0' }]
  ],

  themeConfig: {
    logo: '/logo.png',
    
    nav: [
      { text: '首页', link: '/' },
      { text: '快速开始', link: '/guide/getting-started' },
      { text: '功能模块', link: '/modules/' },
      { text: '部署指南', link: '/deployment/' },
      { text: 'API 文档', link: '/api/' }
    ],

    sidebar: {
      '/guide/': [
        {
          text: '入门指南',
          items: [
            { text: '快速开始', link: '/guide/getting-started' },
            { text: '项目介绍', link: '/guide/introduction' },
            { text: '环境要求', link: '/guide/requirements' }
          ]
        }
      ],
      '/modules/': [
        {
          text: '功能模块',
          items: [
            { text: '概览', link: '/modules/' },
            { text: '仪表盘', link: '/modules/dashboard' },
            { text: '机器人管理', link: '/modules/bots' },
            { text: '用户管理', link: '/modules/users' },
            { text: '订单管理', link: '/modules/orders' },
            { text: '数据分析', link: '/modules/analytics' },
            { text: '命令管理', link: '/modules/bot-commands' },
            { text: '关键词回复', link: '/modules/keyword-replies' },
            { text: '内联键盘', link: '/modules/inline-keyboards' },
            { text: '键盘按钮', link: '/modules/keyboard-buttons' },
            { text: '授权管理', link: '/modules/license' }
          ]
        }
      ],
      '/deployment/': [
        {
          text: '部署指南',
          items: [
            { text: 'Docker 部署', link: '/deployment/docker' },
            { text: '环境配置', link: '/deployment/environment' },
            { text: '故障排查', link: '/deployment/troubleshooting' }
          ]
        }
      ],
      '/api/': [
        {
          text: 'API 文档',
          items: [
            { text: '概览', link: '/api/' },
            { text: '认证接口', link: '/api/auth' },
            { text: '机器人接口', link: '/api/bots' },
            { text: '用户接口', link: '/api/users' },
            { text: '订单接口', link: '/api/orders' }
          ]
        }
      ]
    },

  socialLinks: [
    { icon: 'github', link: 'https://github.com/yourusername/nlbot-vitepress' }
  ],

    footer: {
      message: '基于 VitePress 构建',
      copyright: 'Copyright © 2025 TGNL Admin'
    },

    search: {
      provider: 'local'
    }
  }
})
