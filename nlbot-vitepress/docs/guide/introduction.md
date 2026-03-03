---
title: 项目介绍
description: TelegramPress (TGNL Admin) 项目的详细介绍
layout: doc
sidebar: true
aside: true
outline: [2, 3]
editLink: true
lastUpdated: true
head:
  - - meta
    - name: keywords
      content: telegram, bot, tron, energy, leasing, admin
---

# 项目介绍

**TelegramPress (TGNL Admin)** 是一个基于 Telegram Bot 和 Web 管理面板的波场（Tron）能量租赁与自动发货系统。它集成了能量池管理、自动监控、用户自助购买等功能，旨在为波场生态用户提供便捷的能量获取服务。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg> 界面预览

<div class="screenshot-grid">
  <div class="screenshot-card">
    <img src="/images/preview-1.png" alt="数据仪表盘" class="screenshot-img" />
    <div class="screenshot-caption">数据仪表盘 - 实时监控业务状态</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-2.png" alt="机器人管理" class="screenshot-img" />
    <div class="screenshot-caption">机器人管理 - 可视化配置参数</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-3.png" alt="自定义键盘" class="screenshot-img" />
    <div class="screenshot-caption">自定义键盘 - 灵活定制用户交互</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-4.png" alt="系统设置" class="screenshot-img" />
    <div class="screenshot-caption">系统设置 - 全局参数一键管理</div>
  </div>
</div>

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg> 核心功能

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg> 智能机器人
- **自动化交易**：全天候 24/7 自动响应用户订单，秒级能量派发。
- **自定义回复**：支持自定义关键词回复、欢迎语、操作指引等。
- **多级分销**：内置邀请返利机制，促进用户裂变增长。

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg> 强大的管理后台
- **可视化仪表盘**：实时展示订单量、成交额、新增用户等关键指标。
- **多能量池调度**：支持添加多个能量池 API，智能负载均衡，保障货源稳定。
- **用户画像管理**：详细的用户行为记录，支持封禁、余额调整等操作。

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg> 安全与稳定
- **私钥本地存储**：出款私钥仅在本地服务器加密存储，确保资金安全。
- **Docker 容器化**：服务间相互隔离，部署简单，扩展性强。
- **异常自动报警**：系统异常或能量不足时自动通知管理员。

## 架构概览

项目主要由以下几个部分组成：

- **Bot 服务 (Python)**：负责处理 Telegram 消息、用户交互、订单处理和链上交互。
- **Web 服务 (Nuxt/Node.js)**：提供管理后台 API 和前端页面。
- **数据库 (MySQL/Redis)**：存储用户数据、订单记录和缓存队列。
- **Nginx**：作为反向代理服务器，处理 HTTP 请求。

## 适用场景

- **能量租赁商**：搭建自己的能量租赁平台，通过 TG 机器人自动售卖能量。
- **波场开发者**：集成能量租赁功能到自己的应用中。
- **社区运营者**：为社区成员提供低价能量租赁福利。

::: tip 提示
本项目开源版本仅供学习和研究使用，商业用途请遵守相关开源协议。
:::
