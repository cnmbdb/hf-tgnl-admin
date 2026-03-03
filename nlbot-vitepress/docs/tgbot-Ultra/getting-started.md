---
title: 部署指南
description: TGBot-Ultra 系统部署与环境配置
layout: doc
sidebar: true
aside: true
outline: [2, 3]
lastUpdated: true
---

# 部署指南

本指南将帮助您快速在服务器上部署 **TGBot-Ultra** 系统。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg> 环境准备

在开始之前，请确保服务器满足以下要求：
1.  **操作系统**：Linux (推荐 Ubuntu 20.04+ / Debian 10+)
2.  **基础软件**：已安装宝塔面板（可选，推荐新手使用）或熟悉命令行操作。
3.  **容器环境**：已安装 Docker 和 Docker Compose。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg> 部署步骤

### 1. 获取源码

请前往 GitHub Releases 页面下载最新版本的源码包：

<a href="https://github.com/cnmbdb/tgbot-Ultra-v1/releases" target="_blank" class="vp-button-green">
  <svg height="20" viewBox="0 0 16 16" version="1.1" width="20" aria-hidden="true" style="margin-right: 8px; fill: currentColor;"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
  下载源码
</a>

下载后将文件上传至服务器目录（例如 `/www/wwwroot/tgbot-ultra`），并解压。

::: warning 权限设置
请务必将解压后的文件目录权限设置为 **777**，以确保容器能正常读写数据。
```bash
chmod -R 777 /www/wwwroot/tgbot-ultra
```
:::

### 2. 配置环境变量

本系统包含两个核心服务：**Admin**（后台管理）和 **Job**（任务处理），它们各自有独立的配置文件。

#### A. Admin 服务配置
```bash
# 进入 admin 目录
cd admin
# 复制配置文件
cp .env.example .env
# 编辑配置
vim .env
```

#### B. Job 服务配置
```bash
# 进入 job 目录
cd ../job
# 复制配置文件
cp .env.example .env
# 编辑配置
vim .env
```

::: tip 关键配置一致性
请确保 `admin/.env` 和 `job/.env` 中的数据库连接信息 (`DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`) 和 Redis 配置保持一致。
:::

### 3. 启动服务

回到项目根目录（包含 `docker-compose.yml` 的目录），执行以下命令启动：

```bash
docker compose up -d --build
```

### 4. 验证部署

查看容器运行状态：
```bash
docker compose ps
```

如果所有容器状态均为 `Up`，则说明启动成功。

*   **管理后台**: `http://服务器IP:8080/admin/login`
    *   默认账号: `trxadmin` 或 `admin`
    *   默认密码: 请查看数据库或初始安装说明（通常为 `password` 或 `123456`，建议首次登录后修改）

::: info 数据库初始化
首次启动时，系统会自动执行 `001_init.sql` 脚本初始化数据库结构（包含表结构、初始数据和视图）。如果启动后无法登录，请检查数据库是否已成功导入数据。
:::

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg> 激活授权

::: warning 重要提示
系统部署完成后，默认处于未激活状态，无法直接使用。请按照以下步骤完成授权。
:::

### 1. 注册与购买
前往 **[HFZ.PW 官网](https://hfz.pw)** 注册账户并登录，在商城中找到对应的产品进行购买。

### 2. 配置授权 IP
购买成功后，进入 **个人资料** 页面，在 **授权 IP** 栏位填写您的服务器 IP 地址。

*   **格式**: `http://IP1,http://IP2,`
*   **示例**: `http://113.123.123.123,http://111.222.234.234,`
*   **注意**: 多个 IP 请使用英文逗号 `,` 分隔。

### 3. 填写激活码
在系统的激活/授权页面，填写您的 **商品订单号** 作为激活码。

::: tip 授权说明
*   **标准版限制**: 每个授权码最多支持绑定 **4 个** 服务器 IP。
*   **灵活管理**: 您可以随时在官网后台自行修改授权 IP，方便切换服务器或进行转卖。
:::
