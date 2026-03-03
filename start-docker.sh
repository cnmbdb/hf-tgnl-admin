#!/bin/bash

# TGNL Admin Docker 启动脚本

set -e

echo "🚀 开始启动 TGNL Admin Docker 服务..."

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，正在创建..."
    cat > .env << EOF
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

# 安全：端口绑定 IP（默认仅本机可访问，配合 Nginx 反代最安全）
BIND_IP=127.0.0.1

# Bot Token (可选，也可以从 config.txt 读取)
BOT_TOKEN=

# 时区
TZ=Asia/Shanghai
EOF
    echo "✅ .env 文件已创建，请根据需要修改配置"
fi

# 检查 config.txt 中的 energy_pool_api 配置
if grep -q "energy_pool_api=http://host.docker.internal:3000" nl-2333/config.txt; then
    echo "✅ 能量池 API 配置正确: http://host.docker.internal:3000"
else
    echo "⚠️  警告: config.txt 中的 energy_pool_api 可能未正确配置"
    echo "   请确保配置为: energy_pool_api=http://host.docker.internal:3000"
fi

# 构建并启动服务
echo "📦 构建 Docker 镜像..."
docker compose build

echo "🚀 启动服务..."
docker compose up -d

echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "📊 服务状态:"
docker compose ps

echo ""
echo "✅ 启动完成！"
echo ""
echo "📝 常用命令:"
echo "  查看日志: docker compose logs -f"
echo "  查看 bot 日志: docker compose logs -f bot"
echo "  查看 app 日志: docker compose logs -f app"
echo "  重启服务: docker compose restart"
echo "  停止服务: docker compose down"
echo ""
echo "🌐 访问地址:"
echo "  Nuxt 管理后台: http://localhost:${PORT:-3000}/admin"
echo "  机器人已启动，等待 Telegram 消息..."

