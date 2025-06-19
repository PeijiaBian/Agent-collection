#!/bin/bash

# 设置变量
HARBOR_REGISTRY="harbor.emotibot.com"
PROJECT_NAME="arkagent"
IMAGE_NAME="video-analysis-backend"

# 获取 Git commit ID（取前7位）
GIT_COMMIT=$(git rev-parse --short=7 HEAD)

# 获取当前时间
CURRENT_TIME=$(date "+%Y%m%d-%H%M")

# 构建标签
TAG="${GIT_COMMIT}-${CURRENT_TIME}"
FULL_IMAGE_NAME="${HARBOR_REGISTRY}/${PROJECT_NAME}/${IMAGE_NAME}:${TAG}"

echo "Building image: ${FULL_IMAGE_NAME}"

# 构建 Docker 镜像（从父目录构建）
cd ..
docker build -t ${FULL_IMAGE_NAME} -f docker/Dockerfile .

# 推送到 Harbor
echo "Pushing image to Harbor..."
docker push ${FULL_IMAGE_NAME}

echo "Build and push completed: ${FULL_IMAGE_NAME}" 