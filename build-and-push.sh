#!/bin/bash
DOCKER_HUB_USER="hfdoker2333"
REPO_NAME="tgnl-admin"
# 版本号（可选）：优先用传入的第一个参数，其次用 VERSION 环境变量，最后退回到日期
EXPLICIT_VERSION="${1:-${VERSION:-}}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

docker buildx create --name tgnl-multiarch --driver docker-container --use 2>/dev/null || docker buildx use tgnl-multiarch
docker buildx inspect --bootstrap

cd "$(dirname "$0")"

# 组装 app 镜像 tag 列表
APP_TAGS=(
  "${DOCKER_HUB_USER}/${REPO_NAME}:app"
  "${DOCKER_HUB_USER}/${REPO_NAME}:app-latest"
  "${DOCKER_HUB_USER}/${REPO_NAME}:app-${TIMESTAMP}"
  "${DOCKER_HUB_USER}/${REPO_NAME}:latest"
)
if [ -n "$EXPLICIT_VERSION" ]; then
  APP_TAGS+=("${DOCKER_HUB_USER}/${REPO_NAME}:app-${EXPLICIT_VERSION}")
fi

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  $(printf ' --tag %s' "${APP_TAGS[@]}") \
  --file Dockerfile \
  --push .

cd nl-2333

BOT_TAGS=(
  "${DOCKER_HUB_USER}/${REPO_NAME}:bot"
  "${DOCKER_HUB_USER}/${REPO_NAME}:bot-latest"
  "${DOCKER_HUB_USER}/${REPO_NAME}:bot-${TIMESTAMP}"
)
if [ -n "$EXPLICIT_VERSION" ]; then
  BOT_TAGS+=("${DOCKER_HUB_USER}/${REPO_NAME}:bot-${EXPLICIT_VERSION}")
fi

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  $(printf ' --tag %s' "${BOT_TAGS[@]}") \
  --file Dockerfile \
  --push .
