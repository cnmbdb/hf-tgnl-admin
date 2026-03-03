# bot_notify_url 配置说明

## 为什么需要修改？

`bot_notify_url` 是能量池系统向机器人发送通知的地址，**必须是能量池系统可以访问的地址**。

当前配置 `http://your-bot-server-ip:8080/api/recharge-notify` 只是一个模板，需要替换为实际地址。

## 如何确定自己的服务器地址？

### 方法 1：查看服务器公网 IP

```bash
# 在机器人服务器上执行
curl ifconfig.me
# 或
curl ip.sb
# 或
curl icanhazip.com
```

### 方法 2：查看服务器内网 IP

```bash
# Linux
ip addr show
# 或
ifconfig

# 查看主要网络接口的 IP
hostname -I
```

### 方法 3：使用域名（如果有）

如果机器人服务器有域名，可以使用域名：
```
bot_notify_url=https://bot.example.com/api/recharge-notify
```

## 配置方案

### 方案 1：本地开发环境（能量池和机器人在同一台机器）

如果能量池系统和机器人系统都在本地开发，可以保持：

```txt
bot_notify_url=http://localhost:8080/api/recharge-notify
```

### 方案 2：生产环境 - 使用公网 IP

如果机器人服务器有公网 IP：

```txt
# 假设机器人服务器公网 IP 是 123.45.67.89
bot_notify_url=http://123.45.67.89:8080/api/recharge-notify
```

**注意**：需要确保：
- 服务器防火墙开放 8080 端口
- 能量池系统可以访问这个 IP

### 方案 3：生产环境 - 使用内网 IP（同一内网）

如果能量池系统和机器人系统在同一内网：

```txt
# 假设机器人服务器内网 IP 是 192.168.1.100
bot_notify_url=http://192.168.1.100:8080/api/recharge-notify
```

**注意**：需要确保能量池系统可以访问这个内网 IP

### 方案 4：生产环境 - 使用域名（推荐）

如果机器人服务器有域名和 SSL 证书：

```txt
bot_notify_url=https://bot.example.com/api/recharge-notify
```

**注意**：
- 需要配置 SSL 证书
- 域名需要解析到机器人服务器 IP
- 能量池系统需要能访问这个域名

### 方案 5：Docker 容器环境

如果机器人系统运行在 Docker 容器中：

#### 情况 A：能量池系统在宿主机，机器人在容器

```txt
# 使用宿主机 IP（能量池系统在宿主机上）
bot_notify_url=http://宿主机IP:8080/api/recharge-notify
```

#### 情况 B：能量池系统和机器人都在 Docker，但不同服务器

```txt
# 使用机器人服务器的公网 IP
bot_notify_url=http://机器人服务器公网IP:8080/api/recharge-notify
```

## 配置示例

### 示例 1：机器人服务器 1

**服务器信息**：
- 公网 IP：`123.45.67.89`
- 内网 IP：`192.168.1.100`
- 域名：无

**配置**（使用公网 IP）：
```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://123.45.67.89:8080/api/recharge-notify
```

### 示例 2：机器人服务器 2

**服务器信息**：
- 公网 IP：`123.45.67.90`
- 域名：`bot2.example.com`（有 SSL 证书）

**配置**（使用域名，推荐）：
```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=https://bot2.example.com/api/recharge-notify
```

### 示例 3：机器人服务器 3（内网）

**服务器信息**：
- 内网 IP：`192.168.1.101`
- 与能量池系统在同一内网

**配置**（使用内网 IP）：
```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://192.168.1.101:8080/api/recharge-notify
```

## 验证配置

### 1. 在能量池系统服务器上测试

```bash
# 替换为实际的机器人服务器地址
curl -X POST http://your-bot-server-ip:8080/api/recharge-notify \
  -H "Content-Type: application/json" \
  -d '{"apiUsername": "test", "changeType": "recharge", "amountTrx": 1, "newBalanceTrx": "1.000000"}'
```

如果返回成功（如 `{"success": true}`），说明配置正确。

### 2. 检查机器人系统日志

机器人系统收到通知后，会在日志中显示：
```
[通知接收] 收到余额变动通知: API用户=xxx, 类型=recharge
```

## 常见问题

### Q1: 使用 localhost 可以吗？

**A**: 只有在以下情况可以使用 `localhost`：
- 能量池系统和机器人系统在同一台机器上
- 能量池系统在宿主机，机器人在 Docker，且使用端口映射

**不推荐**在生产环境使用 `localhost`。

### Q2: 使用 127.0.0.1 可以吗？

**A**: 和 `localhost` 一样，只在同一台机器上有效。

### Q3: 端口必须是 8080 吗？

**A**: 不是，可以是任何端口，只要：
- 机器人系统的 HTTP 服务监听该端口
- 配置中指定正确的端口

例如：
```txt
bot_notify_url=http://123.45.67.89:9000/api/recharge-notify
```

### Q4: 必须使用 /api/recharge-notify 路径吗？

**A**: 是的，这是机器人系统接收通知的标准路径，不能修改。

### Q5: 100 个机器人系统，每个都要配置不同的地址吗？

**A**: 是的，每个机器人服务器的 `bot_notify_url` 应该指向自己的服务器地址。

## 快速配置脚本

如果需要批量配置，可以使用以下脚本获取服务器 IP 并自动配置：

```bash
#!/bin/bash
# 自动获取服务器 IP 并配置 bot_notify_url

# 获取公网 IP
PUBLIC_IP=$(curl -s ifconfig.me)

# 获取内网 IP（主要接口）
PRIVATE_IP=$(hostname -I | awk '{print $1}')

echo "公网 IP: $PUBLIC_IP"
echo "内网 IP: $PRIVATE_IP"

# 选择使用哪个 IP（根据实际情况选择）
# 如果能量池系统在公网，使用公网 IP
# 如果能量池系统在同一内网，使用内网 IP
BOT_IP=$PUBLIC_IP  # 或 $PRIVATE_IP

# 更新配置文件
cd /path/to/tgnl-admin/nl-2333
sed -i "s|bot_notify_url=.*|bot_notify_url=http://$BOT_IP:8080/api/recharge-notify|" config.txt

echo "✅ 已更新 bot_notify_url: http://$BOT_IP:8080/api/recharge-notify"
```

## 总结

**必须修改** `bot_notify_url`，将其中的 `your-bot-server-ip` 替换为：
- 机器人服务器的实际 IP 地址（公网或内网）
- 或机器人服务器的域名

**配置要求**：
- 必须是能量池系统可以访问的地址
- 格式：`http://ip:port/api/recharge-notify` 或 `https://domain/api/recharge-notify`
- 对于 100 个机器人系统，每个机器人的地址都不同
