# ==================== Build Stage ====================
FROM node:22.19.0-alpine AS builder

WORKDIR /app

# 安装构建依赖（合并到一行减少层数）
RUN apk add --no-cache python3 make g++

# 复制 package 文件
COPY package*.json ./

# 安装依赖（使用 npm ci 确保一致性，清理缓存）
RUN npm ci --prefer-offline --no-audit && \
    npm cache clean --force

# 复制源码（使用 .dockerignore 排除不必要文件）
COPY . .

# 设置构建时环境变量
ARG APP_BASE_PATH=/admin
ARG PORT=3000
ENV APP_BASE_PATH=${APP_BASE_PATH}
ENV PORT=${PORT}
# 禁止 prebuild 阶段随机改写 .env，确保构建产物的 baseURL 固定
ENV DISABLE_RANDOM_ENV=1

# 构建生产版本并清理
RUN npm run build && \
    rm -rf node_modules/.cache && \
    rm -rf .nuxt/cache

# ==================== Production Stage ====================
FROM node:22.19.0-alpine AS production

# Install tools for healthcheck and docker CLI
RUN apk add --no-cache wget ca-certificates curl docker-cli && \
    update-ca-certificates && \
    rm -rf /var/cache/apk/*

WORKDIR /app

# 创建非 root 用户并添加到 docker 组
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nuxtjs -u 1001 && \
    addgroup -S docker && \
    addgroup nuxtjs docker

# 复制构建产物
COPY --from=builder --chown=nuxtjs:nodejs /app/.output ./.output
COPY --from=builder --chown=nuxtjs:nodejs /app/package.json ./package.json

# 复制配置文件（运行时需要）
COPY --chown=nuxtjs:nodejs nl-2333/config.txt ./nl-2333/config.txt
COPY --chown=nuxtjs:nodejs nl-2333/al.py ./nl-2333/al.py

# 清理不必要的文件
RUN rm -rf /tmp/* /var/tmp/*

USER nuxtjs

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider "http://localhost:3000${APP_BASE_PATH}/api/system/version-check" || exit 1

# 启动服务
CMD ["node", ".output/server/index.mjs"]
