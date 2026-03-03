# 本地开发指南 - 只运行 App（Web端）

## 前提条件

1. **Node.js** 已安装（推荐 v18+）
2. **数据库**：可以选择
   - 使用 Docker 中的 db 容器（推荐，保持现有数据）
   - 或本地 MySQL

## 步骤

### 1. 停止 app 容器（如果正在运行）

```bash
cd /Users/a2333/IDE/tgnl-admin
docker compose stop app
# 或者只停止app，保留db和bot
docker compose stop app
```

### 2. 安装依赖（如果还没安装）

```bash
cd /Users/a2333/IDE/tgnl-admin
npm install
```

### 3. 配置环境变量

确保 `.env` 文件中的数据库配置正确：

**如果使用 Docker 中的 db 容器：**
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的数据库密码
DB_NAME=tgnl
```

**如果使用本地 MySQL：**
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的本地MySQL密码
DB_NAME=tgnl
```

### 4. 如果使用 Docker 中的 db，需要映射端口

如果 db 容器没有暴露端口，需要修改 `docker-compose.yml` 或临时映射：

```bash
# 检查db容器是否暴露了端口
docker compose ps db

# 如果没有，可以临时添加端口映射（修改docker-compose.yml）
# 或者在启动db时添加：-p 3306:3306
```

### 5. 启动本地开发服务器

```bash
cd /Users/a2333/IDE/tgnl-admin
npm run dev
```

或者使用静默模式（减少日志输出）：
```bash
npm run dev:silent
```

### 6. 访问应用

根据 `.env` 中的配置访问：
- 默认：`http://localhost:3000/admin`
- 或根据 `APP_BASE_PATH` 配置的路径

## 注意事项

1. **数据库连接**：
   - 如果使用 Docker 中的 db，确保端口映射正确
   - 如果使用本地 MySQL，确保 MySQL 服务已启动

2. **环境变量**：
   - 确保 `.env` 文件存在且配置正确
   - `NODE_ENV` 会自动设置为 `development`

3. **端口冲突**：
   - 确保本地 3000 端口没有被占用
   - 或修改 `.env` 中的 `PORT` 配置

4. **bot 容器**：
   - bot 容器可以继续在 Docker 中运行
   - 确保 bot 的配置能正确连接到本地运行的 app

## 停止本地开发

按 `Ctrl+C` 停止开发服务器

## 恢复 Docker 运行

如果想恢复使用 Docker 运行 app：

```bash
docker compose up -d app
```
