# TGNL Admin Docker 部署指南

## 前置要求

1. Docker 和 Docker Compose 已安装
2. 确保 `tgnl-home` 的 Next.js 服务已在宿主机运行（`localhost:3000`）
3. 确保端口 3000 未被占用（或修改 `.env` 中的 `PORT`）

## 快速启动

### 方式一：使用启动脚本（推荐）

```bash
cd /Users/a2333/tgnl-home/tgnl-admin
./start-docker.sh
```

### 方式二：手动启动

```bash
cd /Users/a2333/tgnl-home/tgnl-admin

# 1. 创建 .env 文件（如果不存在）
cp .env.example .env
# 编辑 .env 文件，修改数据库密码等配置

# 2. 检查 config.txt 配置
# 确保 energy_pool_api=http://host.docker.internal:3000

# 3. 构建并启动
docker compose build
docker compose up -d

# 4. 查看日志
docker compose logs -f
```

## 服务说明

### 服务组成

1. **app** (tgnl-admin-app)
   - Nuxt 3 管理后台
   - 端口：3000（可通过 `.env` 的 `PORT` 修改）
   - 访问路径：`http://localhost:3000/admin`

2. **db** (tgnl-admin-db)
   - MySQL 8.0 数据库
   - 端口：3306（仅内部访问）

3. **bot** (tgnl-admin-bot)
   - Telegram 机器人
   - 自动连接数据库和 Nuxt API
   - 通过 `host.docker.internal:3000` 访问宿主机上的 `tgnl-home` 能量池服务

## 配置说明

### .env 文件

```env
# 数据库配置
DB_HOST=db
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=tgnl

# 应用配置
PORT=3000
APP_BASE_PATH=/admin
APP_HOST=app

# Bot Token（可选，也可以从 config.txt 读取）
BOT_TOKEN=

# 时区
TZ=Asia/Shanghai
```

### config.txt 配置

关键配置项：
- `TOKEN`: Telegram Bot Token
- `energy_pool_api`: 能量池 API 地址（已配置为 `http://host.docker.internal:3000`）
- `username/password`: 能量池账号密码

## 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看所有日志
docker compose logs -f

# 查看单个服务日志
docker compose logs -f bot
docker compose logs -f app
docker compose logs -f db

# 重启服务
docker compose restart
docker compose restart bot

# 停止服务
docker compose down

# 停止并删除数据卷（⚠️ 会删除数据库数据）
docker compose down -v

# 重新构建
docker compose build --no-cache
docker compose up -d
```

## 故障排查

### 1. Bot 无法连接能量池 API

**问题**：机器人无法访问 `http://host.docker.internal:3000`

**解决**：
- 确保 `tgnl-home` 的 Next.js 服务在宿主机运行
- 检查 `config.txt` 中的 `energy_pool_api` 配置
- 在 Linux 系统上，`host.docker.internal` 可能需要额外配置

### 2. 数据库连接失败

**问题**：应用无法连接数据库

**解决**：
- 检查 `.env` 中的数据库配置
- 确保 `db` 容器已启动：`docker compose ps`
- 查看数据库日志：`docker compose logs db`

### 3. 端口冲突

**问题**：端口 3000 已被占用

**解决**：
- 修改 `.env` 中的 `PORT` 为其他端口（如 3001）
- 或停止占用端口的服务

### 4. Bot 启动失败

**问题**：机器人容器不断重启

**解决**：
- 查看 bot 日志：`docker compose logs bot`
- 检查 `config.txt` 中的 `TOKEN` 是否正确
- 检查 Python 依赖是否安装成功

## 数据持久化

- 数据库数据存储在 Docker volume `tgnl-admin_db_data`
- 机器人日志存储在 `./nl-2333/logs/` 目录
- `config.txt` 通过 volume 挂载，修改后需要重启 bot 容器

## 更新配置

### 更新 config.txt

```bash
# 1. 修改 config.txt
vim nl-2333/config.txt

# 2. 重启 bot 容器（支持热重载，但建议重启）
docker compose restart bot
```

### 更新代码

```bash
# 1. 修改代码后重新构建
docker compose build bot
docker compose up -d bot
```

## 网络说明

- Bot 容器通过 `host.docker.internal:3000` 访问宿主机上的 `tgnl-home` 服务
- 在 macOS/Windows 上，`host.docker.internal` 自动可用
- 在 Linux 上，已通过 `extra_hosts` 配置支持

