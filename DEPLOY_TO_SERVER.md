# 机器人系统服务器部署指南

## 部署前提

- 能量池系统已在服务器上运行（https://tgnl-home.hfz.pw）
- 服务器已安装 Docker 和 Docker Compose
- 服务器可以访问互联网

## 部署步骤

### 步骤 1：上传源码到服务器

将整个 `tgnl-admin` 目录上传到服务器：

```bash
# 在本地执行
scp -r /Users/a2333/IDE/tgnl-admin user@server:/path/to/
```

或使用 git：
```bash
# 在服务器上
git clone <your-repo-url> tgnl-admin
cd tgnl-admin
```

### 步骤 2：配置环境变量

在服务器上创建 `.env` 文件：

```bash
cd /path/to/tgnl-admin
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息
```

### 步骤 3：更新机器人配置

编辑 `nl-2333/config.txt`：

```txt
# 能量池系统地址（服务器环境）
energy_pool_api=https://tgnl-home.hfz.pw

# 机器人通知地址（服务器环境）
# 如果两个系统在同一服务器，使用 localhost 或服务器内网 IP
bot_notify_url=http://localhost:8080/api/recharge-notify
# 或使用服务器内网 IP
# bot_notify_url=http://服务器内网IP:8080/api/recharge-notify
```

### 步骤 4：构建镜像

```bash
cd /path/to/tgnl-admin
docker-compose build --no-cache app bot
```

### 步骤 5：启动服务

```bash
docker-compose up -d
```

### 步骤 6：检查服务状态

```bash
docker-compose ps
docker-compose logs -f bot
```

### 步骤 7：同步配置到能量池系统

在 Telegram 中向机器人发送"查询后台信息"，配置会自动同步到能量池系统数据库。

## 配置说明

### 如果两个系统在同一服务器上

#### 方案 1：使用 localhost（推荐）

```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://localhost:8080/api/recharge-notify
```

#### 方案 2：使用服务器内网 IP

```bash
# 获取服务器内网 IP
hostname -I
# 或
ip addr show | grep "inet " | grep -v "127.0.0.1"
```

然后配置：
```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://服务器内网IP:8080/api/recharge-notify
```

#### 方案 3：使用 Docker 网络（如果两个系统在同一 Docker 网络）

如果两个系统在同一个 Docker 网络中，可以使用容器名：

```txt
energy_pool_api=http://tgnl-home-web:3000
bot_notify_url=http://tgnl-admin-bot:8080/api/recharge-notify
```

但需要确保两个系统在同一个 Docker 网络中。

## 验证部署

### 1. 检查容器状态

```bash
docker-compose ps
```

应该看到：
- `tgnl-admin-app`: Up (healthy)
- `tgnl-admin-bot`: Up (healthy)
- `tgnl-admin-db`: Up

### 2. 检查机器人日志

```bash
docker-compose logs bot | grep -E "充值通知服务器|监听端口|能量池API"
```

应该看到：
```
充值通知服务器已启动，监听端口 8080
能量池API（唯一桥链）已更新为: https://tgnl-home.hfz.pw
```

### 3. 测试通知功能

在能量池系统后台修改 API 余额，然后：

```bash
# 查看能量池系统日志
docker logs --tail 50 tgnl-home-web | grep "通知发送"

# 查看机器人系统日志
docker-compose logs --tail 50 bot | grep "通知接收"
```

### 4. 测试连接

在服务器上测试机器人通知地址：

```bash
curl -X POST http://localhost:8080/api/recharge-notify \
  -H "Content-Type: application/json" \
  -d '{"apiUsername": "test", "changeType": "adjust", "amountTrx": 1, "newBalanceTrx": "1.000000"}'
```

应该返回：`{"success": true, "message": "accepted"}`

## 常见问题

### 问题 1：端口冲突

如果 8080 端口被占用，可以修改 `docker-compose.yml`：

```yaml
bot:
  ports:
    - "8081:8080"  # 改为其他端口
```

然后更新 `config.txt`：
```txt
bot_notify_url=http://localhost:8081/api/recharge-notify
```

### 问题 2：数据库连接失败

检查 `.env` 文件中的数据库配置是否正确。

### 问题 3：能量池系统无法连接机器人

确保：
1. 机器人系统的 8080 端口已映射
2. `bot_notify_url` 配置正确
3. 两个系统在同一服务器上时，使用 `localhost` 或内网 IP

## 更新配置

修改配置后：

1. 修改 `nl-2333/config.txt`
2. 重启机器人容器：
   ```bash
   docker-compose restart bot
   ```
3. 在 Telegram 中发送"查询后台信息"同步配置

## 维护命令

```bash
# 查看日志
docker-compose logs -f bot

# 重启服务
docker-compose restart bot

# 停止服务
docker-compose down

# 更新代码后重新构建
docker-compose build --no-cache app bot
docker-compose up -d
```
