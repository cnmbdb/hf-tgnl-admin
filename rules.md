# 系统提示词 - TGNL Admin（Nuxt3 + Telegram 机器人后台）

## 一、项目概述

TGNL Admin 是一个 **Telegram 机器人后台管理系统**，用于管理能量池 / 套餐 / 订单 / TG 用户与系统用户等功能。  
本项目基于 **Nuxt 3 全栈架构 + MySQL**，前端采用深色现代风格管理后台 UI，后端通过 Nitro API 与数据库及 Telegram 机器人进行交互。

## 二、核心技术栈技能（Skill 配置）

- **框架与语言**
  - Nuxt 3（Vue 3 Composition API，`app.vue` + 文件路由）
  - TypeScript
  - Nitro Server / server routes（`server/api/*.get.ts|post.ts|put.ts|delete.ts`）
- **UI 与样式**
  - @nuxt/ui（`UButton`, `UInput`, `UCard`, `UModal`, `UBadge`, `USelect` 等）
  - Tailwind CSS（深色主题，原子化类名）
- **数据库**
  - MySQL 8（`mysql2/promise`，封装在 `server/utils/database.ts` 的 `executeQuery`）
  - 核心表：`system_users`, `transactions`, `orders`, `bishu_packages`, `licenses`, `system_configs` 等
- **认证与安全**
  - 基于 Cookie 的会话（`userInfo`）
  - `server/utils/auth.ts` 中的 `requireAuth` / `requireAdmin`
  - DEV 开发登录（`.env` 中 `DEV_LOGIN_ENABLED / DEV_ADMIN_USER / DEV_ADMIN_PASS`）
- **部署与运行**
  - Docker + `docker-compose`
  - 多容器：`app` (Nuxt3) + `db` (MySQL) + `bot` (Python)
  - 构建镜像：`tgnl-admin-app:local`、`tgnl-admin-bot:local`
- **Telegram 机器人**
  - Python 机器人代码位于 `nl-2333/`（`al.py`, `config.txt`）
  - 与后台联动的数据表：`transactions`（余额 / 最后活跃）、`orders`、`bishu_packages`

## 三、目录与文件角色

```txt
tgnl-admin/
├── pages/                 # Nuxt 页面，包含用户管理、开发者设置等
│   └── users/index.vue    # 机器人用户 + 系统用户管理（重要）
├── server/
│   ├── api/               # 后端 API 端点
│   │   ├── login.post.ts              # 登录
│   │   ├── system-users.get|post|put|delete.ts
│   │   ├── tg-users.get.ts            # Telegram 用户列表（基于 transactions）
│   │   ├── tg-users.delete.ts         # Telegram 用户删除（按 chat_id）
│   │   ├── bot-*.post.ts              # 机器人余额/注册等接口
│   │   └── license/*.ts               # 授权相关
│   └── utils/
│       ├── database.ts                # executeQuery 封装
│       └── auth.ts                    # requireAuth / requireAdmin
├── nl-2333/              # Telegram 机器人代码（Python）
├── Dockerfile            # Nuxt3 app 构建镜像
├── docker-compose.yml    # app / db / bot 三容器编排
└── .env                  # 统一环境变量配置
```

## 四、UI / 交互设计风格

- **主题**
  - 深色：背景 `#0c0c0d`，卡片 `#1a1a1b`，边框 `#2a2a2b`
  - 主文字：白色；次要文字：`#9ca3af`
  - 强调色：Nuxt 绿 `#00dc82`（按钮、高亮、标签）
- **布局与组件**
  - 顶部标题 + 统计卡片 + 搜索过滤条 + 表格列表 + 分页
  - 卡片统一使用：
    - `bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4`
  - 操作按钮使用 `UButton`，图标用 `UIcon i-heroicons-*`
- **状态表现**
  - 状态徽章使用 `UBadge`：
    - 成功 / 活跃：`color="green" variant="subtle"`
    - 失败 / 禁用：`color="red" variant="subtle"`
    - 警告：`color="yellow" variant="subtle"`
  - 加载 / 删除 / 保存时 `:loading="..."` 并禁用按钮

## 五、系统提示词（面向开发助手）

**你现在在维护的项目是：`tgnl-admin`（Nuxt3 + Telegram 机器人后台）。在这个项目中：**

1. **前端规范**
   - 所有页面使用 `<script setup lang="ts">` 和 Composition API。
   - 优先使用 @nuxt/ui 组件，配合 Tailwind 类名做细节布局。
   - 遵循现有深色后台风格（参考 `pages/users/index.vue`）。
   - 表格操作区统一使用图标按钮（铅笔 / 垃圾桶）。
2. **后端规范**
   - 新增 API 端点放在 `server/api`，使用 `xxx.get.ts/.post.ts/.put.ts/.delete.ts` 命名。
   - 所有数据库访问统一通过 `executeQuery`，使用参数化查询防 SQL 注入。
   - API 返回统一结构：
     ```ts
     { success: true, message?: string, data?: any }
     { success: false, error: string }
     ```
   - 需要登录 / 管理员权限的接口必须先调用 `requireAuth` / `requireAdmin`。
3. **Telegram 相关**
   - Telegram 用户列表由 `tg-users.get.ts` 提供，只读自 `transactions` / `orders` / `bishu_packages`。
   - 删除 Telegram 用户时：**不要动系统用户表**，只按 `chat_id` 删除相关数据（使用 `tg-users.delete.ts` 已实现的策略）。
   - 机器人配置（如钱包地址、价格）优先从 `.env` 读取，Python 端通过挂载 `.env` 获取。
4. **安全与限制**
   - `system-users.delete.ts` 当前设计为单用户模式：禁止删除唯一管理员账号，如需改动需额外确认。
   - 修改登录逻辑时，必须同步维护：
     - Cookie 写入：`userInfo`（包含 id / username / role / status）
     - `last_login` 字段更新（`system_users`）

## 六、Skill 使用建议（给 AI / 开发者）

- 当涉及 **数据库设计 / 查询** 时：
  - 打开 `nl-admin.sql` 确认真实字段与索引，再修改 API。
- 当涉及 **Telegram 用户/余额/套餐**：
  - 首选表：`transactions`（余额 + 最后活跃）、`bishu_packages`（套餐）、`orders`（订单）。
  - 所有与 `chat_id` 相关的操作保持幂等：用户重新与机器人交互时可以自动重建数据。
- 当涉及 **前端交互**：
  - 始终保持「系统用户」与「Telegram 用户」两个 tab 逻辑分离，避免误用彼此 API。
  - 在 `users/index.vue` 中，任何新功能应根据 `activeTab` 分支处理。

## 七、Nuxt 与 Telegram 机器人的协作方式

- Nuxt 后台负责：
  - 管理系统用户和权限
  - 查看和管理 `transactions / orders / bishu_packages`
  - 对 Python 机器人进行配置与监控（通过数据库 / Docker / 环境变量）
- Python Telegram 机器人负责：
  - 与用户交互，将余额 / 套餐 / 日志写入数据库
  - 通过数据库与 Nuxt 后台解耦

在进行功能开发或重构时，请始终围绕以上约定与风格执行，保持 TGNL Admin 项目的整体一致性与稳定性。

