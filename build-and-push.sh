#!/bin/bash
DOCKER_HUB_USER="hfdoker2333"
REPO_NAME="tgnl-admin"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

docker buildx create --name tgnl-multiarch --driver docker-container --use 2>/dev/null || docker buildx use tgnl-multiarch
docker buildx inspect --bootstrap

cd "$(dirname "$0")"
docker buildx build --platform linux/amd64,linux/arm64 --tag ${DOCKER_HUB_USER}/${REPO_NAME}:app --tag ${DOCKER_HUB_USER}/${REPO_NAME}:app-latest --tag ${DOCKER_HUB_USER}/${REPO_NAME}:app-${TIMESTAMP} --tag ${DOCKER_HUB_USER}/${REPO_NAME}:latest --file Dockerfile --push .

cd nl-2333
docker buildx build --platform linux/amd64,linux/arm64 --tag ${DOCKER_HUB_USER}/${REPO_NAME}:bot --tag ${DOCKER_HUB_USER}/${REPO_NAME}:bot-latest --tag ${DOCKER_HUB_USER}/${REPO_NAME}:bot-${TIMESTAMP} --file Dockerfile --push .
