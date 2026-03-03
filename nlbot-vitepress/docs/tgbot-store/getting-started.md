---
title: 部署指南
description: 独角数卡 + TG 发卡机器人部署教程
layout: doc
sidebar: true
aside: true
outline: [2, 3]
lastUpdated: true
---

# 部署指南

本指南将帮助您将 **TG 发卡机器人** 成功部署并连接到您的独角数卡系统。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg> 前置条件

在开始之前，请确保您已满足以下条件：

1.  **已部署独角数卡**：您需要有一个正在运行的独角数卡网站（v2.0.5+）。
2.  **服务器权限**：拥有独角数卡所在服务器的 SSH 访问权限或文件管理权限。
3.  **Telegram Bot**：已在 @BotFather 申请好一个新的机器人并获取 Token。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg> 部署步骤

### 1. 上传机器人文件
将购买获取的机器人程序包上传至服务器任意目录（建议与独角数卡同级），并解压。

### 2. 配置连接
编辑机器人目录下的 `config.php` 文件，填入您的独角数卡数据库信息：

```php
// 数据库配置示例
'db_host' => '127.0.0.1',
'db_name' => 'dujiaoka',
'db_user' => 'dujiaoka',
'db_pass' => '您的数据库密码',
```

### 3. 配置机器人 Token
在同级目录下的 `.env` 文件中填入您的 Telegram Bot Token：

```ini
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=您的TG_ID
```

### 4. 启动服务
使用以下命令启动机器人：

```bash
# 启动机器人
php start.php start -d
```

::: tip 提示
启动成功后，向您的机器人发送 `/start` 命令，如果机器人有回应，说明部署成功。
:::

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg> 常见问题

**Q: 机器人无法连接数据库？**
A: 请检查 `config.php` 中的数据库信息是否正确，并确保服务器防火墙允许本地连接。

**Q: 机器人没有响应？**
A: 请检查服务器是否能正常访问 Telegram API（需自行解决网络问题），或检查 `.env` 中的 Token 是否正确。

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
