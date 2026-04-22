# 云服务器部署指南

本文档以 **Ubuntu 22.04 LTS** 为例。其他 Debian 系发行版步骤基本一致。

---

## 目录

1. [准备工作](#1-准备工作)
2. [安装 Docker](#2-安装-docker)
3. [安装 Nginx](#3-安装-nginx)
4. [申请 SSL 证书](#4-申请-ssl-证书)
5. [部署应用](#5-部署应用)
6. [配置 Nginx](#6-配置-nginx)
7. [验证上线](#7-验证上线)
8. [后续更新](#8-后续更新)
9. [数据备份与恢复](#9-数据备份与恢复)
10. [常见问题](#10-常见问题)

---

## 1. 准备工作

- 一台云服务器（1核 1GB 内存即可）
- 域名已将 **A 记录** 解析到服务器公网 IP（解析生效需几分钟到数小时，建议提前配置）
- 服务器开放了 80、443 端口

---

## 2. 安装 Docker

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# 重新登录后生效，验证：
docker version && docker compose version
```

---

## 3. 安装 Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable --now nginx
```

---

## 4. 申请 SSL 证书

```bash
sudo apt install -y certbot python3-certbot-nginx

# 替换为你的域名
sudo certbot --nginx -d love.example.com
# 按提示输入邮箱，同意协议；询问是否重定向 HTTP → HTTPS 时选 2
```

证书 90 天自动续期，验证：

```bash
sudo certbot renew --dry-run
```

---

## 5. 部署应用

### 5.1 服务器上创建目录

```bash
mkdir -p /opt/twospace/data/uploads
mkdir -p /opt/twospace/data/db
```

### 5.2 准备 `.env`

在本地生成所需的值：

```bash
# 密码哈希（两个用户各执行一次）
python3 -c "import bcrypt; print(bcrypt.hashpw(b'你的密码', bcrypt.gensalt()).decode())"

# JWT 密钥
openssl rand -hex 32
```

`.env` 填写示例：

```dotenv
SECRET_KEY=（openssl 生成的64位字符串）

USER1_NAME=小花
USER1_AVATAR=/uploads/avatar1.jpg
USER1_PASSWORD_HASH=$2b$12$...

USER2_NAME=小明
USER2_AVATAR=/uploads/avatar2.jpg
USER2_PASSWORD_HASH=$2b$12$...

LOVE_START_DATE=2024-01-01
COUPLE_PHOTO=/uploads/couple.jpg
QUOTES=你是我的小太阳|爱你呀|在一起的每一天都是礼物

UPLOAD_DIR=/app/uploads
DOMAIN=love.example.com
```

> `UPLOAD_DIR=/app/uploads` 是容器内路径，保持此值不变。

### 5.3 上传文件到服务器

**方式一：使用部署脚本（自动完成构建+上传+启动）**

```bash
# 先上传 .env
scp .env user@YOUR_SERVER_IP:/opt/twospace/.env

# 执行脚本
chmod +x deploy.sh
./deploy.sh user@YOUR_SERVER_IP
```

脚本依次执行：本地 `npm run build` → `rsync` 同步前端产物到 `/var/www/twospace/` → `rsync` 同步后端代码到 `/opt/twospace/backend/` → 上传 `docker-compose.yml` → 服务器端 `docker compose up -d --build`。

---

**方式二：手动逐步操作**

**① 本地构建前端**

```bash
cd frontend
npm install
npm run build
# 产物在 frontend/dist/
cd ..
```

**② 上传前端静态文件**

```bash
# 服务器上创建 web 根目录
ssh user@YOUR_SERVER_IP "sudo mkdir -p /var/www/twospace && sudo chown $USER /var/www/twospace"

# 上传
rsync -avz --delete frontend/dist/ user@YOUR_SERVER_IP:/var/www/twospace/
```

**③ 上传后端代码**

```bash
rsync -avz --delete \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.env' \
  backend/ user@YOUR_SERVER_IP:/opt/twospace/backend/
```

**④ 上传 `docker-compose.yml`**

```bash
scp docker-compose.yml user@YOUR_SERVER_IP:/opt/twospace/
```

**⑤ 上传 `.env` 和初始图片**

```bash
scp .env          user@YOUR_SERVER_IP:/opt/twospace/.env
scp couple.jpg    user@YOUR_SERVER_IP:/opt/twospace/data/uploads/
scp avatar1.jpg   user@YOUR_SERVER_IP:/opt/twospace/data/uploads/
scp avatar2.jpg   user@YOUR_SERVER_IP:/opt/twospace/data/uploads/
```

**⑥ 在服务器上启动后端容器**

```bash
ssh user@YOUR_SERVER_IP
cd /opt/twospace
docker compose up -d --build
docker ps   # 确认 twospace-backend 处于 Up 状态
```

---

## 6. 配置 Nginx

```bash
# 上传 Nginx 配置（在本地执行）
scp nginx/twospace.conf user@YOUR_SERVER_IP:/tmp/twospace.conf

# 以下在服务器上执行
sudo cp /tmp/twospace.conf /etc/nginx/sites-available/twospace
sudo sed -i 's/YOUR_DOMAIN/love.example.com/g' /etc/nginx/sites-available/twospace
sudo ln -s /etc/nginx/sites-available/twospace /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default   # 禁用默认站点

sudo nginx -t && sudo systemctl reload nginx
```

若第 4 步 Certbot 已自动写入证书路径，检查配置中是否已包含：

```nginx
ssl_certificate     /etc/letsencrypt/live/love.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/love.example.com/privkey.pem;
```

如果没有，手动补充到 `server { listen 443 ssl; ... }` 块中。

---

## 7. 验证上线

```bash
# 检查容器
docker ps
docker logs twospace-backend --tail 50

# 测试 API（返回 401 说明后端正常）
curl https://love.example.com/api/config

# 浏览器访问
https://love.example.com
```

---

## 8. 后续更新

**只更新前端：**

```bash
cd frontend && npm run build && cd ..
rsync -avz --delete frontend/dist/ user@YOUR_SERVER_IP:/var/www/twospace/
```

**只更新后端：**

```bash
rsync -avz --delete \
  --exclude '__pycache__' --exclude '*.pyc' --exclude '.env' \
  backend/ user@YOUR_SERVER_IP:/opt/twospace/backend/
ssh user@YOUR_SERVER_IP "cd /opt/twospace && docker compose up -d --build"
```

**前后端都更新（手动）：** 按顺序执行上面两段命令即可。

---

## 9. 数据备份与恢复

所有数据在服务器的 `/opt/twospace/data/`：

```
data/
├── db/twospace.db   # SQLite 数据库
└── uploads/         # 上传的图片
```

**备份：**

```bash
# 在服务器上打包
tar czf ~/twospace-backup-$(date +%Y%m%d-%H%M).tar.gz /opt/twospace/data/

# 下载到本地
scp user@YOUR_SERVER_IP:~/twospace-backup-*.tar.gz ./
```

**定时自动备份（服务器 crontab）：**

```bash
crontab -e
```

```cron
# 每天凌晨 3 点备份，保留最近 7 份
0 3 * * * tar czf ~/backups/twospace-$(date +\%Y\%m\%d).tar.gz /opt/twospace/data/ && ls -t ~/backups/twospace-*.tar.gz | tail -n +8 | xargs rm -f
```

**恢复：**

```bash
cd /opt/twospace && docker compose down
tar xzf twospace-backup-20240101.tar.gz -C /
docker compose up -d
```

---

## 10. 常见问题

**502 Bad Gateway**

后端容器未正常启动：

```bash
docker logs twospace-backend --tail 100
```

常见原因：`.env` 中必填字段为空（如 `USER1_PASSWORD_HASH`）；端口 8000 被占用（`sudo lsof -i :8000`）。

**图片无法显示**

1. 确认图片在 `/opt/twospace/data/uploads/`
2. `.env` 中 `UPLOAD_DIR=/app/uploads`（容器内路径，不要改成宿主机路径）
3. `docker-compose.yml` volume 映射：`./data/uploads:/app/uploads`

**SSL 证书申请失败**

- 确认域名已解析：`dig love.example.com`
- 确认 80 端口可访问（Certbot 通过 80 端口验证）

**修改密码**

重新生成哈希，更新 `.env` 后：

```bash
scp .env user@YOUR_SERVER_IP:/opt/twospace/.env
ssh user@YOUR_SERVER_IP "cd /opt/twospace && docker compose restart backend"
```

**查看实时日志**

```bash
docker logs -f twospace-backend
```
