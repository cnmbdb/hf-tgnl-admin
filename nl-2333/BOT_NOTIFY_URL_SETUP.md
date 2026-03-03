# bot_notify_url 配置指南

## 配置说明

`bot_notify_url` 是能量池系统向机器人发送通知的地址，**必须是能量池系统可以访问的地址**。

当前能量池系统地址：`https://tgnl-home.hfz.pw`

## 配置格式

```txt
bot_notify_url=http://机器人服务器IP:8080/api/recharge-notify
```

或使用域名：

```txt
bot_notify_url=https://机器人服务器域名/api/recharge-notify
```

## 如何获取机器人服务器 IP？

### 方法 1：查看公网 IP（推荐）

在机器人服务器上执行：

```bash
curl ifconfig.me
# 或
curl ip.sb
# 或
curl icanhazip.com
```

### 方法 2：查看内网 IP

在机器人服务器上执行：

```bash
# Linux
hostname -I
# 或
ip addr show
# 或
ifconfig
```

## 配置示例

### 示例 1：使用公网 IP

假设机器人服务器公网 IP 是 `123.45.67.89`：

```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://123.45.67.89:8080/api/recharge-notify
```

### 示例 2：使用内网 IP（如果能量池系统在同一内网）

假设机器人服务器内网 IP 是 `192.168.1.100`：

```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://192.168.1.100:8080/api/recharge-notify
```

### 示例 3：使用域名（如果有）

假设机器人服务器域名是 `bot.example.com`：

```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=https://bot.example.com/api/recharge-notify
```

## 重要说明

### 1. 不能使用容器名

❌ **错误配置**：
```txt
bot_notify_url=http://tgnl-admin-bot:8080/api/recharge-notify
```

原因：容器名只在同一 Docker 网络内有效，能量池系统在另一个服务器上，无法访问容器名。

### 2. 必须使用宿主机 IP 或域名

✅ **正确配置**：
```txt
bot_notify_url=http://机器人服务器宿主机IP:8080/api/recharge-notify
```

### 3. 端口必须是 8080

机器人系统的通知服务器监听端口是 8080（在 docker-compose.yml 中配置为 `8080:8080`）。

### 4. 路径必须是 /api/recharge-notify

这是机器人系统接收通知的标准路径，不能修改。

## 配置步骤

### 步骤 1：获取服务器 IP

在机器人服务器上执行：

```bash
# 获取公网 IP（推荐）
curl ifconfig.me

# 或获取内网 IP
hostname -I
```

### 步骤 2：修改 config.txt

编辑 `nl-2333/config.txt` 文件：

```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://你的服务器IP:8080/api/recharge-notify
```

### 步骤 3：重启机器人

重启机器人后，配置会自动同步到能量池系统数据库。

## 验证配置

### 1. 检查配置是否正确

```bash
cat nl-2333/config.txt | grep -E "energy_pool_api|bot_notify_url"
```

应该看到：
```
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://你的服务器IP:8080/api/recharge-notify
```

### 2. 测试能量池系统连接

在机器人服务器上测试：

```bash
curl https://tgnl-home.hfz.pw/api/health
```

应该返回：
```json
{"status":"ok","database":"connected","timestamp":"..."}
```

### 3. 测试机器人通知地址

在能量池系统服务器上测试（替换为实际机器人 IP）：

```bash
curl -X POST http://你的机器人服务器IP:8080/api/recharge-notify \
  -H "Content-Type: application/json" \
  -d '{"apiUsername": "test", "changeType": "recharge", "amountTrx": 1, "newBalanceTrx": "1.000000"}'
```

如果返回成功，说明配置正确。

## 对于 100 个机器人系统

每个机器人服务器的 `bot_notify_url` 应该不同，指向各自的服务器地址：

- 机器人服务器 1：`bot_notify_url=http://123.45.67.89:8080/api/recharge-notify`
- 机器人服务器 2：`bot_notify_url=http://123.45.67.90:8080/api/recharge-notify`
- 机器人服务器 3：`bot_notify_url=http://123.45.67.91:8080/api/recharge-notify`
- ... 以此类推

## 常见问题

### Q1: 使用 localhost 可以吗？

**A**: 只有在以下情况可以使用 `localhost`：
- 能量池系统和机器人系统在同一台机器上
- 能量池系统在宿主机，机器人在 Docker，且使用端口映射

**不推荐**在生产环境使用 `localhost`。

### Q2: 端口必须是 8080 吗？

**A**: 是的，这是机器人系统通知服务器的标准端口。如果修改了端口，需要同时修改 `bot_notify_url` 中的端口。

### Q3: 必须使用 /api/recharge-notify 路径吗？

**A**: 是的，这是机器人系统接收通知的标准路径，不能修改。

### Q4: 配置后需要重启机器人吗？

**A**: 是的，修改 `config.txt` 后需要重启机器人，配置才会：
1. 被机器人系统读取
2. 自动同步到能量池系统数据库

## 快速配置脚本

如果需要自动获取 IP 并配置，可以使用以下脚本：

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
echo "⚠️  请重启机器人以使配置生效"
```

## 总结

**必须修改** `bot_notify_url`，将其中的 `your-bot-server-host-ip` 替换为：
- 机器人服务器的实际 IP 地址（公网或内网）
- 或机器人服务器的域名

**配置要求**：
- 必须是能量池系统可以访问的地址
- 格式：`http://ip:8080/api/recharge-notify` 或 `https://domain/api/recharge-notify`
- 对于 100 个机器人系统，每个机器人的地址都不同
