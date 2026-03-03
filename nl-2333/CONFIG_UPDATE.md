# 机器人系统配置文件更新说明

## 已修改的配置

### 1. energy_pool_api（能量池系统地址）

**修改前**（本地开发）：
```
energy_pool_api=http://host.docker.internal:3000
```

**修改后**（生产环境）：
```
energy_pool_api=https://tgnl-home.hfz.pw
```

**说明**：
- 已更新为生产环境的 HTTPS 域名
- 不需要加端口（HTTPS 默认 443）
- 所有机器人系统都使用相同的能量池地址

### 2. bot_notify_url（机器人通知地址）

**修改前**（本地开发）：
```
bot_notify_url=http://localhost:8080/api/recharge-notify
```

**修改后**（需要根据实际情况配置）：
```
bot_notify_url=http://your-bot-server-ip:8080/api/recharge-notify
```

**重要说明**：
- `your-bot-server-ip` 需要替换为**每个机器人服务器的实际地址**
- 这个地址必须是**能量池系统可以访问**的地址
- 对于 100 个不同服务器的机器人系统，每个机器人的 `bot_notify_url` 应该不同

## 配置示例

### 示例 1：机器人服务器 1（使用 IP）

**服务器 IP**：`123.45.67.89`

```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://123.45.67.89:8080/api/recharge-notify
```

### 示例 2：机器人服务器 2（使用域名）

**服务器域名**：`bot2.example.com`

```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=https://bot2.example.com/api/recharge-notify
```

### 示例 3：机器人服务器 3（内网 IP）

**内网 IP**：`192.168.1.100`（需要能量池系统能访问到）

```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://192.168.1.100:8080/api/recharge-notify
```

## 配置要求

### bot_notify_url 配置要求

1. **必须是能量池系统可访问的地址**
   - 如果机器人在公网：使用公网 IP 或域名
   - 如果机器人在内网：使用内网 IP（需要能量池系统能访问到）
   - 如果机器人在不同网络：需要配置端口转发或 VPN

2. **端口要求**
   - 默认端口：`8080`
   - 如果使用其他端口，需要修改为实际端口

3. **协议要求**
   - HTTP：`http://ip:8080/api/recharge-notify`
   - HTTPS：`https://domain.com/api/recharge-notify`（需要 SSL 证书）

## 批量配置脚本（100个机器人）

如果需要批量配置 100 个机器人系统，可以使用以下脚本：

```bash
#!/bin/bash
# 批量更新机器人系统配置

ENERGY_POOL_API="https://tgnl-home.hfz.pw"

# 机器人服务器列表（IP:端口，可选）
BOTS=(
  "123.45.67.89:8080"
  "123.45.67.90:8080"
  "123.45.67.91:8080"
  # ... 更多机器人
)

for bot_info in "${BOTS[@]}"; do
  IFS=':' read -r bot_ip bot_port <<< "$bot_info"
  bot_port=${bot_port:-8080}  # 默认端口 8080
  
  echo "配置机器人: $bot_ip:$bot_port"
  
  # 在每个机器人服务器上执行（需要 SSH 访问）
  ssh user@$bot_ip << EOF
    cd /path/to/tgnl-admin/nl-2333
    # 备份原配置
    cp config.txt config.txt.backup
    
    # 更新配置
    sed -i 's|energy_pool_api=.*|energy_pool_api=$ENERGY_POOL_API|' config.txt
    sed -i "s|bot_notify_url=.*|bot_notify_url=http://$bot_ip:$bot_port/api/recharge-notify|" config.txt
    
    echo "✅ 配置已更新: $bot_ip"
EOF
done
```

## 验证配置

### 1. 检查配置是否正确

```bash
# 在机器人服务器上
cat nl-2333/config.txt | grep -E "energy_pool_api|bot_notify_url"
```

应该看到：
```
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://your-actual-bot-server-ip:8080/api/recharge-notify
```

### 2. 测试能量池系统连接

```bash
# 在机器人服务器上测试
curl https://tgnl-home.hfz.pw/api/health
```

应该返回：
```json
{"status":"ok","database":"connected","timestamp":"..."}
```

### 3. 测试机器人通知地址

```bash
# 在能量池系统服务器上测试（替换为实际机器人 IP）
curl -X POST http://your-bot-server-ip:8080/api/recharge-notify \
  -H "Content-Type: application/json" \
  -d '{"apiUsername": "test", "changeType": "recharge", "amountTrx": 1, "newBalanceTrx": "1.000000"}'
```

## 注意事项

1. **每个机器人服务器都需要单独配置**
   - `energy_pool_api`：所有机器人相同（`https://tgnl-home.hfz.pw`）
   - `bot_notify_url`：每个机器人不同（指向自己的服务器地址）

2. **网络要求**
   - 机器人系统 → 能量池系统：需要能访问 `https://tgnl-home.hfz.pw`
   - 能量池系统 → 机器人系统：需要能访问每个机器人的 `bot_notify_url`

3. **防火墙配置**
   - 确保机器人服务器的 8080 端口对能量池系统开放
   - 确保能量池系统的 443 端口对所有机器人系统开放

4. **配置同步**
   - 机器人启动时会自动将配置同步到能量池系统数据库
   - 能量池系统会使用数据库中的 `bot_notify_url` 发送通知

## 当前配置状态

✅ **已更新**：
- `energy_pool_api=https://tgnl-home.hfz.pw`

⚠️ **需要修改**：
- `bot_notify_url=http://your-bot-server-ip:8080/api/recharge-notify`
  - 请将 `your-bot-server-ip` 替换为实际机器人服务器的 IP 或域名
