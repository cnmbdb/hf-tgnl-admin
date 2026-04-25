# 项目介绍

**TelegramPress (TGNL Admin)** 是一个基于 Telegram Bot 和 Web 管理面板的波场（Tron）能量租赁与自动发货系统。它集成了能量池管理、自动监控、用户自助购买等功能，旨在为波场生态用户提供便捷的能量获取服务。

## 界面预览

- **数据仪表盘** - 实时监控业务状态
- **机器人管理** - 可视化配置参数
- **自定义键盘** - 灵活定制用户交互
- **系统设置** - 全局参数一键管理

## 核心功能

### 智能机器人

- **自动化交易**：全天候 24/7 自动响应用户订单，秒级能量派发
- **自定义回复**：支持自定义关键词回复、欢迎语、操作指引等
- **多级分销**：内置邀请返利机制，促进用户裂变增长

### 强大的管理后台

- **可视化仪表盘**：实时展示订单量、成交额、新增用户等关键指标
- **多能量池调度**：支持添加多个能量池 API，智能负载均衡，保障货源稳定
- **用户画像管理**：详细的用户行为记录，支持封禁、余额调整等操作

### 安全与稳定

- **私钥本地存储**：出款私钥仅在本��服务器加密存储，确保资金安全
- **Docker 容器化**：服务间相互隔离，部署简单，扩展性强
- **异常自动报警**：系统异常或能量不足时自动通知管理员

## 架构概览

项目主要由以下几个部分组成：

- **Bot 服务 (Python)**：负责处理 Telegram 消息、用户交互、订单处理和链上交互
- **Web 服务 (Nuxt/Node.js)**：提供管理后台 API 和前端页面
- **数据库 (MySQL/Redis)**：存储用户数据、订单记录和缓存队列
- **Nginx**：作为反向代理服务器，处理 HTTP 请求

## 适用场景

- **能量租赁商**：搭建自己的能量租赁平台，通过 TG 机器人自动售卖能量
- **波场开发者**：集成能量租赁功能到自己的应用中
- **社区运营者**：为社区成员提供低价能量租赁福利

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

### 1. 准备服务器和安装宝塔 (可选)

如果您习惯使用图形化面板，可以安装宝塔面板（建议使用纯净版）。
如果熟悉命令行，可以直接在终端操作。

### 2. 获取源码

将项目源码上传至服务器，或者直接克隆仓库（假设您有 Git）：

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

#### 如何配置 Cloudflare Turnstile（验证码）

Cloudflare Turnstile 是一种隐私友好的验证码服务。

**1. 获取 Site Key 和 Secret Key：**
- 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
- 进入 "Security" → "Turnstile"
- 点击 "Add a subdomain"，填写您的域名
- 创建后获取 **Site Key** 和 **Secret Key**

**2. 在 .env 中配置：**

```bash
# ================== Cloudflare Turnstile ==================
TURNSTILE_SITE_KEY=0x4AAAAAAAxxxxxxxxxxxxxxxx
TURNSTILE_SECRET_KEY=1x00000000xxxxxxxxxxxxxxxx
```

#### 如何配置 Cloudflare Tunnel（内网穿透）

Cloudflare Tunnel 允许将本地服务暴露到互联网，无需公网 IP。

**1. 安装 cloudflared：**

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb
```

**2. 登录并创建隧道：**

```bash
cloudflared tunnel login
cloudflared tunnel create tgnl-admin-tunnel
```

**3. 获取 Tunnel ID 和 Token：**
- 创建成功后显示 **Tunnel ID**
- 在 Cloudflare Zero Trust Dashboard → "Networks" → "Tunnels" 获取 **Token**

**4. 在 .env 中配置：**

```bash
# ================== Cloudflare Tunnel ==================
CFTUN_TUNNEL_ID=a1b2c3d4-5678-90ab-cdef-1234567890ab
CFTUN_TOKEN=eyJhIjoiNjk5OTk5OTktOTk5OS05OTk5LTAwMDAtMDAwMD
```

**5. 配置 DNS 记录：**

| Type | Name | Target | Proxy status |
| :--- | :--- | :--- | :--- |
| CNAME | admin | `Tunnel ID` | Proxied |

> 请妥善保管您的 Secret Key 和 Token，不要泄露或提交到公共代码仓库。

### 5. 启动服务

使用 Docker Compose 构建并启动所有服务：

```bash
docker compose up -d --build
```

此命令将自动下载依赖、构建镜像并启动管理后台、数据库和机器人服务。

> 首次构建可能需要几分钟时间，请耐心等待。

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

## 激活授权

> 系统部署完成后，默认处于未激活状态，无法直接使用。请按照以下步骤完成授权。

### 1. 注册与购买

前往 **[HFZ.PW 官网](https://hfz.pw)** 注册账户并登录，在商城中找到对应的产品进行购买。

### 2. 配置授权 IP

购买成功后，进入 **个人资料** 页面，在 **授权 IP** 栏位填写您的服务器 IP 地址。

- **格式**: `http://IP1,http://IP2,`
- **示例**: `http://113.123.123.123,http://111.222.234.234,`
- **注意**: 多个 IP 请使用英文逗号 `,` 分隔。

### 3. 填写激活码

在系统的激活/授权页面，填写您的 **商品订单号** 作为激活码。

> - **标准版限制**: 每个授权码最多支持绑定 **4 个** 服务器 IP。
> - **灵活管理**: 您可以随时在官网后台自行修改授权 IP，方便切换服务器或进行转卖。

---

# 配置指南

TelegramPress 的配置主要分为三部分：环境变量配置 (`.env`)、Cloudflare 安全配置、以及机器人应用配置 (`al.py` / `config.txt`)。

## 环境变量 (.env)

`.env` 文件控制着 Docker 容器的基础设置，如数据库连接、端口映射、安全验证和隧道连接等。

### 数据库配置

```bash
# ================== 数据库配置 ==================
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=tgnl
MYSQL_USER=tgnl_user
MYSQL_PASSWORD=your_db_password

# Web 服务端口
PORT=35474

# 其他系统配置...
```

### Cloudflare Turnstile 配置

Cloudflare Turnstile 是一种隐私友好的验证码服务，用于保护您的网站免受机器人攻击。

**如何获取 Cloudflare Turnstile 的 Site Key 和 Secret Key：**

1. **访问 Cloudflare Dashboard**
   登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)，选择您的域名或创建一个站点。

2. **进入 Turnstile 设置**
   - 在左侧菜单中选择 "Security" → "Turnstile"
   - 点击 "Add a subdomain" 或 "Add site"

3. **创建 Turnstile 站点**
   - **Site Name**: 输入您的站点名称（如：`tgnl-admin`）
   - **Domain**: 输入您的域名（如：`example.com`，不要加 `https://`）
   - **Widget Type**: 选择 `Managed`（托管式）或 `Invisible`（隐形）
   - 点击 "Create"

4. **获取密钥**
   创建成功后，您会看到：
   - **Site Key**: 用于前端代码中（如 `0x4AAAAAAA...`）
   - **Secret Key**: 用于后端验证（如 `1x00000000...`）

> 请妥善保管您的 Secret Key，不要在前端代码中暴露。

### Cloudflare Tunnel 配置

Cloudflare Tunnel（也称为 `cloudflared`）允许您将本地服务安全地暴露到互联网，无需公网 IP 或复杂的防火墙配置。

**如何获取 Cloudflare Tunnel 的 Tunnel ID 和 Token：**

1. **安装 cloudflared**
   在您的服务器上安装 Cloudflare Tunnel 客户端：

   ```bash
   # Debian/Ubuntu
   curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
   sudo dpkg -i cloudflared.deb
   ```

2. **登录 Cloudflare 账号**

   ```bash
   cloudflared tunnel login
   ```

   这会打开一个浏览器窗口，让您授权 Cloudflare 访问您的账号。

3. **创建隧道**

   ```bash
   cloudflared tunnel create tgnl-admin-tunnel
   ```

   成功后会显示您的 **Tunnel ID**（类似于 `a1b2c3d4-5678-90ab-cdef-1234567890ab`）

4. **获取 Tunnel Token**

   创建隧道后，您需要获取 Token 来运行隧道：

   ```bash
   # 查看隧道列表
   cloudflared tunnel list

   # 运行隧道（使用 Token）
   cloudflared tunnel run --token <YOUR_TOKEN>
   ```

   或者在 Cloudflare Zero Trust Dashboard 中：
   - 进入 "Networks" → "Tunnels"
   - 点击您的隧道名称
   - 在 "Connections" 标签页中查看或创���新的 Token

5. **配置 DNS 路由**

   在 Cloudflare 的 DNS 设置中，添加一条 CNAME 记录指向您的隧道：

   | Type | Name | Target | Proxy status |
   | :--- | :--- | :--- | :--- |
   | CNAME | admin | `a1b2c3d4-5678-90ab-cdef-1234567890ab` | Proxied |

> **安全警告**
> - 请务必修改默认的数据库密码，防止被暴力破解。
> - Tunnel Token 是敏感信息，请勿泄露或提交到公共代码仓库。
> - 建议使用环境变量文件（`.env`）来管理这些敏感配置，并确保该文件被 `.gitignore` 忽略。

### 完整 .env 配置示例

以下是包含所有配置项的完整示例：

```bash
# ================== 数据库配置 ==================
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=tgnl
MYSQL_USER=tgnl_user
MYSQL_PASSWORD=your_db_password

# ================== 服务端口 ==================
PORT=35474

# ================== Cloudflare Turnstile ==================
TURNSTILE_SITE_KEY=0x4AAAAAAAxxxxxxxxxxxxxxxx
TURNSTILE_SECRET_KEY=1x00000000xxxxxxxxxxxxxxxx

# ================== Cloudflare Tunnel ==================
CFTUN_TUNNEL_ID=a1b2c3d4-5678-90ab-cdef-1234567890ab
CFTUN_TOKEN=eyJhIjoiNjk5OTk5OTktOTk5OS05OTk5LTAwMDAtMDAwMD
```

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

1. **机器人管理**：设置 Token、管理员 ID
2. **能量池配置**：添加和管理对接的能量池节点
3. **商品管理**：上架或下架能量租赁套餐

> 修改 `.env` 或代码级配置后，通常需要重启容器才能生效：`docker compose restart`

---

# 功能说明

本页将详细介绍管理后台的各项核心功能与配置方法。

## 基础配置详解

进入后台 **机器人管理** -> **基础配置** 页面，您会看到核心参数配置面板。这些参数直接决定了机器人的运行逻辑、资金安全及对外展示信息。

### 1. 核心身份信息

这些配置项定义了机器人在 Telegram 网络中的"身份证"���及管理员权限。

| 配置项 | 说明 | 填写规范 / 示例 |
| :--- | :--- | :--- |
| **Bot Token** | 机器人的 API 令牌 | 从 [@BotFather](https://t.me/BotFather) 申请，格式如 `123456:ABC-DEF...` |
| **管理员 ID** | 超级管理员的 Telegram User ID | 纯数字 ID，例如 `821234563`。拥有最高管理权限。 |
| **机器人 ID** | 机器人的对外链接标识 | 填写您的机器人链接，如 `http://t.me/your_bot_username` |
| **用户名** | 用于内部 API 鉴权的用户名 | 部署好默认是空的。TG 机器人管理员只需对机器人发送关键词 `查询后台信息`，系统会自动生成并填写此处��� |
| **密码** | 用于内部 API 鉴权的密码 | 同上。TG 机器人管理员只需对机器人发送关键词 `查询后台信息`，系统会自动生成并填写此处。 |

### 2. 运营与导流配置

设置用户与机器人交互时的联系方式、推广链接及广告策略。

- **客服链接**: 用户在机器人菜单点击"联系客服"时跳转的地址（如 `https://t.me/YourService`）
- **群组链接**: 您的官方用户交流群链接（如 `https://t.me/YourGroup`），引导用户加入社区
- **广告时间**: 广播消息或通知在用户端保留的时长（单位：秒）
  - *示例*: `940` (约 15 分钟后自动删除，避免打扰用户)

### 3. 钱包与资金配置

配置用于收付款的 TRON 钱包信息，这是机器人进行 USDT/TRX 交易的基础。

> **资金安全警告**
> **私钥 (Private Key)** 是您资产安全的唯一凭证。
> 1. 系统采用高强度加密存储，但请确保您的服务器环境安全。
> 2. **切勿** 将私钥透露给任何第三方，包括开发人员。
> 3. 如果怀疑私钥泄露，请立即转移资产并更换控制地址。

| 配置项 | 说明 |
| :--- | :--- |
| **控制地址** | 机器人的 TRON 主网地址 (Base58格式)。这是系统中**唯一**的地址，同时用于：1. **能量出租**：作为代理支付能量费用的账户。2. **收款地址**：接收用户充值的 USDT 和兑换的 TRX。 |
| **私钥** | 对应控制地址的私钥。**这是收到 USDT 后自动兑换并出款 TRX 的必要凭证。** |
| **汇率折扣** | USDT 兑换 TRX 的汇率调整系数。用于微调兑换比例，确保在汇率波动时仍能保持合理的兑换利润。 |

### 4. 系统对接与 API

用于连接能量池后端服务，确保订单能够实时处理。

> 机器人通过 HTTP 回调与能量池系统进行双向通信。请确保回调地址配置正确，否则会导致充值不到账。

- **能量池 API**: 上游能量池服务的接口地址。
  ```
  https://tgnl-home.hfz.pw
  ```
- **机器人回调地址 (bot_notify_url)**:
  - 能量池系统向机器人推送「充值成功 / 余额变动」等通知时使用的 HTTP 回调地址。
  - **格式**: 通常为 `http://机器人服务器IP:8080/api/recharge-notify`
  - *注意*: 请确保服务器防火墙已放行该端口，允许外部访问。

### 5. 价格配置 (单价/65000能量)

这里设置的是 **每 65,000 能量** 的租赁单价（单位：TRX）。

| 价格类型 | 适用场景 | 说明 |
| :--- | :--- | :--- |
| **小时价格** | 1 小时租赁 | 适用于临时转账需求，价格通常最低。 |
| **日价格** | 1 天租赁 | 适合大多数日常转账用户，性价比适中。 |
| **三日价格** | 3 天租赁 | 适合需要较长时间保留能量的用户。 |
| **预存价格** | 预存套餐 | 用户预先购买能量包的优惠单价，鼓励用户囤货。 |

### 6. Tron API 配置 (TronGrid)

> 配置 TronGrid API Key 是保障机器人高并发稳定运行的关键。
> **强烈建议**完成此配置，它能将您的 API 请求额度从免费版的低频限制提升至 **500,000 次/天**，彻底告别"请求过多"导致的订单卡顿。

#### 获取与配置流程

**1. 注册与登录**
访问 [TronGrid 官网](https://www.trongrid.io/)，使用邮箱注册账号并登录。

**2. 关联钱包 (关键步骤)**
点击右上角头像 -> **Integrate Wallet (关联钱包)**。
- **注意**: 必须绑定您在后台填写的 **控制地址 (收款地址)**。
- 此步骤需要您的浏览器已安装 [TronLink 插件](https://www.tronlink.org/)。

> 如果点击"关联"后一直转圈或失败，请尝试：
> 1. **检查插件状态**: 确保 TronLink 插件已"点亮"并固定在浏览器工具栏，且已登录对应的钱包地址。
> 2. **浏览器环境**: 推荐使用 **Google Chrome** 浏览器。避免使用全屏模式。
> 3. **重启大法**: 关闭浏览器重新打开，或更换一台电脑尝试。

**3. 创建 API Key**
关联成功后，在 Dashboard 点击 **Create API Key**。
- 自定义一个名称（如 `NLBot`）
- 创建成功后，复制显示的 API Key 字符串。

**4. 填入后台**
回到机器人后台 -> **基础配置** -> **Tron API Key**，粘贴刚才复制的 Key。
系统会自动保存，无需重启即可生效。

## 常用功能概览

除了基础配置，后台还提供以下核心管理模块，助您高效运营。

### 仪表盘 (Dashboard)

实时监控系统运行状态，助您运筹帷幄：
- **核心指标**: 今日订单数、总成交额、新增用户数
- **系统状态**: 实时监控内存占用、CPU 负载及网络流量

### 订单管理

全方位的订单追踪与处理能力：
- **能量订单**: 查看所有租赁记录，支持按状态筛选
- **异常处理**: 对于失败的订单，提供一键**补单**或**退款**功能，提升用户体验

### 用户管理

- **资产管理**: 支持手动给用户加款（充值）或扣款
- **风控管理**: 对违规用户进行封禁或解封操作

### 机器人指令 (用户端)

用户与 Telegram 机器人交互时的常用指令：

| 指令 | 描述 |
| :--- | :--- |
| `/start` | 启动机器人，查看主菜单 |
| `购买能量` | 点击菜单按钮，自助选择时长和数量 |
| `查询订单` | 查询最近的租赁订单状态 |
| `个人中心` | 查看账户余额、推广链接及邀请人数 |
| `联系客服` | 获取人工客服联系方式 |

---

::: tip 提示
本项目开源版本仅供学习和研究使用，商业用途请遵守相关开源协议。
:::

## 相关链接

- 官网：https://hfz.pw
- Telegram：https://t.me/HTTGID
