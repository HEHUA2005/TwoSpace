#!/bin/bash
# 部署脚本（在本地运行，推送到服务器）
# 用法：./deploy.sh user@your-server-ip

set -e
SERVER=$1
REMOTE_DIR=/opt/twospace

if [ -z "$SERVER" ]; then
  echo "用法: ./deploy.sh user@server-ip"
  exit 1
fi

echo ">>> 构建前端..."
cd frontend
npm run build
cd ..

echo ">>> 上传前端到服务器..."
ssh $SERVER "mkdir -p /var/www/twospace"
rsync -avz --delete frontend/dist/ $SERVER:/var/www/twospace/

echo ">>> 上传后端到服务器..."
rsync -avz --delete \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.env' \
  backend/ $SERVER:$REMOTE_DIR/backend/

echo ">>> 上传 docker-compose.yml..."
scp docker-compose.yml $SERVER:$REMOTE_DIR/

echo ">>> 重启后端服务..."
ssh $SERVER "cd $REMOTE_DIR && docker compose up -d --build"

echo ">>> 完成！"
