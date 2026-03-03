---
title: TGPro Admin 部署指南
description: TGPro Admin 系统部署与配置文档
layout: doc
sidebar: true
aside: true
outline: [2, 3]
lastUpdated: true
---

# TGPro Admin

**TGPro Admin** 是一套功能强大的 Telegram 机器人管理系统，支持 USDT (TRC20) 和 TON 支付，集成了自动发货、用户管理、数据统计等功能。通过现代化的 Web 管理后台，您可以轻松管理机器人配置和业务数据。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg> 环境要求

在开始部署之前，请确保您的服务器满足以下最低要求：

- **操作系统**: Linux (推荐 Ubuntu 20.04+)
- **容器环境**:
  - Docker 20.10 或更高版本
  - Docker Compose 2.0 或更高版本
- **硬件配置**:
  - 内存: 2GB+
  - 磁盘: 10GB+ 可用空间

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg> 部署步骤

### 1. 上传项目文件
将整个 `tgpro-admin` 目录上传至您的服务器目标位置。

### 2. 初始化配置
进入项目目录，复制示例配置文件并进行编辑：

```bash
cd tgpro-admin
cp .env.example .env
nano .env  # 或使用 vim/vi 编辑
```

### 3. 关键配置项
为了保证系统正常运行，您**必须**修改以下配置：

| 配置项 | 说明 | 示例/备注 |
| :--- | :--- | :--- |
| `BOT_TOKEN` | Telegram 机器人 Token | 从 @BotFather 获取 |
| `BOT_CONTROL_ADDRESS` | USDT (TRC20) 收款地址 | 您的波场钱包地址 |
| `BOT_ADMIN_ID` | 管理员 Telegram ID | 用于接收通知和权限验证 |
| `ResHash` / `ResCookie` | Fragment.com 认证信息 | 用于相关高级功能 |
| `WalletMnemonic` | TON 钱包助记词 | 用于处理 TON 支付 |
| `DEBUG_PASSWORD` | 后台登录密码 | 请设置强密码 |

### 4. 启动服务
确认配置无误后，使用 Docker Compose 一键启动所有服务：

```bash
docker compose up -d
```

此命令将自动拉取镜像、构建容器并在后台运行服务。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg> 系统管理

### 访问后台
服务启动成功后，您可以通过浏览器访问管理后台：

- **后台地址**: `http://服务器IP:54699/fgxkd4ho`
- **默认账号**: `admin`
- **默认密码**: 您在 `.env` 中设置的 `DEBUG_PASSWORD`

::: tip 安全建议
建议在 Nginx 反向代理层配置 SSL 证书，并通过域名访问，以提高安全性。
:::

### 查看日志
如果遇到问题，可以通过查看日志进行排查：

```bash
# 查看所有服务实时日志
docker compose logs -f

# 查看机器人服务日志
docker logs -f tgpro-bot

# 查看 Web 后台服务日志
docker logs -f tgpro-app
```

### 常用运维命令

```bash
# 重启所有服务
docker compose restart

# 重启单个服务 (如 bot)
docker compose restart bot

# 更新代码/配置后重新构建并启动
docker compose up -d --build

# 停止并删除所有容器
docker compose down

# 查看容器运行状态
docker compose ps
```

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> 目录结构说明

了解项目结构有助于您更好地维护系统：

```
tgpro-admin/
├── .env                    # 环境配置文件（核心敏感配置）
├── .env.example           # 配置模板文件
├── docker-compose.yml     # Docker 容器编排配置
├── Dockerfile             # Web 前端/后端构建文件
├── database/
│   └── init.sql           # 数据库初始化脚本
└── hf-tgpro/              # 机器人核心目录
    ├── Dockerfile         # 机器人环境构建文件
    ├── hy.py              # 机器人主程序入口
    ├── main               # TON 支付处理二进制程序
    └── keyword_replies.json # 自动回复规则配置
```
