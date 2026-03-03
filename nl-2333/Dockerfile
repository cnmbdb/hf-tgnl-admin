FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖并清理（合并减少层数，添加重试和修复机制）
RUN apt-get update --allow-releaseinfo-change || apt-get update && \
    apt-get install -y --no-install-recommends --fix-missing \
    gcc \
    libffi-dev \
    libssl-dev \
    procps \
    || (sleep 5 && apt-get update && apt-get install -y --no-install-recommends --fix-missing gcc libffi-dev libssl-dev procps) && \
    apt-get --fix-broken install -y || true && \
    rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/* \
    && apt-get clean

# 复制依赖文件
COPY requirements.txt ./

# 安装 Python 依赖并清理缓存
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge || true

# 复制机器人代码（使用 .dockerignore 排除不必要文件）
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs && \
    chmod 755 /app/logs

# 设置时区（合并减少层数）
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    rm -rf /tmp/* /var/tmp/*

# 健康检查（通过检查进程是否存在）
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f "python.*al.py" || exit 1

# 启动机器人
CMD ["python3", "al.py"]
