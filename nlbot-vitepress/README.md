# TGNL Admin 文档

这是 TGNL Admin 项目的 VitePress 文档站点。

## 本地开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 部署

本项目设计用于部署到阿里云 Pages，通过 GitHub 仓库自动拉取和部署。

### 部署步骤

1. 将代码推送到 GitHub 仓库 `nlbot-vitepress`
2. 在阿里云 Pages 中配置：
   - 源仓库：`yourusername/nlbot-vitepress`
   - 构建命令：`npm install && npm run build`
   - 输出目录：`docs/.vitepress/dist`

## 文档结构

```
docs/
├── index.md              # 首页
├── guide/                # 入门指南
│   ├── getting-started.md
│   ├── introduction.md
│   └── requirements.md
├── modules/              # 功能模块
│   ├── dashboard.md
│   ├── bots.md
│   └── ...
├── deployment/           # 部署指南
│   ├── docker.md
│   ├── environment.md
│   └── troubleshooting.md
└── api/                  # API 文档
    ├── index.md
    ├── auth.md
    └── ...
```

## 技术栈

- [VitePress](https://vitepress.dev/) - 文档生成框架
- Vue 3 - 前端框架
- TypeScript - 类型支持

## 许可证

MIT
