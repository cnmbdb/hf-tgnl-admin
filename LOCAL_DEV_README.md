# 本地开发说明

## 目录用途

- **本目录** (`/Users/a2333/IDE/tgnl-admin`): 本地开发环境，使用本地构建镜像
- **服务器部署目录** (`/Users/a2333/IDE/部署到服务器的文件/tgnl-admin`): 服务器部署，使用远程镜像

## 本地开发流程

### 1. 开发代码

在本地修改代码后：

```bash
# 重新构建镜像
docker compose build

# 重启服务
docker compose up -d
```

### 2. 推送镜像到 Docker Hub

开发完成后，推送镜像供服务器使用：

```bash
# 执行构建和推送脚本
./build-and-push.sh
```

脚本会：
- 构建多架构镜像（linux/amd64, linux/arm64）
- 推送到 `hfdoker2333/tgnl-admin:app-latest` 和 `hfdoker2333/tgnl-admin:bot-latest`

### 3. 服务器部署

服务器上使用部署目录的配置，直接拉取远程镜像：

```bash
cd /path/to/部署到服务器的文件/tgnl-admin
docker-compose pull
docker-compose up -d
```

## 配置说明

### 本地开发配置 (`docker-compose.yml`)

- 使用 `build` 指令本地构建镜像
- 镜像名称：`tgnl-admin-app:local` 和 `tgnl-admin-bot:local`
- 适合快速迭代开发

### 服务器部署配置

- 使用 `image` 指令拉取远程镜像
- 镜像名称：`hfdoker2333/tgnl-admin:app-latest` 和 `hfdoker2333/tgnl-admin:bot-latest`
- 无需构建，直接使用

## 注意事项

1. **本地开发**: 修改代码后需要重新构建镜像
2. **服务器部署**: 修改代码后需要推送镜像，服务器再拉取
3. **配置文件**: 两个目录共享相同的配置文件结构，但环境变量可能不同
