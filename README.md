# hf-tgnl-admin

## 项目说明

演示机器人：[@HFTGNLTRXbot](https://t.me/HFTGNLTRXbot)

此目录用于**本地开发**，使用本地构建镜像。

- **镜像构建**: 本地构建 `tgnl-admin-app:local` 和 `tgnl-admin-bot:local`
- **服务器部署**: 请使用 `/Users/a2333/IDE/部署到服务器的文件/tgnl-admin` 目录

## 本地开发步骤

1. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，修改数据库密码等配置
   ```

2. **构建并启动**
   ```bash
   docker compose build
   docker compose up -d
   ```

3. **查看状态**
   ```bash
   docker compose ps
   docker compose logs -f
   ```

4. **推送镜像到 Docker Hub**（开发完成后）
   ```bash
   ./build-and-push.sh
   ```

## 常用命令

```bash
# 重启所有服务
docker compose restart

# 重启单个服务
docker compose restart app
docker compose restart bot

# 查看日志
docker compose logs -f app
docker compose logs -f bot

# 停止服务
docker compose down

# 重新构建并启动
docker compose build --no-cache
docker compose up -d
```

## 目录结构

```
tgnl-docker/
├── Dockerfile          # App 镜像构建文件
├── docker-compose.yml  # Docker 编排配置
├── .env.example        # 环境变量示例
├── nl-admin.sql        # 数据库初始化脚本
├── nl-2333/            # Telegram Bot 代码
│   ├── Dockerfile      # Bot 镜像构建文件
│   ├── al.py           # Bot 主程序
│   └── config.txt      # Bot 配置文件
├── server/             # Nuxt API 后端
├── pages/              # Nuxt 页面
├── components/         # Vue 组件
└── ...
```

## 能量池系统对接（重要：网络与配置）

机器人系统（本项目）会与能量池系统（`tgnl-home`）双向通讯：

- **机器人 → 能量池**：机器人调用能量池 API（创建订单/同步配置/查余额等）
  - 基地址由 `nl-2333/config.txt` 的 `energy_pool_api` 决定
- **能量池 → 机器人**：能量池回调机器人 HTTP 服务（充值成功/余额变动等）
  - 回调地址由 `nl-2333/config.txt` 的 `bot_notify_url` 决定（并同步到能量池的 `bot_configs.bot_notify_url`）

### config.txt 最小示例（不要把真实 token 提交到仓库）

在 `nl-2333/config.txt` 中配置：

```txt
TOKEN=REPLACE_ME
admin_id=REPLACE_ME
energy_pool_api=http://host.docker.internal:3000
bot_notify_url=http://localhost:8080/api/recharge-notify
username=your_api_username
password=your_api_password
```

### 本地开发推荐配置（能量池在宿主机，机器人在 Docker）

这是最常见的联调模式：

- **机器人 → 能量池**：容器访问宿主机，使用 `host.docker.internal`
  - `energy_pool_api=http://host.docker.internal:3000`
- **能量池 → 机器人**：宿主机访问容器映射端口，使用 `localhost`
  - `bot_notify_url=http://localhost:8080/api/recharge-notify`

> 说明：`host.docker.internal` 主要用于“容器访问宿主机”。如果把它用在回调地址上（宿主机→容器），很容易出现 `fetch failed / other side closed / empty reply` 等问题。

### 服务器部署推荐配置（能量池在远端服务器）

当能量池部署在服务器上时，`bot_notify_url` 必须是 **能量池服务器可访问** 的地址，例如：

```txt
energy_pool_api=https://energy-pool.example.com
bot_notify_url=https://bot.example.com/api/recharge-notify
# 或者（不走域名时）：
# bot_notify_url=http://<bot-server-ip>:8080/api/recharge-notify
```

## 安全建议（强烈建议）

目前仓库里存在 `nl-2333/config.txt` 与 `.env`（可能包含敏感信息）。建议：

- **不要提交真实 token**
  - `TOKEN`、Webhook、以及任何密钥不要进 Git
  - 生产环境使用服务器环境变量或私密配置文件
- **添加忽略规则**
  - 建议将 `.env`、`nl-2333/config.txt` 加入 `.gitignore`

## 键盘按钮页面开发（/pages/keyboard-buttons/index.vue）

### 已完成

- **主键盘菜单可视化**
  - 左侧卡片展示主键盘（回复键盘）当前真实布局：9 个按钮（📦 笔数套餐、预存扣费、USDT转TRX、查交易、TRX转能量、已监听地址、开始/结束监听、我要充值、个人中心）。
  - 支持在弹窗中**编辑键盘名称、按钮文案、行布局与状态**，并即时更新预览。
  - 预览弹窗以「行 × 按钮」的形式展示当前键盘布局，方便对照 Telegram 端实际键盘。
  - **页面加载时自动从机器人配置读取布局**：`onMounted()` 调用 `GET /api/keyboard-layout`，如果 API 成功返回有效数据则更新显示，失败时保留默认布局（数据保护机制）。

- **功能链映射**
  - 右侧卡片将主键盘的每个按钮映射为 1–9 号「功能链」，与左侧按钮顺序一一对应。
  - 点击功能链行会打开「功能链工作流详情」模态框，用于展示该按钮在机器人中的真实业务流程。

- **工作流可视化（简化版 n8n 风格）**
  - 引入 `WorkflowDefinition` 数据结构，将每个按钮的流程拆为：
    - 主线步骤（main steps）
    - 用户 / 机器人消息（user / bot）
    - 内联按钮分支（branches）
  - 对于 **1 号：📦 笔数套餐**：
    - 使用 `mode: 'tree'` 的工作流定义，主线只有一个节点：  
      「收到指令 & 展示入口按钮」——用户发送「📦 笔数套餐」，机器人回复规则说明并给出两个入口按钮。
    - 该节点下有两个分支：
      - **分支 A：已有套餐**  
        用户点击「已有套餐」，机器人从数据库读取该 chat_id 的笔数套餐列表并返回，供用户查看已激活 / 休眠套餐。
      - **分支 B：添加套餐**  
        用户点击「添加套餐」，机器人依次引导：
        1. 展示可选套餐按钮（5 笔 / 15T、15 笔 / 45T 等）；  
        2. 用户选择某一套餐；  
        3. 用户输入要绑定的 Tron 地址；  
        4. 机器人校验地址并提供「使用余额 / 立即支付」两种支付方式；  
        5. 支付成功后，在数据库写入套餐记录并标记为激活。
  - 前端展示上：
    - 顶部一条垂直主线，每个主线步骤为一个矩形卡片（包含标题 + 对话内容 + 按钮标签）。
    - 当步骤存在 `branches` 时，在该卡片下方水平展开多条「分支链」，每条分支链由若干小卡片垂直排列，形成树状结构。

- **主键盘与机器人同步机制（已完成）**
  - 后台修改按钮文案后，自动同步到机器人配置（`config.txt`）。
  - 机器人通过配置文件热加载机制（永不停止），在 1-2 秒内自动重载配置，无需重启。
  - 消息路由改为按 key 匹配，支持任意修改按钮文案而不影响功能。
  - 详细实现原理见下方「主键盘与机器人同步机制」章节。

### 规划中（未继续开发部分，仅记录设计意图）

- **按“用户动作”为粒度拆分所有步骤**
  - 一步 = 用户一次触发（发送消息 / 点击按钮 / 回复文本），机器人回复挂在该卡片下。
  - 每个卡片展示：
    - 用户输入内容（或点击的按钮）。
    - 机器人返回的文案说明、错误提示、下一步可选按钮。

- **树形工作流扩展到其他按钮**
  - 将「🛎 预存扣费」「✅ USDT转TRX」「⏰ 查交易」「⚡ TRX转能量」等按钮的逻辑，从 `nl-2333/al.py` 中抽象为同样的 `WorkflowTree` 数据结构。
  - 右侧工作流弹窗按相同排版规则展示：一条主线 + 若干分支，形成类似 n8n 的树状卡片布局（只读、不可拖拽）。

- **后续可选优化（暂不实施）**
  - 从静态定义升级为自动生成：通过分析 `al.py` 中的 handler / callback_data，将部分工作流节点半自动生成，减少手工维护成本。
  - 在工作流弹窗中加入「跳转到源码」入口，直接打开对应的 bot 逻辑位置，方便调试与联动修改。

## 主键盘与机器人同步机制

### 实现原理

主键盘菜单的 9 个按钮现在已与机器人代码（`nl-2333/al.py`）完全同步，支持在后台修改按钮文案后自动同步到机器人配置。

#### 1. 配置存储（`nl-2333/config.txt`）

- 新增配置项 `main_menu_buttons_json`，存储键盘布局的 JSON 字符串。
- 格式：`[[{key,label}], [{key,label},{key,label}], ...]`
- **key 固定不变**（用于代码逻辑路由），**label 可修改**（显示文案）。
- 9 个按钮的 key 固定为：
  - `bishu`（笔数套餐）
  - `yucun`（预存扣费）
  - `usdt2trx`（USDT转TRX）
  - `check_tx`（查交易）
  - `trx2energy`（TRX转能量）
  - `monitored_addresses`（已监听地址）
  - `toggle_monitor`（开始/结束监听）
  - `recharge`（我要充值）
  - `profile`（个人中心）

#### 2. 机器人代码改造（`nl-2333/al.py`）

- **全局变量**：
  - `main_menu_layout`：从配置加载的键盘布局
  - `label_to_key`：label → key 映射表，用于消息匹配

- **配置加载**：
  - `load_main_menu_config()`：解析 `config.txt` 中的 `main_menu_buttons_json`，构建布局和映射表。
  - `reload_config()`：调用 `load_main_menu_config()`，支持热重载。

- **键盘生成**：
  - `start()` 函数：从 `main_menu_layout` 读取布局，生成 Telegram 回复键盘；如果没有配置，使用默认布局（向后兼容）。

- **消息路由**：
  - `get_message_key()`：根据消息文本获取对应的 key（优先使用 `label_to_key` 映射，否则使用默认映射）。
  - 所有消息处理逻辑改为按 key 匹配（例如 `if message_key == 'bishu'`），同时保留对旧文案的兼容（`or message_text == '📦笔数套餐'`），确保平滑过渡。

#### 3. 后台 API（`server/api/keyboard-layout.*.ts`）

- **GET `/api/keyboard-layout`**：
  - 读取 `config.txt` 中的 `main_menu_buttons_json`，解析并返回布局数据（按行组织 + 扁平化列表）。

- **PUT `/api/keyboard-layout`**：
  - 接收前端传来的按钮布局（格式：`[[{text, action}], ...]`）。
  - 按照固定的 9 个 key 顺序，将前端布局转换为配置格式（`{key, label}`）。
  - 更新 `config.txt` 中的 `main_menu_buttons_json` 行（保留其他配置项不变）。
  - 如果按钮数量不足 9 个，使用默认 label 补齐。

#### 4. 前端同步（`pages/keyboard-buttons/index.vue`）

- **页面加载**：
  - `onMounted()` 时调用 `GET /api/keyboard-layout`，读取当前配置并更新主键盘菜单的布局显示。

- **保存键盘**：
  - `saveKeyboard()` 函数中，判断是否是主键盘菜单（`id === 1` 或 `name === '主键盘菜单'`）。
  - 如果是，调用 `PUT /api/keyboard-layout`，将布局同步到 `config.txt`。
  - 机器人会在下次 `reload_config()` 时（或重启后）自动使用新布局。

### 使用流程

1. **修改按钮文案**：
   - 在「键盘按钮」页面，点击主键盘菜单的「编辑」按钮。
   - 修改任意按钮的文案（例如将「📦 笔数套餐」改为「📦 套餐管理」）。
   - 点击「保存」。

2. **自动同步**：
   - 前端调用 `PUT /api/keyboard-layout`，将新布局写入 `config.txt`。
   - 机器人通过 `reload_config()`（或重启）读取新配置，更新 `main_menu_layout` 和 `label_to_key`。
   - 用户发送 `/start` 或点击按钮时，机器人使用新文案生成键盘。

3. **消息路由**：
   - 用户点击新文案的按钮（例如「📦 套餐管理」）。
   - 机器人通过 `get_message_key()` 查找映射表，找到对应的 key（`bishu`）。
   - 按 key 匹配路由到「笔数套餐」的处理逻辑，功能不受影响。

#### 5. 配置文件热加载（`nl-2333/config_watcher.py`）

- **永不停止的热加载机制**：
  - `monitor_config_mtime()`：每秒轮询一次 `config.txt` 的修改时间（mtime），检测到变化后自动调用 `reload_config()`。
  - `monitor_reload_flag()`：监听 `.reload_flag` 标记文件，支持手动触发重载。
  - 两个监听线程都使用 `while True` 循环，永不停止，即使出错也会在 1 秒后自动恢复。
  - 在 Docker bind mount 环境中，watchdog 事件可能不触发，mtime 轮询作为主要的热重载机制。

- **启动时初始化**：
  - `main()` 函数启动时调用 `load_main_menu_config()`，确保键盘配置在机器人启动时就被加载。
  - 配置文件监听器在 `main()` 中启动，并在整个机器人运行期间持续运行。

- **Docker 挂载**：
  - `docker-compose.yml` 中将 `config_watcher.py` 也挂载到容器中，修改后无需重新构建镜像即可生效。

### 使用流程

1. **修改按钮文案**：
   - 在「键盘按钮」页面，点击主键盘菜单的「编辑」按钮。
   - 修改任意按钮的文案（例如将「📦 笔数套餐」改为「📦 套餐管理」）。
   - 点击「保存」。

2. **自动同步与热加载**：
   - 前端调用 `PUT /api/keyboard-layout`，将新布局写入 `config.txt`。
   - 机器人的 `config_watcher` 在 1-2 秒内检测到 `config.txt` 的 mtime 变化。
   - 自动调用 `reload_config()` → `load_main_menu_config()`，更新 `main_menu_layout` 和 `label_to_key`。
   - **无需重启机器人**，配置已热重载完成。

3. **用户端刷新**：
   - 用户在 Telegram 中发送 `/start` 命令，机器人使用新文案生成键盘。
   - 用户点击新文案的按钮，机器人通过 `get_message_key()` 查找映射表，找到对应的 key（例如 `bishu`）。
   - 按 key 匹配路由到对应的处理逻辑，功能不受影响。

### 注意事项

- **key 固定**：9 个按钮的 key 不允许修改，否则会导致消息路由失效。
- **按钮数量**：必须保持 9 个按钮，如果前端布局不足 9 个，API 会自动补齐默认 label。
- **热加载永不停止**：配置文件监听器默认开启且永不关闭，即使出错也会自动恢复。
- **前端数据保护**：如果 API 调用失败或返回无效数据，前端会保留默认的 9 个按钮布局，不会显示为 0 个按钮。
- **向后兼容**：如果 `config.txt` 中没有 `main_menu_buttons_json`，机器人会使用硬编码的默认布局，确保旧版本正常运行。

## 对接能量池系统开发计划

### 已完成功能 ✅

#### 1. 能量池系统连接
- ✅ **配置管理**
  - 在 `config.txt` 中配置 `energy_pool_api` 地址
  - 支持通过 `host.docker.internal` 访问宿主机服务
  - 配置 `username` 和 `password` 用于 API 认证

- ✅ **自动创建 API 账号**
  - 实现"查询后台信息"命令（`查询后台信息`）
  - 当 `username` 或 `password` 为空时，自动调用能量池系统创建账号
  - 自动更新 `config.txt` 并重新加载配置
  - 查询并显示 API 账号余额信息

- ✅ **配置同步**
  - 将机器人配置同步到能量池系统（`/api/bots/config`）
  - 上传 `botNotifyUrl` 通知地址到能量池系统
  - 支持能量池系统查询机器人配置

#### 2. 充值功能
- ✅ **充值订单创建**
  - 用户发送充值金额，机器人创建充值订单
  - 调用能量池系统 `/api/api-recharge-orders` 接口
  - 生成充值地址并发送给用户
  - 支持 TRX 充值

- ✅ **支付状态检测**
  - 能量池系统自动检测充值地址支付状态
  - 支付成功后自动更新 API 账号余额
  - 能量池系统通知机器人充值成功

- ✅ **充值通知处理**
  - 实现 HTTP 服务器接收能量池系统通知（端口 8080）
  - 处理充值成功通知（`changeType: 'recharge'`）
  - 发送充值成功消息给用户和管理员
  - 支持编辑原消息显示支付成功状态

#### 3. 余额变动通知
- ✅ **统一通知处理**
  - 实现 `RechargeNotifyHandler` 处理所有类型的余额变动
  - 支持充值（`recharge`）、扣费（`deduct`）、调整（`adjust`）等类型
  - 根据变动类型发送不同的通知消息

- ✅ **通知服务器**
  - 启动独立的 HTTP 服务器监听端口 8080
  - 接收能量池系统发送的余额变动通知
  - 支持 JSON 格式的通知数据

#### 4. 消息处理优化
- ✅ **命令路由优化**
  - 修复"查询后台信息"命令被误拦截的问题
  - 优化消息处理逻辑，确保命令正确路由
  - 添加详细的调试日志

- ✅ **充值流程优化**
  - 修复充值金额输入被误判为地址的问题
  - 优化状态管理，确保充值流程顺畅
  - 支持充值流程中的状态检查

### 对接能量池系统技术实现

#### 配置示例（`config.txt`）
```
energy_pool_api=http://host.docker.internal:3000
username=your_api_username
password=your_api_password
bot_notify_url=http://localhost:8080/api/recharge-notify
```

#### 主要 API 调用

1. **创建 API 账号**
   ```python
   POST {energy_pool_api}/api/api-users
   Body: {"username": "auto_generated"}
   ```

2. **查询账号信息**
   ```python
   GET {energy_pool_api}/v1/get_api_user_info?username={username}
   Headers: Authorization: Basic {base64(username:password)}
   ```

3. **同步配置**
   ```python
   POST {energy_pool_api}/api/bots/config
   Body: {
     "apiUsername": username,
     "configContent": config_content,
     "botNotifyUrl": "<bot_notify_url from config.txt>"
   }
   ```

4. **创建充值订单**
   ```python
   POST {energy_pool_api}/api/api-recharge-orders
   Body: {
     "api_username": username,
     "amount_trx": amount,
     "telegram_chat_id": chat_id,
     "telegram_message_id": message_id
   }
   ```

#### 通知接收（HTTP 服务器）

机器人启动时会在端口 8080 启动 HTTP 服务器，接收能量池系统的通知（URL 以 `config.txt` 的 `bot_notify_url` 为准）：

```python
POST http://localhost:8080/api/recharge-notify
Content-Type: application/json

{
  "apiUsername": "username",
  "changeType": "recharge|deduct|adjust|other",
  "amountTrx": 10.0,
  "newBalanceTrx": 100.0,
  "orderId": "order_id",  // 仅充值类型
  "txHash": "tx_hash",    // 仅充值类型
  "telegramChatId": 123,  // 仅充值类型
  "telegramMessageId": 456 // 仅充值类型
}
```

### 重要实现说明（2026-02 更新）

- `/api/recharge-notify` 回调已改为 **先快速返回 200 accepted**，再后台线程发送 Telegram 通知，避免能量池侧 `fetch failed`。
- `docker-compose.yml` 中 `bot` 服务使用 bind mount：
  - `./nl-2333/al.py:/app/al.py:ro`
  - `./nl-2333/config.txt:/app/config.txt`
  - 所以 **本地改代码/配置后，重启容器即可生效**，无需重建镜像。

## 系统优化与功能增强（2026-02-07 更新）

### 能量购买功能修复与优化 ✅

#### 1. 能量购买流程优化
- **移除错误消息**：用户购买能量失败时不再收到"兑换失败"消息（因为用户购买能量是发送TRX，不需要兑币）
- **改进错误处理**：
  - 能量API调用支持多种响应格式（布尔值、字符串、tx_hash）
  - 安全解析JSON响应，处理非JSON响应情况
  - 区分超时错误和连接错误，提供更详细的错误信息
  - 支持多种成功标识检查（`success`、`tx_hash`、包含"成功"的字符串）

#### 2. 订单管理功能完善
- **订单保存**：
  - 成功和失败的订单都会自动保存到数据库
  - 订单号格式：`ENERGY_{timestamp}_{address_prefix}`（成功）或 `ENERGY_FAIL_{timestamp}_{address_prefix}`（失败）
  - `chat_id=0` 表示直接转账订单（匿名用户）
- **管理员通知**：
  - 购买成功时发送详细通知（订单号、金额、套餐、能量、地址、交易哈希、API余额）
  - 购买失败时发送错误通知（订单号、错误详情）
  - 使用HTML格式避免Markdown解析错误，失败时回退到纯文本
- **前端显示优化**：
  - `chat_id=0` 的订单显示为"匿名用户"和"直接转账订单"
  - 订单类型正确区分"充值余额"和"能量出租"

#### 3. 功能链7（开始/结束监听）修复 ✅
- **问题修复**：
  - 修复了"开始监听 地址"命令无法响应的问题
  - 在 `message_chain_id == 0` 分支中添加了监听命令处理逻辑
  - 支持直接输入"开始监听 地址"或"结束监听 地址"
- **功能说明**：
  - 点击按钮"🔔 开始/结束监听" → 显示格式说明
  - 直接输入"开始监听 地址" → 自动添加监听
  - 直接输入"结束监听 地址" → 自动删除监听

#### 4. 错误处理与日志改进
- **能量API错误处理**：
  - 添加超时处理（30秒超时）
  - 添加连接错误处理
  - 改进错误消息获取逻辑（从多个字段获取：`message`、`error`、`msg`）
  - 详细的错误日志记录（包含完整的result对象）
- **日志级别优化**：
  - 能量API调用结果从 `debug` 改为 `info` 级别，便于排查问题

### 技术实现细节

#### 能量购买订单保存逻辑
```python
# 成功订单保存
save_order_to_db(
    chat_id=0,  # 直接转账订单使用0作为占位符
    order_number=f"ENERGY_{int(time.time())}_{from_address[:8]}",
    energy_amount=energy,
    duration=desc,
    receiver_address=from_address,
    amount=us_amount / 1000000.0,
    payment_method='trx',
    status='completed',
    tx_hash=txid,
    remark=f"能量套餐：{desc}"
)

# 失败订单保存
save_order_to_db(
    chat_id=0,
    order_number=f"ENERGY_FAIL_{int(time.time())}_{from_address[:8]}",
    status='failed',
    remark=f"能量套餐失败：{desc}，错误：{error_msg[:50]}"
)
```

#### 能量API调用改进
- 支持多种成功标识检查
- 安全JSON解析（处理非JSON响应）
- 详细的错误分类（超时、连接错误、API错误）
- 完整的错误信息记录

#### 管理员通知格式
- 使用HTML格式（`parse_mode='HTML'`）避免Markdown解析错误
- 失败时回退到纯文本格式
- 限制错误信息长度，避免消息过长

### 使用说明

1. **能量购买**：
   - 用户在Telegram机器人中选择能量套餐
   - 发送TRX到 `control_address`
   - 系统自动匹配套餐并调用能量池API下发能量
   - 成功/失败都会保存订单并通知管理员

2. **订单查看**：
   - 在后台"订单管理"页面查看所有订单
   - 支持按时间范围筛选
   - 支持按状态筛选（全部、待付款、已完成、已取消等）
   - 匿名用户订单显示为"匿名用户"和"直接转账订单"

3. **监听地址管理**：
   - 点击"🔔 开始/结束监听"按钮查看格式说明
   - 直接输入"开始监听 地址"添加监听
   - 直接输入"结束监听 地址"删除监听

### 注意事项

- **能量API配置**：确保 `energy_pool_api` 配置正确，API服务可用
- **订单记录**：所有能量购买订单都会保存，包括成功和失败的
- **错误处理**：如果能量API调用失败，会保存失败订单并通知管理员，不会给用户发送错误消息
- **匿名订单**：直接转账订单的 `chat_id=0`，在数据库中作为占位符使用

#### Docker 配置

在 `docker-compose.yml` 中配置端口映射：

```yaml
bot:
  ports:
    - "8080:8080"  # 充值通知服务器端口
    - "8443:8443"  # Webhook 端口（如果使用）
```

### 规划中功能 🚧

#### 1. 通知重试机制
- 实现通知接收失败时的重试逻辑
- 支持本地缓存未处理的通知
- 定期重试失败的通知

#### 2. 余额监控
- 实现余额不足告警
- 支持设置余额阈值
- 自动提醒管理员充值

#### 3. 使用统计
- 记录能量消耗统计
- 生成使用报告
- 支持按时间段查询统计

#### 4. 多能量池支持
- 支持配置多个能量池系统
- 支持按需切换能量池
- 实现负载均衡

#### 5. 错误处理增强
- 完善网络错误处理
- 实现自动重连机制
- 添加详细的错误日志

#### 6. 安全性增强
- API 密钥加密存储
- 支持 API 密钥轮换
- 实现请求签名验证

### 开发注意事项

1. **网络配置**
   - 使用 `host.docker.internal` 访问宿主机服务
   - 确保 Docker 容器可以访问宿主机网络
   - 配置正确的端口映射

2. **配置同步**
   - 修改配置后需要调用能量池系统同步
   - 确保 `botNotifyUrl` 正确配置
   - 支持配置热重载

3. **错误处理**
   - 网络请求失败时要有重试机制
   - 记录详细的错误日志
   - 用户友好的错误提示

4. **测试**
   - 测试"查询后台信息"命令
   - 测试充值流程完整性
   - 测试余额变动通知接收
   - 测试配置同步功能

## 用户管理页面开发计划

### 已完成功能 ✅

#### 1. 数据库表结构
- ✅ **创建 `tg_users` 表**
  - 表结构包含 Telegram 用户的所有必要字段：
    - `tg_user_id`：Telegram 用户 ID（唯一标识）
    - `username`：Telegram 用户名（@username）
    - `first_name`、`last_name`：用户姓名
    - `phone_number`：电话号码（可选）
    - `status`：用户状态（active/banned/inactive）
    - `membership_type`：会员类型（free/vip/premium）
    - `last_activity`：最后活跃时间
    - `created_at`、`updated_at`：创建和更新时间
  - 建立索引优化查询性能：
    - `unique_tg_user_id`：唯一索引
    - `idx_status`、`idx_membership_type`：状态和会员类型索引
    - `idx_last_activity`、`idx_created_at`：时间索引

#### 2. 用户注册 API
- ✅ **修复 `/api/bot-register-user` 接口**
  - **问题**：之前只返回模拟数据，没有真正写入数据库
  - **修复**：实现真正的数据库写入逻辑
    - 检查用户是否已存在于 `tg_users` 表
    - 如果存在：更新用户信息（username、first_name、last_name、last_activity）
    - 如果不存在：创建新用户记录
    - 同时在 `transactions` 表中创建初始余额记录（amount = 0）
  - **数据格式兼容**：
    - 支持机器人发送的格式：`chat_id`、`user_nickname`、`username`
    - 支持标准格式：`chat_id`、`username`、`first_name`、`last_name`
    - 自动将 `user_nickname` 拆分为 `first_name` 和 `last_name`

#### 3. 自动用户注册
- ✅ **在 `handle_message` 中添加自动注册逻辑**
  - **问题**：用户发送私信时，如果没有发送 `/start` 命令，用户不会被注册
  - **修复**：在消息处理函数开始时添加用户检查
    - 如果是私聊消息，检查用户是否存在
    - 如果用户不存在，自动调用 `handle_start_command` 注册用户
    - 记录自动注册日志，方便调试
    - 即使注册失败也不中断消息处理流程

#### 4. 用户列表 API
- ✅ **修复 `/api/tg-users` 接口**
  - **问题**：之前从 `transactions` 表读取数据，数据不完整
  - **修复**：改为从 `tg_users` 表读取数据
    - 主查询从 `tg_users` 表获取用户信息
    - 通过 LEFT JOIN 关联 `transactions` 表获取余额信息
    - 支持搜索功能（按 tg_user_id、username、first_name、last_name）
    - 支持状态筛选（active/banned/inactive）
    - 支持分页查询
  - **统计数据**：
    - 总用户数（`total_users`）
    - 活跃用户数（`active_count`）
    - 今日新增用户数（`today_new_users`）
    - VIP 用户数（`vip_users`）

#### 5. 用户列表页面显示
- ✅ **前端页面已支持**
  - 页面路径：`/pages/users/index.vue`
  - 显示用户列表表格，包含：
    - 用户信息（头像、姓名、用户名）
    - Telegram ID（tg_user_id）
    - 用户状态（活跃/非活跃/已禁用）
    - 用户余额（从 transactions 表关联获取）
    - 最后活跃时间
    - 操作按钮（编辑、删除等）
  - 统计卡片显示：
    - 总用户数
    - 活跃用户数
    - 今日新增
    - VIP 用户数
  - 支持搜索和筛选功能

### 技术实现细节

#### 数据库表创建 SQL
```sql
CREATE TABLE IF NOT EXISTS tg_users (
  id INT NOT NULL AUTO_INCREMENT,
  tg_user_id BIGINT NOT NULL,
  username VARCHAR(255) DEFAULT NULL,
  first_name VARCHAR(255) DEFAULT NULL,
  last_name VARCHAR(255) DEFAULT NULL,
  phone_number VARCHAR(50) DEFAULT NULL,
  is_bot TINYINT(1) DEFAULT 0,
  is_premium TINYINT(1) DEFAULT 0,
  language_code VARCHAR(10) DEFAULT 'en',
  status ENUM('active', 'banned', 'inactive') DEFAULT 'active',
  membership_type ENUM('free', 'vip', 'premium') DEFAULT 'free',
  membership_expires DATETIME DEFAULT NULL,
  last_activity DATETIME DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY unique_tg_user_id (tg_user_id),
  KEY idx_status (status),
  KEY idx_membership_type (membership_type),
  KEY idx_last_activity (last_activity),
  KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Telegram用户表';
```

#### API 调用流程

1. **用户注册流程**：
   ```
   用户发送私信 → handle_message() 
   → 检查用户是否存在 
   → 如果不存在 → handle_start_command() 
   → POST /api/bot-register-user 
   → 写入 tg_users 表 
   → 写入 transactions 表（初始余额为 0）
   ```

2. **用户列表查询流程**：
   ```
   前端页面加载 → GET /api/tg-users?page=1&limit=10
   → 查询 tg_users 表（LEFT JOIN transactions）
   → 返回用户列表和统计数据
   → 前端渲染表格和统计卡片
   ```

#### 关键代码位置

- **用户注册 API**：`server/api/bot-register-user.post.ts`
- **用户列表 API**：`server/api/tg-users.get.ts`
- **机器人消息处理**：`nl-2333/al.py`（`handle_message` 和 `handle_start_command` 函数）
- **用户列表页面**：`pages/users/index.vue`

### 使用说明

#### 用户注册触发方式

1. **发送 `/start` 命令**：
   - 用户发送 `/start` 命令时，会调用 `handle_start_command` 注册用户

2. **发送任意私信**：
   - 用户发送任意消息时，`handle_message` 会自动检查并注册用户
   - 无需用户主动发送 `/start` 命令

#### 后台查看用户

1. **访问用户管理页面**：
   - 登录后台管理系统
   - 导航到「用户管理」页面
   - 切换到「Telegram 用户」标签页

2. **查看用户列表**：
   - 页面会自动加载用户列表
   - 显示所有已注册的 Telegram 用户
   - 支持搜索和筛选功能

3. **查看统计数据**：
   - 页面顶部显示统计卡片
   - 实时显示总用户数、活跃用户数、今日新增、VIP 用户数

### 规划中功能 🚧

#### 1. 用户状态管理
- 支持在后台手动修改用户状态（active/banned/inactive）
- 支持批量操作（批量禁用、批量激活）
- 实现用户状态变更日志

#### 2. 用户详情页面
- 显示用户详细信息（注册时间、最后活跃、余额变动历史）
- 显示用户的订单记录
- 显示用户的充值记录
- 支持管理员备注功能

#### 3. 用户搜索和筛选增强
- 支持按注册时间范围筛选
- 支持按余额范围筛选
- 支持按会员类型筛选
- 支持导出用户列表（CSV/Excel）

#### 4. 用户统计报表
- 用户增长趋势图表
- 活跃用户分析
- 用户地域分布（如果收集到地理位置信息）
- 用户行为分析

#### 5. 用户导入/导出功能
- 支持批量导入用户（从 CSV/Excel）
- 支持导出用户数据
- 支持用户数据备份和恢复

#### 6. 用户通知功能
- 支持向用户发送系统通知
- 支持批量通知
- 支持通知模板管理

### 开发注意事项

1. **数据一致性**
   - `tg_users` 表和 `transactions` 表需要保持数据一致
   - 注册用户时，两个表都要创建记录
   - 删除用户时，需要同时删除两个表的记录

2. **性能优化**
   - 用户列表查询使用索引优化
   - 大数据量时考虑分页和缓存
   - 统计数据可以定期更新，避免实时计算

3. **错误处理**
   - API 调用失败时要有友好的错误提示
   - 记录详细的错误日志
   - 数据库操作要有事务保护

4. **测试**
   - 测试用户注册流程（/start 命令和自动注册）
   - 测试用户列表查询和分页
   - 测试搜索和筛选功能
   - 测试统计数据准确性

---

## 快速部署说明（服务器部署）

### 系统要求
- Ubuntu 20.04 或更高版本
- 宝塔面板
- Node.js v22.19
- Python 3.9.7
- Nginx、PHP、MySQL、phpMyAdmin

### 部署步骤
1. 安装宝塔面板并安装所需环境
2. 文件权限设置为 777，用户 root
3. 从 [Releases](https://github.com/cnmbdb/hf-tgnl-admin/releases) 下载源码
4. 新建并导入数据库（使用 `nl-admin.sql`）
5. 新建 Node 项目，自定义命令：`npm run start`
6. 新建 Python 项目，自定义命令：`python3 al.py`
7. 设置自动备份

### 配置说明
- 在 `al.py` 的头几行设置 `api_key`（建议升级到 50w 一天的 key）
- `privateKey` 是出款私钥，不需要和收款同一个地址
- `hour_price`、`day_price`、`three_day_price` 分别是 1 小时、1 天和 3 天的单笔单价
- `yucun_price` 是预存单价
- `username=HFTGID` 是 API 账户
- `control_address` 是收款地址
- `CUSTOMER_SERVICE_ID` 是客服链接
- 其他配置信息在同一目录下对照修改

### 能量池对接
可接本平台能量池：**1小时1笔1.5trx**
