---
title: 配置指南
description: TGBot-Ultra 系统详细配置说明
layout: doc
sidebar: true
aside: true
outline: [2, 3]
lastUpdated: true
---

# 配置指南

本系统包含两个核心服务 (`Admin` 和 `Job`)，它们各自拥有独立的配置文件。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg> 通用配置

以下配置在 `admin/.env` 和 `job/.env` 中通常保持一致，特别是数据库和 Redis 连接。

### 数据库 (PostgreSQL)

| 配置项 | 说明 | 默认值 (Docker) |
| :--- | :--- | :--- |
| `DB_CONNECTION` | 数据库类型 | `pgsql` |
| `DB_HOST` | 数据库主机名 | `postgres` |
| `DB_PORT` | 数据库端口 | `5432` |
| `DB_DATABASE` | 数据库名 | `tgbot` |
| `DB_USERNAME` | 数据库用户名 | `root` |
| `DB_PASSWORD` | 数据库密码 | `rootpassword` |

### 缓存 (Redis)

| 配置项 | 说明 | 默认值 (Docker) |
| :--- | :--- | :--- |
| `REDIS_HOST` | Redis 主机名 | `redis` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `REDIS_PASSWORD` | Redis 密码 | (留空) |
| `REDIS_DB` | 默认数据库索引 | `0` |

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"></path><path d="M12 6v6l4 2"></path></svg> Admin 服务配置

位于 `admin/.env`，主要控制后台管理系统的行为。

| 配置项 | 说明 | 示例 |
| :--- | :--- | :--- |
| `APP_URL` | 站点访问地址 | `http://localhost:8080` |
| `APP_ENV` | 环境模式 | `production` |
| `APP_DEBUG` | 调试模式 | `false` |
| `API_WEB_URL` | Job 服务 API 地址 | `http://job:9503` |

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg> Job 服务配置

位于 `job/.env`，主要控制机器人消息处理和后台任务。

| 配置项 | 说明 | 示例 |
| :--- | :--- | :--- |
| `NL_API_BASE_URL` | 上游能量池 API 地址 | `https://tgnl-home.hfz.pw` |
| `BOT_POLLING_INTERVAL` | 消息轮询间隔 (ms) | `200` |

::: warning API 通信
`Admin` 和 `Job` 服务之间需要相互通信，请确保 `API_WEB_URL` 配置正确，使其能在 Docker 网络中互相访问。
:::
