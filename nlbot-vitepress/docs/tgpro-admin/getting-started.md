---
title: 部署指南
description: TGPro Admin 系统部署与环境配置
layout: doc
sidebar: true
aside: true
outline: [2, 3]
lastUpdated: true
---

# 部署指南

本指南将帮助您快速在服务器上部署 TGPro Admin 系统。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg> 环境准备

在开始之前，请确保服务器满足以下要求：
1.  **操作系统**：Linux (推荐 Ubuntu 20.04+ / Debian 10+)
2.  **基础软件**：已安装宝塔面板（可选，推荐新手使用）或熟悉命令行操作。
3.  **容器环境**：已安装 Docker 和 Docker Compose。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg> 部署步骤

<div class="video-container">
  <iframe src="//player.bilibili.com/player.html?isOutside=true&aid=116064042096273&bvid=BV1yscnzSEoM&cid=36042182004&p=1&high_quality=1&danmaku=0" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>
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

### 1. 获取源码

请前往 GitHub Releases 页面下载最新版本的源码包：

<a href="https://github.com/cnmbdb/hf-tgpro-admin/releases" target="_blank" class="vp-button-green">
  <svg height="20" viewBox="0 0 16 16" version="1.1" width="20" aria-hidden="true" style="margin-right: 8px; fill: currentColor;"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
  下载源码
</a>

下载后将文件上传至服务器目录（例如 `/www/wwwroot/tgpro-admin`），并解压。

::: warning 权限设置
请务必将解压后的文件目录权限设置为 **777**，以确保容器能正常读写数据。
```bash
chmod -R 777 /www/wwwroot/tgpro-admin
```
:::

### 2. 获取关键配置信息

在配置环境变量前，您需要先获取以下关键信息：

#### A. 波场 (Tron) API
1.  访问 [TronGrid 官网](https://www.trongrid.io/) 注册并登录。
2.  下载并安装 TronLink 浏览器插件。
3.  在 TronGrid 首页关联您的钱包地址。
4.  申请并升级 API Key（建议申请 50w 访问量的 Key）。

#### B. Fragment 认证信息 (用于高级功能)
如果您需要使用 Fragment 相关功能（如用户名拍卖、匿名号码等），需要获取 Hash 和 Cookie。

1.  访问 [Fragment 官网](https://fragment.com/)。
2.  登录您的 Telegram 和 TON 钱包。
3.  在首页点击右上角的“会员界面”或任意交互入口。
4.  按 `F12` 打开浏览器开发者工具，切换到 **Network (网络)** 标签页。
5.  在页面上进行任意操作（如输入用户名 `@aaaa` 并回车搜索）。
6.  在 Network 面板中找到任意以 `api` 开头的请求。
7.  点击该请求，在 **Headers** 或 **Payload** 中找到并复制 `hash` 和 `cookie` 值。

### 3. 配置环境变量

将项目根目录下的 `.env.example` 文件重命名为 `.env`，并编辑填入上述信息。

```bash
mv .env.example .env
vim .env
```

**重点修改项：**
*   `BOT_TOKEN`: 您的机器人 Token。
*   `TRON_API_KEY`: 您的波龙 API Key。
*   `FRAGMENT_HASH`: 刚才获取的 Hash。
*   `FRAGMENT_COOKIE`: 刚才获取的 Cookie。

### 4. 启动服务

在项目根目录下执行以下命令启动：

```bash
docker compose up -d --build
```

::: tip 启动成功
当看到所有容器状态为 `Up` 时，说明部署成功。您可以通过浏览器访问服务器 IP + 端口进入管理后台。
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
