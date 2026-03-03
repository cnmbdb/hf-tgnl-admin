---
title: 功能说明
description: TGPro Admin 系统操作与运维手册
layout: doc
sidebar: true
aside: true
outline: [2, 3]
lastUpdated: true
---

# 功能说明

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg> 管理后台

### 登录
*   **地址**: `http://您的IP:54699/fgxkd4ho` (默认端口 54699，路径 `fgxkd4ho` 为安全入口，建议部署后核对实际路径)
*   **账号**: `admin`
*   **密码**: 在 `.env` 中配置的 `DEBUG_PASSWORD`

### 核心模块
1.  **仪表盘**: 查看今日收入、订单量、用户增长曲线。
2.  **订单管理**:
    *   **会员订单**: 查看所有购买会员的交易记录，支持按支付方式 (USDT/TON) 筛选。
    *   **补单**: 对于区块链确认延迟导致的漏单，支持手动补单。
3.  **用户管理**:
    *   查看机器人所有用户列表。
    *   修改用户会员有效期、封禁违规用户。
4.  **配置中心**:
    *   动态修改机器人回复语、按钮布局等，无需重启。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> 机器人交互

用户端机器人的主要指令与功能：

*   `/start`: 启动机器人，进入主菜单。
*   **会员购买**: 点击菜单按钮 -> 选择套餐 -> 选择支付方式 (USDT/TON) -> 获取支付地址 -> 支付并自动到账。
*   **个人中心**: 查看会员剩余时长、推广邀请记录。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg> 常用运维命令

```bash
# 查看所有服务状态
docker compose ps

# 查看实时日志 (排查问题神器)
docker compose logs -f

# 重启服务 (修改配置后)
docker compose restart

# 停止服务
docker compose down
```
