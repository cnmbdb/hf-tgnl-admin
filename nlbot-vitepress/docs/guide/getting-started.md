---
title: 快速开始
description: TelegramPress 项目的安装和部署指南
layout: doc
sidebar: true
aside: true
outline: [2, 3]
editLink: true
lastUpdated: true
head:
  - - meta
    - name: keywords
      content: install, deploy, docker, setup
---

# 快速开始

本指南将帮助您快速在服务器上部署 TelegramPress 系统。我们推荐使用 Docker Compose 进行部署，这是最简单且最稳定的方式。

## 环境准备

在开始之前，请确保您的服务器满足以下要求：

- **操作系统**：任意 Linux 发行版（推荐 Ubuntu 20.04+ / Debian 10+）
- **软件依赖**：
  - [Docker](https://docs.docker.com/get-docker/)
  - [Docker Compose](https://docs.docker.com/compose/install/)
- **硬件配置**：建议 2核 4G 内存及以上
- **网络**：服务器需能访问 Telegram API 和波场节点

## 部署步骤

<div class="video-container">
  <iframe src="//player.bilibili.com/player.html?bvid=BV1wfrVB1EQ2&page=1&high_quality=1&danmaku=0" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>
</div>

<style>
.video-container {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
  height: 0;
  margin: 24px 0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}
.video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>

### 1. 准备服务器和安装宝塔 (可选)

如果您习惯使用图形化面板，可以安装宝塔面板（建议使用纯净版）。
如果熟悉命令行，可以直接在终端操作。

### 2. 获取源码

将项目源码上传至服务器，或者直接克隆仓库（假设您有 Git）：

<a href="https://github.com/cnmbdb/hf-tgnl-admin" target="_blank" class="vp-button-green">
  <svg height="20" viewBox="0 0 16 16" version="1.1" width="20" aria-hidden="true" style="margin-right: 8px; fill: currentColor;"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
  源码下载
</a>

```bash
# 创建目录
mkdir -p /www/wwwroot/tgnl-admin
cd /www/wwwroot/tgnl-admin

# 上传源码文件到此目录，并解压
# 确保解压后的目录结构包含 docker-compose.yml
```

### 3. 文件权限设置

为了确保 Docker 容器内的服务能正常读写文件，建议设置权限：

```bash
# 设置目录权限
chmod -R 777 .
```

### 4. 配置环境变量

复制示例配置文件并进行修改：

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑配置文件
vim .env
```

您需要修改 `.env` 文件中的关键信息（如数据库密码、端口等）。同时，也需要检查 `nl-2333/config.txt` (如果有) 或相关 Bot 配置文件。

### 5. 启动服务

使用 Docker Compose 构建并启动所有服务：

```bash
docker compose up -d --build
```

此命令将自动下载依赖、构建镜像并启动管理后台、数据库和机器人服务。

::: info 等待启动
首次构建可能需要几分钟时间，请耐心等待。
:::

### 6. 验证部署

查看容器运行状态：

```bash
docker compose ps
```

如果所有容器状态均为 `Up`，则说明启动成功。

访问管理面板：
- 打开浏览器访问：`http://服务器IP:35474` (端口默认为 35474，或您在 `.env` 中设置的端口)

## 初始设置

1. **登录后台**
   - 默认账号：`admin`
   - 默认密码：`admin123`
   
2. **授权激活**
   - 进入后台 -> 授权激活
   - 填写激活码（如果是开源版或测试版，可能有特定的激活方式，或者直接使用）

3. **配置机器人**
   - 进入后台 -> 机器人管理
   - 填写机器人 Token（从 [@BotFather](https://t.me/BotFather) 获取）
   - 填写管理员 TG ID
   - 点击保存并重启机器人

::: tip 恭喜
至此，您的 TelegramPress 系统已成功部署并运行！
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
