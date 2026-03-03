---
title: 配置指南
description: 详细的系统配置说明
layout: doc
sidebar: true
aside: true
outline: [2, 3]
editLink: true
lastUpdated: true
head:
  - - meta
    - name: keywords
      content: config, env, settings, parameters
---

# 配置指南

TelegramPress 的配置主要分为两部分：环境变量配置 (`.env`) 和 机器人应用配置 (`al.py` / `config.txt`)。

## 环境变量 (.env)

`.env` 文件控制着 Docker 容器的基础设置，如数据库连接、端口映射等。

```bash
# 数据库配置
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=tgnl
MYSQL_USER=tgnl_user
MYSQL_PASSWORD=your_db_password

# Web 服务端口
PORT=35474

# 其他系统配置...
```

::: warning 安全警告
请务必修改默认的数据库密码，防止被暴力破解。
:::

## 机器人配置

机器人逻辑的核心配置通常位于 `nl-2333/al.py` 头部或同级目录下的配置文件中。

### 关键参数说明

| 参数名 | 说明 | 示例 |
| :--- | :--- | :--- |
| `api_key` | 能量池 API Key | `your_api_key` |
| `privateKey` | 出款钱包私钥 | `xxxxxxxx` (注意保密) |
| `control_address` | 收款钱包地址 | `TRX_Address...` |
| `username` | API 账户名 | `HFTGID` |
| `CUSTOMER_SERVICE_ID` | 客服 TG 链接/ID | `https://t.me/service` |

### 价格配置

您可以设置不同时长的能量租赁单价：

- `hour_price`: 1小时单价
- `day_price`: 1天单价
- `three_day_price`: 3天单价
- `yucun_price`: 预存单价

## 后台配置

登录 Web 管理后台后，您还可以进行动态配置：

1. **机器人管理**：设置 Token、管理员 ID。
2. **能量池配置**：添加和管理对接的能量池节点。
3. **商品管理**：上架或下架能量租赁套餐。

::: tip 提示
修改 `.env` 或代码级配置后，通常需要重启容器才能生效：
`docker compose restart`
:::
