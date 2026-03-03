---
title: 功能说明
description: TGBot-Ultra 系统功能使用手册
layout: doc
sidebar: true
aside: true
outline: [2, 3]
lastUpdated: true
---

# 功能说明

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg> 管理后台

### 登录
*   **地址**: `http://您的IP:8080/admin/login`
*   **默认账号**: `trxadmin` 或 `admin`
*   **默认密码**: 请查看数据库或部署说明

### 核心模块

#### 1. 机器人管理 (Telegram)
*   **Bot 列表**: 添加、删除和管理多个 Telegram Bot。
*   **自定义回复**: 设置关键词回复规则。
*   **键盘菜单**: 可视化编辑 Bot 的底部菜单和内联键盘。
*   **消息广播**: 向 Bot 用户群发通知消息。

#### 2. 能量业务 (Energy)
*   **能量平台**: 对接第三方能量池，配置 API Key。
*   **价格配置**: 设置不同时长的能量租赁价格。
*   **订单管理**: 查看能量租赁订单状态（待支付、进行中、已完成）。

#### 3. 会员业务 (Premium)
*   **商品管理**: 上架 Telegram Premium 会员商品（3个月/6个月/12个月）。
*   **库存管理**: 管理会员赠送链接或代开库存。

#### 4. 商城系统 (Shop)
*   **商品分类**: 创建虚拟商品分类。
*   **卡密管理**: 批量导入/导出卡密 (CD-Key)。
*   **自动发货**: 用户支付成功后自动发送卡密。

#### 5. 监控系统 (Monitor)
*   **地址监控**: 添加需要监控的 TRON 钱包地址。
*   **动账通知**: 配置资金变动通知的目标群组或频道。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg> 常用运维命令

```bash
# 查看所有服务状态
docker compose ps

# 查看 Job 服务日志 (排查消息处理问题)
docker compose logs -f job

# 查看 Admin 服务日志
docker compose logs -f admin

# 重启所有服务
docker compose restart
```
