---
title: 配置指南
description: TGPro Admin 系统详细配置说明
layout: doc
sidebar: true
aside: true
outline: [2, 3]
lastUpdated: true
---

# 配置指南

本页详细说明了 `.env` 配置文件中的各项参数。请确保在启动服务前正确填写。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg> 基础配置

| 配置项 | 说明 | 示例 / 获取方式 |
| :--- | :--- | :--- |
| `BOT_TOKEN` | **(必填)** Telegram 机器人 Token | 联系 [@BotFather](https://t.me/BotFather) 获取 |
| `BOT_ADMIN_ID` | **(必填)** 管理员 TG ID | 联系 [@userinfobot](https://t.me/userinfobot) 获取 |
| `DEBUG_PASSWORD` | **(必填)** 后台管理登录密码 | 设置一个复杂的密码 |
| `WEB_PORT` | Web 后台映射端口 | 默认为 `54699`，可根据需要修改 |

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> 支付与钱包

### 波场 (TRON) / USDT
| 配置项 | 说明 |
| :--- | :--- |
| `TRON_API_KEY` | TronGrid API Key，用于查询 USDT 到账。请参考部署指南获取。 |
| `BOT_CONTROL_ADDRESS` | 您的波场收款地址 (TRC20)。 |

### TON 网络
| 配置项 | 说明 |
| :--- | :--- |
| `WalletMnemonic` | TON 钱包助记词（24个单词）。<br>**注意**: 请确保助记词正确，机器人将监控该钱包的入账信息。 |

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"></path><path d="M12 6v6l4 2"></path></svg> Fragment 高级配置

用于与 Fragment.com 交互（如用户名、匿名号码相关功能）。

| 配置项 | 说明 | 获取提示 |
| :--- | :--- | :--- |
| `ResHash` | Fragment 登录会话 Hash | 登录 Fragment 后通过 F12 抓包获取 |
| `ResCookie` | Fragment 登录会话 Cookie | 登录 Fragment 后通过 F12 抓包获取 |

::: warning 会话过期
Fragment 的 Hash 和 Cookie 可能会随时间或会话注销而过期。如果相关功能失效，请重新抓取并更新此配置，然后重启服务。
:::
