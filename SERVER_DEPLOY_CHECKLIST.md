# 服务器部署检查清单

## 部署前准备

- [ ] 确认服务器已安装 Docker 和 Docker Compose
- [ ] 确认能量池系统已在服务器上运行
- [ ] 准备上传源码到服务器

## 部署步骤

### 1. 上传源码

- [ ] 上传 `tgnl-admin` 目录到服务器
- [ ] 确认所有文件已上传（特别是 `nl-2333/config.txt`）

### 2. 配置环境

- [ ] 创建 `.env` 文件（从 `.env.example` 复制）
- [ ] 配置数据库连接信息
- [ ] 配置其他必要的环境变量

### 3. 更新机器人配置

- [ ] 编辑 `nl-2333/config.txt`
- [ ] 设置 `energy_pool_api=https://tgnl-home.hfz.pw`
- [ ] 设置 `bot_notify_url=http://localhost:8080/api/recharge-notify`（如果两个系统在同一服务器）

### 4. 构建和启动

- [ ] 执行 `docker-compose build --no-cache app bot`
- [ ] 执行 `docker-compose up -d`
- [ ] 检查容器状态：`docker-compose ps`

### 5. 验证部署

- [ ] 检查机器人日志：`docker-compose logs bot | grep "充值通知服务器"`
- [ ] 测试通知接口：`curl -X POST http://localhost:8080/api/recharge-notify ...`
- [ ] 在 Telegram 中发送"查询后台信息"同步配置
- [ ] 在能量池系统后台修改 API 余额
- [ ] 检查是否收到通知

## 配置检查

### 机器人系统配置（config.txt）

```txt
energy_pool_api=https://tgnl-home.hfz.pw
bot_notify_url=http://localhost:8080/api/recharge-notify
```

### 数据库配置检查

在能量池系统服务器上执行：
```bash
docker exec tgnl-postgres psql -U tgnl_user -d tgnl_db -c "SELECT api_username, bot_username, bot_notify_url FROM bot_configs WHERE api_username = 'api_e27ca5b3';"
```

应该看到 `bot_notify_url` 已正确配置。

## 故障排查

如果通知不工作：

1. **检查机器人日志**：
   ```bash
   docker-compose logs bot | grep -E "通知接收|充值通知服务器"
   ```

2. **检查能量池日志**：
   ```bash
   docker logs --tail 50 tgnl-home-web | grep "通知发送"
   ```

3. **测试连接**：
   ```bash
   curl -X POST http://localhost:8080/api/recharge-notify \
     -H "Content-Type: application/json" \
     -d '{"apiUsername": "test", "changeType": "adjust", "amountTrx": 1, "newBalanceTrx": "1.000000"}'
   ```

4. **检查端口映射**：
   ```bash
   docker-compose ps | grep 8080
   ```

## 完成部署

部署完成后，两个系统应该能够正常通信：
- ✅ 机器人系统可以访问能量池系统
- ✅ 能量池系统可以访问机器人通知接口
- ✅ 余额变动时，机器人管理员能收到通知
